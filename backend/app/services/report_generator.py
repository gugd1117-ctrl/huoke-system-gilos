from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.lead import Lead, LeadCategory
from app.models.task import Task
from app.services.llm_client import LLMClient
from app.services.cost_engine import CostEngine
from collections import Counter
import json


class ReportGenerator:
    def __init__(self, db: Session, task: Task, llm: LLMClient = None, cost_engine: CostEngine = None):
        self.db = db
        self.task = task
        self.llm = llm or LLMClient()
        self.cost_engine = cost_engine

    def _get_leads(self, category: Optional[LeadCategory] = None, limit: int = 100, high_intent_only: bool = False) -> List[Lead]:
        q = self.db.query(Lead).filter(Lead.task_id == self.task.id)
        if category:
            q = q.filter(Lead.category == category)
        if high_intent_only:
            q = q.filter(Lead.is_high_intent == 1)
        return q.order_by(Lead.overall_score.desc()).limit(limit).all()

    def _top_tags(self, leads: List[Lead], k: int = 20) -> List[tuple]:
        c: Counter = Counter()
        for l in leads:
            for t in l.tags or []:
                c[t] += 1
        return c.most_common(k)

    def _platform_distribution(self, leads: List[Lead]) -> dict:
        c: Counter = Counter()
        for l in leads:
            c[l.source_platform or "unknown"] += 1
        return dict(c.most_common())

    async def generate_markdown(self) -> str:
        task = self.task
        all_leads = self._get_leads(limit=500)
        high_leads = self._get_leads(high_intent_only=True, limit=100)
        companies = self._get_leads(category=LeadCategory.COMPANY, limit=50)
        demands = self._get_leads(category=LeadCategory.DEMAND, limit=50)
        pains = self._get_leads(category=LeadCategory.PAIN_POINT, limit=50)
        opps = self._get_leads(category=LeadCategory.OPPORTUNITY, limit=50)
        trends = self._get_leads(category=LeadCategory.TREND, limit=30)
        comps = self._get_leads(category=LeadCategory.COMPETITION, limit=30)

        top_tags = self._top_tags(all_leads)
        plat_dist = self._platform_distribution(all_leads)

        lines = [
            f"# {task.query} 市场智能获客报告",
            "",
            f"> 生成时间：{task.completed_at or task.updated_at}",
            f"> 搜索模式：{task.search_mode.value}",
            f"> 平台数量：{len(task.platforms or [])}  扩展关键词：{len(task.expanded_keywords or [])}",
            "",
            "## 一、市场概况",
            "",
            f"- 发现内容总数：**{task.total_contents}**",
            f"- 识别企业/公司线索：**{task.total_companies}**",
            f"- 识别明确需求：**{task.total_demands}**",
            f"- 高意向线索（Overall ≥ 65）：**{task.total_high_intent_leads}**",
            f"- 企业/商业机会：**{task.total_company_opportunities}**",
            f"- 增长趋势：**{task.total_trends}**",
            f"- 竞争相关信号：**{task.total_competitions}**",
            "",
            "### 平台分布",
            "",
        ]
        for p, n in plat_dist.items():
            pct = n / max(1, len(all_leads)) * 100
            lines.append(f"- **{p}**: {n} 条 ({pct:.1f}%)")
        lines.append("")
        lines.append("### Top 关键词/标签")
        lines.append("")
        for t, n in top_tags:
            lines.append(f"- {t}: {n}")
        lines.append("")
        lines.append("## 二、高意向线索 Top 15")
        lines.append("")
        lines.append("| # | 类别 | 平台 | 标题/摘要 | 意向 | 机会 | 紧急 | 综合 | 公司 | URL |")
        lines.append("|---|------|------|----------|-----|-----|-----|-----|------|-----|")
        for i, l in enumerate(high_leads[:15], 1):
            title = (l.title or l.summary or "")[:60].replace("|", "/").replace("\n", " ")
            company = (l.company_name or "")[:15]
            url = l.url or ""
            link = f"[链接]({url})" if url else "-"
            lines.append(f"| {i} | {l.category.value} | {l.source_platform} | {title} | {l.intent_score} | {l.opportunity_score} | {l.urgency_score} | {l.overall_score} | {company} | {link} |")
        lines.append("")

        def section(title: str, items: List[Lead], limit: int = 10):
            out = [f"## {title}", ""]
            if not items:
                out.append("_暂无数据_")
                out.append("")
                return out
            for i, l in enumerate(items[:limit], 1):
                out.append(f"### {i}. {(l.title or l.summary or '')[:80]}")
                out.append("")
                out.append(f"- **平台**: {l.source_platform}  **类别**: {l.category.value}  **综合分**: {l.overall_score}")
                if l.company_name:
                    out.append(f"- **公司**: {l.company_name}")
                if l.location:
                    out.append(f"- **地点**: {l.location}")
                if l.language:
                    out.append(f"- **语言**: {l.language}")
                if l.tags:
                    out.append(f"- **标签**: {', '.join(l.tags[:15])}")
                if l.analysis_notes:
                    out.append(f"- **分析说明**: {l.analysis_notes}")
                if l.recommendations:
                    out.append(f"- **推荐行动**:")
                    for r in l.recommendations:
                        out.append(f"  - {r}")
                if l.url:
                    out.append(f"- **证据链接**: {l.url}")
                if l.summary and l.summary != (l.title or ""):
                    out.append("")
                    out.append(f"> {l.summary[:300]}")
                out.append("")
            return out

        lines += section("三、企业线索（潜在目标公司）", companies, 10)
        lines += section("四、明确需求信号", demands, 10)
        lines += section("五、用户痛点", pains, 10)
        lines += section("六、商业机会", opps, 10)
        lines += section("七、市场趋势", trends, 10)
        lines += section("八、竞争情报", comps, 10)

        lines.append("## 九、推荐行动")
        lines.append("")
        lines.append("1. **优先跟进 Top 10 高意向线索**：综合分最高的线索通常需求明确、机会大，建议销售/BD团队 48 小时内联系。")
        lines.append("2. **针对痛点定向营销**：从" + f" {len(pains)} " + "条痛点中提炼共性，制作针对性内容营销材料。")
        lines.append("3. **行业人才猎取**：企业线索中" + f" {sum(1 for c in companies if c.tags and any('招' in t or 'hire' in t.lower() for t in c.tags))} " + "条含招聘信号，可反向判断扩张需求。")
        lines.append("4. **竞品监控**：对竞争线索中的企业/产品建立长期跟踪机制。")
        lines.append("")

        cost_summary = CostEngine.summarize_task(self.db, self.task.id)
        lines.append("## 十、任务成本")
        lines.append("")
        lines.append(f"- 总消耗（USD）: **${cost_summary['total_usd']:.4f}**")
        lines.append(f"- 总消耗（CNY）: **¥{cost_summary['total_cny']:.2f}**")
        lines.append(f"- LLM Token 消耗: **{cost_summary['total_tokens']:,}**")
        lines.append(f"- API 调用次数: **{cost_summary['total_api_calls']:,}**")
        lines.append("")

        if self.task.expanded_keywords:
            lines.append("## 附录A. 扩展关键词")
            lines.append("")
            lines.append(", ".join(f"`{k}`" for k in (self.task.expanded_keywords or [])[:50]))
            lines.append("")

        return "\n".join(lines)
