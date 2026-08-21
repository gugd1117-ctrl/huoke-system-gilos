from app.platforms.registry import PlatformRegistry
from app.platforms.base import PlatformAdapter
from app.platforms.unified_schema import UnifiedContent, ContentType
from app.models.platform_result import PlatformTier, ErrorCode
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import random


@PlatformRegistry.register
class YouTubeAdapter(PlatformAdapter):
    name = "youtube"
    display_name = "YouTube"
    tier = PlatformTier.TIER_1

    async def is_available(self) -> Tuple[bool, Optional[ErrorCode], Optional[str]]:
        if self.mock_mode:
            return True, None, None
        if not self.settings.YOUTUBE_API_KEY:
            return False, ErrorCode.AUTH_ERROR, "YouTube API key not configured"
        return True, None, None

    def get_mock_results(self, keywords: List[str], max_items: int = 50) -> List[UnifiedContent]:
        channel_names = [
            "跨境电商实战派", "Japan Business Tips", "E-commerce Growth", "SaaS Review JP",
            "Shopify Masters", "Amazon FBA Japan", "マーケティング大学", "Global D2C",
        ]
        title_templates = [
            "{kw} Tutorial - Step by Step for Beginners",
            "日本での{kw}導入ガイド",
            "Top 5 {kw} Mistakes to Avoid in 2026",
            "How we 3x'd sales with {kw} (Case Study)",
            "Best {kw} Tools for Cross-Border Sellers",
            "{kw} vs Alternatives: Honest Review",
            "{kw} Setup for Shopify Stores",
            "Interview: CEO talks about {kw} Strategy",
            "{kw} 徹底解説｜メリット・デメリット",
            "Live Demo: {kw} in Action",
        ]
        desc_templates = [
            "In this video we walk through {kw} implementation for your Japan e-commerce business. Including: integration with Rakuten, PayPay, Amazon FBA.\n\n👇 Timestamps, links & resources in description.",
            "Complete guide to {kw} for Japanese market. Support my channel on Patreon!\nContact: biz@channel.com",
            "After 2 years using {kw}, here is my honest feedback, pros and cons, and who should / should NOT buy it in 2026.\n\n#ecommerce #japan #{kw.replace(' ', '')}",
        ]

        items: List[UnifiedContent] = []
        for i, kw in enumerate(keywords[:min(10, len(keywords))]):
            for j in range(5):
                if len(items) >= max_items:
                    break
                idx = i * 100 + j
                channel = random.choice(channel_names)
                title = random.choice(title_templates).format(kw=kw)
                desc = random.choice(desc_templates).format(kw=kw)
                pub = datetime.utcnow() - timedelta(days=random.randint(0, 365))
                views = random.randint(100, 500000)
                items.append(UnifiedContent(
                    platform="youtube",
                    content_type=ContentType.VIDEO,
                    raw_id=f"yt_{idx}",
                    title=title,
                    content=desc,
                    url=f"https://youtube.com/watch?v=vid{idx}",
                    author_name=channel,
                    author_url=f"https://youtube.com/@{channel}",
                    author_company="",
                    author_location=random.choice(["Tokyo", "Shanghai", "Singapore", ""]),
                    published_at=pub,
                    language=random.choice(["en", "ja", "zh-CN"]),
                    tags=[kw, "youtube", "tutorial", "review"],
                    metadata={"video_id": f"vid{idx}", "duration_sec": random.randint(120, 1800)},
                    engagement={
                        "views": views,
                        "likes": views // random.randint(20, 100),
                        "comments": random.randint(0, 500),
                        "subscribers": random.randint(500, 200000),
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
