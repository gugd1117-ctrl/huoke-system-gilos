from app.config import get_settings
from typing import List, Tuple, Optional
import json


class LLMClient:
    def __init__(self):
        self.settings = get_settings()
        self.model = self.settings.LLM_MODEL

    def _mock_chat(self, messages: List[dict], response_json: bool = False) -> str:
        sys_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")

        if "关键词" in sys_msg or "关键词" in user_msg or "keyword" in sys_msg.lower() or "keyword" in user_msg.lower():
            return json.dumps([
                "跨境电商", "日本电商市场", "日本亚马逊卖家", "乐天卖家", "日本独立站",
                "Shopify日本", "跨境物流", "日本支付", "跨境客服", "日语客服",
                "日本雅虎拍卖", "日本Mercari", "跨境ERP", "海外仓", "日本FBA",
                "D2C品牌出海", "日本社媒营销", "日本网红营销", "跨境SaaS", "日本税务"
            ], ensure_ascii=False)

        if "分析" in sys_msg or "抽取" in sys_msg or "需求" in sys_msg or "pain" in sys_msg.lower():
            return json.dumps({
                "has_buying_intent": True,
                "intent_score": 82,
                "opportunity_score": 75,
                "urgency_score": 60,
                "category": "demand",
                "summary": "卖家正在寻找日本跨境电商客服解决方案，对多语言支持和AI自动化有明确需求。",
                "pain_points": ["客服人力成本高", "日语人才短缺", "响应速度不够快"],
                "demands": ["AI客服系统", "日语自动回复", "多平台整合"],
                "recommendations": ["推荐AI客服SaaS产品", "可重点跟进日语功能模块"],
                "tags": ["跨境电商", "客服", "AI", "日本市场"],
                "why_score": "包含明确的产品搜索词和痛点描述，属于高意向需求信号。"
            }, ensure_ascii=False)

        if "报告" in sys_msg or "report" in sys_msg.lower():
            return "# 市场分析报告\n\n## 概况\n\n这是一个有潜力的市场。"

        return "Mock response for: " + user_msg[:100]

    async def chat(self, messages: List[dict], response_json: bool = False) -> Tuple[str, int]:
        if self.mock_mode or not self.settings.OPENAI_API_KEY or self.settings.OPENAI_API_KEY.startswith("your-"):
            content = self._mock_chat(messages, response_json=response_json)
            tokens = len(content) // 2
            return content, tokens

        try:
            import httpx
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(
                    f"{self.settings.OPENAI_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {self.settings.OPENAI_API_KEY}"},
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.3,
                        "response_format": {"type": "json_object"} if response_json else None,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                return content, tokens
        except Exception as e:
            content = self._mock_chat(messages, response_json=response_json)
            return content, len(content) // 2

    @property
    def mock_mode(self) -> bool:
        return self.settings.ENABLE_MOCK_MODE or not self.settings.OPENAI_API_KEY or self.settings.OPENAI_API_KEY.startswith("your-")
