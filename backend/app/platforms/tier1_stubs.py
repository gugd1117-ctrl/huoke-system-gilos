from app.platforms.registry import PlatformRegistry
from app.platforms.base import PlatformAdapter
from app.platforms.unified_schema import UnifiedContent, ContentType
from app.models.platform_result import PlatformTier, ErrorCode
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import random


def _generate_mock_content(platform: str, display: str, keywords: List[str], content_types, max_items: int = 40) -> List[UnifiedContent]:
    templates_post = [
        "{kw}真的太香了！用了一个月业绩翻倍",
        "有没有靠谱的{kw}推荐？预算5w以内",
        "做跨境这么久，终于找到合适的{kw}了",
        "避雷！某{kw}真的不好用，大家别踩坑",
        "创业日记：Day1 搭建{kw}体系",
        "日本市场{kw}调研报告分享（干货）",
        "招{kw}运营｜东京可远程｜待遇优",
        "大家做{kw}一个月ROI能做到多少？求交流",
    ]
    templates_en = [
        "Just launched my {kw} journey in Japan! Any tips?",
        "Best {kw} tools for cross-border sellers 2026, anyone?",
        "We are hiring {kw} specialist in Tokyo area.",
        "Struggling with {kw} for my Shopify store - advice welcome!",
    ]
    items: List[UnifiedContent] = []
    for i, kw in enumerate(keywords[:min(8, len(keywords))]):
        for j in range(5):
            if len(items) >= max_items:
                break
            idx = i * 100 + j
            is_en = random.random() < 0.25
            tpl = random.choice(templates_en if is_en else templates_post)
            title = tpl.format(kw=kw)
            pub = datetime.utcnow() - timedelta(days=random.randint(0, 90), hours=random.randint(0, 24))
            lang = "en" if is_en else random.choice(["zh-CN", "ja"])
            items.append(UnifiedContent(
                platform=platform,
                content_type=random.choice(content_types),
                raw_id=f"{platform}_{idx}",
                title=title[:100],
                content=f"{title}\n\n补充说明：我们做日本跨境电商三年，一直被{kw}问题困扰，试过很多方法都不理想。希望有经验的朋友推荐一下，可以加我vx交流。",
                url=f"https://{platform}.com/p/{idx}",
                author_name=f"{display}用户{random.randint(10000,99999)}",
                author_url=f"https://{platform}.com/u/{idx}",
                author_company=random.choice(["", "某跨境公司", "SaaS提供商", ""]),
                author_location=random.choice(["东京", "上海", "深圳", "大阪", ""]),
                published_at=pub,
                language=lang,
                tags=[kw, platform, random.choice(["跨境电商", "创业", "日本市场", "SaaS", "招聘"])],
                metadata={},
                engagement={
                    "likes": random.randint(0, 20000),
                    "comments": random.randint(0, 2000),
                    "shares": random.randint(0, 500),
                    "views": random.randint(0, 500000),
                },
            ))
    return items


@PlatformRegistry.register
class DouyinAdapter(PlatformAdapter):
    name = "douyin"
    display_name = "抖音"
    tier = PlatformTier.TIER_1

    async def is_available(self):
        if self.mock_mode:
            return True, None, None
        return False, ErrorCode.NOT_SUPPORTED, "Douyin API requires enterprise access"

    async def search(self, keywords, checkpoint=None, max_items=500):
        results = _generate_mock_content("douyin", "抖音", keywords, [ContentType.VIDEO, ContentType.POST], max_items)
        return results, {"processed_keywords": len(keywords), "total_found": len(results)}


@PlatformRegistry.register
class XiaohongshuAdapter(PlatformAdapter):
    name = "xiaohongshu"
    display_name = "小红书"
    tier = PlatformTier.TIER_1

    async def is_available(self):
        if self.mock_mode:
            return True, None, None
        return False, ErrorCode.NOT_SUPPORTED, "Xiaohongshu API not public"

    async def search(self, keywords, checkpoint=None, max_items=500):
        results = _generate_mock_content("xiaohongshu", "小红书", keywords, [ContentType.POST, ContentType.ARTICLE], max_items)
        return results, {"processed_keywords": len(keywords), "total_found": len(results)}


@PlatformRegistry.register
class BilibiliAdapter(PlatformAdapter):
    name = "bilibili"
    display_name = "B站"
    tier = PlatformTier.TIER_1

    async def is_available(self):
        if self.mock_mode:
            return True, None, None
        return False, ErrorCode.NOT_SUPPORTED, "Bilibili API access pending"

    async def search(self, keywords, checkpoint=None, max_items=500):
        results = _generate_mock_content("bilibili", "B站", keywords, [ContentType.VIDEO, ContentType.ARTICLE], max_items)
        return results, {"processed_keywords": len(keywords), "total_found": len(results)}


@PlatformRegistry.register
class TikTokAdapter(PlatformAdapter):
    name = "tiktok"
    display_name = "TikTok"
    tier = PlatformTier.TIER_1

    async def is_available(self):
        if self.mock_mode:
            return True, None, None
        return False, ErrorCode.AUTH_ERROR, "TikTok API key not configured"

    async def search(self, keywords, checkpoint=None, max_items=500):
        results = _generate_mock_content("tiktok", "TikTok", keywords, [ContentType.VIDEO], max_items)
        return results, {"processed_keywords": len(keywords), "total_found": len(results)}


@PlatformRegistry.register
class InstagramAdapter(PlatformAdapter):
    name = "instagram"
    display_name = "Instagram"
    tier = PlatformTier.TIER_1

    async def is_available(self):
        if self.mock_mode:
            return True, None, None
        return False, ErrorCode.AUTH_ERROR, "Instagram Graph API not configured"

    async def search(self, keywords, checkpoint=None, max_items=500):
        results = _generate_mock_content("instagram", "IG", keywords, [ContentType.POST], max_items)
        return results, {"processed_keywords": len(keywords), "total_found": len(results)}


@PlatformRegistry.register
class XAdapter(PlatformAdapter):
    name = "x"
    display_name = "X (Twitter)"
    tier = PlatformTier.TIER_1

    async def is_available(self):
        if self.mock_mode:
            return True, None, None
        return False, ErrorCode.AUTH_ERROR, "X API bearer token not configured"

    async def search(self, keywords, checkpoint=None, max_items=500):
        results = _generate_mock_content("x", "X", keywords, [ContentType.POST, ContentType.COMMENT], max_items)
        return results, {"processed_keywords": len(keywords), "total_found": len(results)}
