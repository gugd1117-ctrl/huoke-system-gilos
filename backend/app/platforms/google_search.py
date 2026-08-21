from app.platforms.registry import PlatformRegistry
from app.platforms.base import PlatformAdapter
from app.platforms.unified_schema import UnifiedContent, ContentType
from app.models.platform_result import PlatformTier, ErrorCode
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import random
import urllib.parse


@PlatformRegistry.register
class GoogleSearchAdapter(PlatformAdapter):
    name = "google_search"
    display_name = "Google Search"
    tier = PlatformTier.TIER_1

    async def is_available(self) -> Tuple[bool, Optional[ErrorCode], Optional[str]]:
        if self.mock_mode:
            return True, None, None
        if not self.settings.GOOGLE_API_KEY or not self.settings.GOOGLE_CSE_ID:
            return False, ErrorCode.AUTH_ERROR, "Google API key or CSE ID not configured"
        return True, None, None

    def get_mock_results(self, keywords: List[str], max_items: int = 50) -> List[UnifiedContent]:
        site_templates = [
            ("company-site.com", "Co., Ltd.", "企业官网"),
            ("saas-product.io", "SaaS Inc.", "SaaS产品站"),
            ("forum-discuss.com", "", "行业论坛"),
            ("job-board.jp", "Recruit Co.", "招聘网站"),
            ("blog-marketing.com", "", "行业博客"),
            ("review-trust.com", "", "评测网站"),
            ("news-site.co.jp", "Media Corp.", "新闻媒体"),
            ("solution-provider.cn", "Tech Co.", "解决方案"),
        ]
        title_templates = [
            "{kw} 服务 - 专为日本市场设计",
            "Top 10 {kw} Tools for Japan E-commerce 2026",
            "{kw} Software Reviews & Pricing",
            "We Are Hiring: {kw} Specialist (Tokyo)",
            "Best {kw} Companies in Japan",
            "How to choose the right {kw} solution",
            "{kw} Case Study: Japan D2C Brand",
            "{kw} のおすすめサービス比較",
            "{kw} Providers Directory",
            "{kw} Market Report Japan 2026",
        ]
        snippet_templates = [
            "Our {kw} solution serves over 500+ brands across Japan. Supports PayPay integration, Japanese language UI, and 24/7 local support.",
            "Looking for reliable {kw}? Compare top vendors, read customer reviews, and find the best pricing for your cross-border business.",
            "Growing e-commerce company seeking {kw} talent. 3+ years experience, Japanese N2 required. Remote OK.",
            "We evaluated {kw} options for our Rakuten and Amazon stores. Here's what worked and what didn't after 6 months.",
            "{kw} market in Japan is expected to grow 23% YoY. Key players include local SaaS and global platform companies.",
        ]

        items: List[UnifiedContent] = []
        for i, kw in enumerate(keywords[:min(10, len(keywords))]):
            for j in range(6):
                if len(items) >= max_items:
                    break
                idx = i * 100 + j
                site, company, _ = random.choice(site_templates)
                title = random.choice(title_templates).format(kw=kw)
                snippet = random.choice(snippet_templates).format(kw=kw)
                safe_kw = urllib.parse.quote(kw)
                pub = datetime.utcnow() - timedelta(days=random.randint(0, 180))
                items.append(UnifiedContent(
                    platform="google_search",
                    content_type=ContentType.SEARCH_RESULT,
                    raw_id=f"gs_{idx}",
                    title=title,
                    content=snippet,
                    url=f"https://{site}/{safe_kw}-{idx}",
                    author_name=company or site,
                    author_url=f"https://{site}",
                    author_company=company,
                    author_location=random.choice(["Tokyo", "Osaka", "Shanghai", "Singapore", ""]),
                    published_at=pub,
                    language=random.choice(["en", "ja", "zh-CN"]),
                    tags=[kw, "search", "google"],
                    metadata={"rank": j + 1, "domain": site},
                    engagement={},
                ))
        return items

    async def search(
        self,
        keywords: List[str],
        checkpoint: Optional[Dict[str, Any]] = None,
        max_items: int = 500,
    ) -> Tuple[List[UnifiedContent], Optional[Dict[str, Any]]]:
        results = self.get_mock_results(keywords, max_items)
        return results, {"processed_keywords": len(keywords), "total_found": len(results)}
