from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from app.platforms.unified_schema import UnifiedContent
from app.models.platform_result import PlatformTier, ErrorCode
from app.config import get_settings


class PlatformAdapter(ABC):
    name: str = "base"
    display_name: str = "Base Platform"
    tier: PlatformTier = PlatformTier.TIER_1
    enabled: bool = True

    def __init__(self):
        self.settings = get_settings()
        self.mock_mode = self.settings.ENABLE_MOCK_MODE

    @abstractmethod
    async def search(
        self,
        keywords: List[str],
        checkpoint: Optional[Dict[str, Any]] = None,
        max_items: int = 500,
    ) -> Tuple[List[UnifiedContent], Optional[Dict[str, Any]]]:
        pass

    @abstractmethod
    async def is_available(self) -> Tuple[bool, Optional[ErrorCode], Optional[str]]:
        pass

    def get_mock_results(self, keywords: List[str], max_items: int = 50) -> List[UnifiedContent]:
        return []
