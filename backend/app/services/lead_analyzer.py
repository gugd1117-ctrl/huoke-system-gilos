from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import json
import re
from app.platforms.unified_schema import UnifiedContent
from app.models.lead import Lead, LeadCategory
from app.services.llm_client import LLMClient
from app.services.cost_engine import CostEngine


class LeadAnalyzer:
    def __init__(self, llm: LLMClient = None, cost_engine: CostEngine = None):
        self.llm = llm or LLMClient()
        self.cost_engine = cost_engine
        self._light_cache: Dict[str, dict] = {}

    def _route_model(self, content: UnifiedContent) -> str:
        text = f"{content.title or ''} {content.content or ''}".lower()
        length = len(text)
        has_buy = any(w in text for w in ["buy", "purchase", "looking for", "recommend", "any", "budget", "price", "招聘", "求", "推荐", "购买", "预算", "寻找", "需要"])
        has_pain = any(w in text for w in ["struggle", "problem", "issue", "bad", "sucks", "frustrat", "complaint", "坑", "难用", "投诉", "问题", "困扰", "踩坑"])
        if length < 300 and not has_buy and not has_pain:
            return "rule"
        if length < 800 or (has_buy and length < 1500):
            return "light"
        return "advanced"

    def _rule_based_analyze(self, content: UnifiedContent) -> dict:
        text = f"{content.title or ''} {content.content or ''}"
        text_lower = text.lower()
        score = 0.0
        pain_points: List[str] = []
        demands: List[str] = []
        category = LeadCategory.TREND

        intent_keywords = ["looking for", "recommend", "any recommendations", "best", "budget", "buy", "purchase",
                           "推荐", "求", "寻找", "需要", "预算", "购买", "采购", "怎么选", "避雷", "坑", "靠谱"]
        pain_keywords = ["struggle", "problem", "issue", "bad", "sucks", "complaint", "error", "failed", "bug",
                         "难用", "投诉", "问题", "困扰", "踩坑", "太贵", "慢", "不稳定", "bug"]
        job_keywords = ["hiring", "hire", "recruit", "招聘", "招", "人才", "岗位", "remote", "远程"]

        for kw in intent_keywords:
            if kw in text_lower:
                score += 8
                demands.append(kw)
        for kw in pain_keywords:
            if kw in text_lower:
                score += 6
                pain_points.append(kw)
        for kw in job_keywords:
            if kw in text_lower:
                score += 10

        if content.engagement:
            total = sum(int(v) for v in content.engagement.values() if isinstance(v, (int, float)))
            if total > 1000:
                score += 5
            if total > 10000:
                score += 5

        if job_keywords and any(kw in text_lower for kw in job_keywords):
            category = LeadCategory.COMPANY
        elif pain_points and not demands:
            category = LeadCategory.PAIN_POINT
        elif demands and score >= 15:
            category = LeadCategory.DEMAND
        elif score >= 20:
            category = LeadCategory.OPPORTUNITY

        score = min(score, 100)
        intent_score = min(len(demands) * 12 + 10, 100)
        urgency_score = min(len(pain_points) * 10 + 5, 100)
        opportunity_score = score

        tags = list(set(demands + pain_points + (content.tags or [])))[:20]
        summary = (content.title or text)[:200]

        return {
            "has_buying_intent": score >= 30 or intent_score >= 40,
            "intent_score": intent_score,
            "opportunity_score": opportunity_score,
            "urgency_score": urgency_score,
            "category": category.value,
            "summary": summary,
            "pain_points": pain_points,
            "demands": demands,
            "recommendations": ["进一步人工评估，查看原文链接"] if score >= 30 else [],
            "tags": tags,
            "why_score": f"规则命中: {len(demands)} 个需求关键词, {len(pain_points)} 个痛点关键词, 互动量参考.",
        }

    async def _llm_analyze(self, content: UnifiedContent, level: str) -> Tuple[dict, int]:
        sys_prompt = """你是商业情报分析师。请分析下面的社交媒体/搜索内容，判断是否存在购买意向、需求、痛点、商机。
输出严格JSON，包含以下字段：
{
  "has_buying_intent": boolean,
  "intent_score": 0-100（购买意向）,
  "opportunity_score": 0-100（商业机会）,
  "urgency_score": 0-100（紧迫度）,
  "category": "customer" | "company" | "demand" | "pain_point" | "opportunity" | "trend" | "competition",
  "summary": "中文摘要（200字内）",
  "pain_points": ["痛点1", "痛点2"],
  "demands": ["需求1", "需求2"],
  "recommendations": ["推荐行动1", "推荐行动2"],
  "tags": ["标签1", "标签2"],
  "why_score": "分数解释（中文）"
}"""
        content_text = (
            f"平台: {content.platform}\n"
            f"类型: {content.content_type.value}\n"
            f"标题: {content.title or ''}\n"
            f"正文: {content.content or ''}\n"
            f"作者: {content.author_name or ''} (公司: {content.author_company or ''}, 地点: {content.author_location or ''})\n"
            f"语言: {content.language or ''}\n"
            f"发布时间: {content.published_at}\n"
            f"互动: {json.dumps(content.engagement, ensure_ascii=False)}\n"
            f"URL: {content.url or ''}"
        )
        model_level_map = {"light": "light", "advanced": "advanced"}
        resp, tokens = await self.llm.chat([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": content_text},
        ], response_json=True)
        try:
            parsed = json.loads(resp)
        except Exception:
            parsed = self._rule_based_analyze(content)
        if self.cost_engine:
            self.cost_engine.log_llm(tokens=tokens, platform=content.platform, model_level=model_level_map.get(level, "advanced"))
        return parsed, tokens

    async def analyze_content(self, content: UnifiedContent) -> dict:
        cache_key = f"{content.platform}|{content.raw_id}"
        if cache_key in self._light_cache:
            return self._light_cache[cache_key]
        level = self._route_model(content)
        if level == "rule":
            result = self._rule_based_analyze(content)
        else:
            result, _ = await self._llm_analyze(content, level)
        self._light_cache[cache_key] = result
        return result

    @staticmethod
    def lead_category_from_str(v: str) -> LeadCategory:
        mapping = {
            "customer": LeadCategory.CUSTOMER,
            "company": LeadCategory.COMPANY,
            "demand": LeadCategory.DEMAND,
            "pain_point": LeadCategory.PAIN_POINT,
            "opportunity": LeadCategory.OPPORTUNITY,
            "trend": LeadCategory.TREND,
            "competition": LeadCategory.COMPETITION,
        }
        return mapping.get(v, LeadCategory.TREND)

    def content_to_lead(self, task_id: int, content: UnifiedContent, analysis: dict) -> Lead:
        intent = float(analysis.get("intent_score", 0) or 0)
        opp = float(analysis.get("opportunity_score", 0) or 0)
        urg = float(analysis.get("urgency_score", 0) or 0)
        overall = round(intent * 0.45 + opp * 0.35 + urg * 0.20, 2)
        is_high = 1 if (intent >= 70 or overall >= 65) else 0
        cat_str = analysis.get("category") or "trend"
        category = self.lead_category_from_str(cat_str)

        company = content.author_company or ""
        if not company and (category == LeadCategory.COMPANY or "招聘" in (content.title or "") or "hiring" in (content.title or "").lower()):
            company = content.author_name or ""

        return Lead(
            task_id=task_id,
            category=category,
            title=content.title or analysis.get("summary", "")[:200],
            summary=analysis.get("summary", "") or (content.content or "")[:300],
            content=content.content,
            url=content.url,
            author=content.author_name,
            author_profile=content.author_url,
            company_name=company,
            location=content.author_location or content.location,
            language=content.language,
            tags=list(set((content.tags or []) + list(analysis.get("tags") or [])))[:30],
            source_platform=content.platform,
            source_id=content.raw_id,
            published_at=content.published_at,
            intent_score=round(intent, 2),
            opportunity_score=round(opp, 2),
            urgency_score=round(urg, 2),
            overall_score=overall,
            analysis_notes=analysis.get("why_score", ""),
            recommendations=list(analysis.get("recommendations") or []),
            evidence_links=[content.url] if content.url else [],
            is_high_intent=is_high,
        )
