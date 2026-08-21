from typing import Dict, List, Type, Optional
from app.platforms.base import PlatformAdapter
from app.models.platform_result import PlatformTier


class PlatformRegistry:
    _platforms: Dict[str, Type[PlatformAdapter]] = {}
    _instances: Dict[str, PlatformAdapter] = {}

    @classmethod
    def register(cls, adapter_cls: Type[PlatformAdapter]) -> Type[PlatformAdapter]:
        cls._platforms[adapter_cls.name] = adapter_cls
        return adapter_cls

    @classmethod
    def get(cls, name: str) -> Optional[PlatformAdapter]:
        if name not in cls._instances and name in cls._platforms:
            cls._instances[name] = cls._platforms[name]()
        return cls._instances.get(name)

    @classmethod
    def list_all(cls) -> List[Dict[str, str]]:
        result = []
        for name, cls in cls._platforms.items():
            result.append({
                "name": name,
                "display_name": cls.display_name,
                "tier": cls.tier.value,
                "enabled": cls.enabled,
            })
        return result

    @classmethod
    def list_by_tier(cls, tier: PlatformTier) -> List[str]:
        return [name for name, cls in cls._platforms.items() if cls.tier == tier and cls.enabled]

    @classmethod
    def default_platforms(cls) -> List[str]:
        return [name for name, cls in cls._platforms.items() if cls.enabled]

    @classmethod
    def tier1(cls) -> List[str]:
        return cls.list_by_tier(PlatformTier.TIER_1)

    @classmethod
    def tier2(cls) -> List[str]:
        return cls.list_by_tier(PlatformTier.TIER_2)

    @classmethod
    def tier3(cls) -> List[str]:
        return cls.list_by_tier(PlatformTier.TIER_3)
