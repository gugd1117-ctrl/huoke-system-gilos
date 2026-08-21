from typing import List
from app.services.llm_client import LLMClient
import json
import re


class KeywordExpander:
    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()

    def _basic_expand(self, query: str) -> List[str]:
        tokens = re.split(r"[\s,，、]+", query.strip())
        tokens = [t for t in tokens if t]
        results = list(dict.fromkeys(tokens + [query]))

        suffixes = ["公司", "企业", "服务", "系统", "平台", "工具", "软件", "解决方案", "招聘", "服务提供商"]
        for t in tokens:
            for s in suffixes:
                results.append(f"{t}{s}")
        return results[:30]

    async def expand(self, query: str, search_mode: str = "family_bucket") -> List[str]:
        basic = self._basic_expand(query)

        sys_prompt = """你是市场研究专家。请根据用户输入的搜索主题，生成20-30个高度相关的中英文搜索关键词，用于在多平台（社交媒体、搜索引擎、招聘网站、电商平台）检索潜在客户、企业、需求、痛点、机会。
要求：
1. 包含同义词、相关词、上下游词、场景词、职位词、行业词
2. 中英双语优先
3. 返回严格的JSON数组格式，不输出其他文本。
示例：["跨境电商", "日本亚马逊卖家", "Japan Amazon seller"]
"""

        try:
            content, tokens = await self.llm.chat([
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"用户搜索主题: {query}\n搜索模式: {search_mode}\n请生成关键词:"},
            ], response_json=True)
            try:
                llm_keywords = json.loads(content)
                if isinstance(llm_keywords, list):
                    merged = basic + [k for k in llm_keywords if isinstance(k, str)]
                    seen = set()
                    final = []
                    for k in merged:
                        if k and k not in seen:
                            seen.add(k)
                            final.append(k)
                    return final[:50]
            except Exception:
                pass
        except Exception:
            pass
        return basic
