from app.platforms.registry import PlatformRegistry
from app.platforms.base import PlatformAdapter
from app.platforms.unified_schema import UnifiedContent, ContentType
from app.models.platform_result import PlatformTier, ErrorCode
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import random


@PlatformRegistry.register
class RedditAdapter(PlatformAdapter):
    name = "reddit"
    display_name = "Reddit"
    tier = PlatformTier.TIER_1

    async def is_available(self) -> Tuple[bool, Optional[ErrorCode], Optional[str]]:
        if self.mock_mode:
            return True, None, None
        if not self.settings.REDDIT_CLIENT_ID or not self.settings.REDDIT_CLIENT_SECRET:
            return False, ErrorCode.AUTH_ERROR, "Reddit API credentials not configured"
        return True, None, None

    def get_mock_results(self, keywords: List[str], max_items: int = 50) -> List[UnifiedContent]:
        subreddits = ["r/ecommerce", "r/Entrepreneur", "r/smallbusiness", "r/dropshipping", "r/shopify", "r/japan"]
        templates = [
            "Any recommendations for {kw} tools in Japan market?",
            "We are struggling with {kw} for our cross-border business.",
            "Looking for {kw} service providers that support Japanese.",
            "Best {kw} software for Amazon Japan sellers?",
            "Has anyone tried {kw} with Rakuten stores?",
            "Hiring: {kw} specialist for our e-commerce team.",
            "{kw} prices keep rising - any alternatives?",
            "Feedback on {kw} platforms for D2C brands?",
        ]
        items: List[UnifiedContent] = []
        for i, kw in enumerate(keywords[:min(10, len(keywords))]):
            for j, tpl in enumerate(templates):
                if len(items) >= max_items:
                    break
                idx = i * 100 + j
                sub = random.choice(subreddits)
                title = tpl.format(kw=kw)
                pub = datetime.utcnow() - timedelta(days=random.randint(0, 60), hours=random.randint(0, 24))
                items.append(UnifiedContent(
                    platform="reddit",
                    content_type=random.choice([ContentType.POST, ContentType.COMMENT]),
                    raw_id=f"reddit_{idx}",
                    title=title,
                    content=f"{title}\n\nContext: We are a small cross-border e-commerce company looking to expand in Japan. We need {kw} solutions with good support for Japanese language and local payment methods like PayPay and credit cards. Budget is around $1000-$3000/month.",
                    url=f"https://reddit.com/{sub}/comments/{idx}",
                    author_name=f"seller_{random.randint(100,9999)}",
                    author_url=f"https://reddit.com/user/seller_{idx}",
                    author_company=random.choice(["", "E-commerce Co.", "Global Trade Ltd.", ""]),
                    author_location=random.choice(["Tokyo, Japan", "Osaka", "Shanghai, China", "California, US", ""]),
                    published_at=pub,
                    language=random.choice(["en", "en", "en", "ja"]),
                    tags=[kw, sub, "cross-border", "ecommerce"],
                    engagement={
                        "upvotes": random.randint(0, 500),
                        "comments": random.randint(0, 80),
                    },
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
