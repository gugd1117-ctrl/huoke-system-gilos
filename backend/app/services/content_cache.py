import hashlib
import json
import time
from cachetools import TTLCache
from typing import Any, Optional, Dict
from app.config import get_settings


class ContentCache:
    _instances: Dict[str, "ContentCache"] = {}

    def __init__(self, name: str = "default"):
        settings = get_settings()
        ttl_seconds = max(1, settings.CACHE_TTL_DAYS) * 24 * 3600
        self._cache = TTLCache(maxsize=100000, ttl=ttl_seconds)
        self._hits = 0
        self._misses = 0
        self.name = name

    @classmethod
    def get(cls, name: str = "default") -> "ContentCache":
        if name not in cls._instances:
            cls._instances[name] = ContentCache(name)
        return cls._instances[name]

    @staticmethod
    def _make_key(platform: str, method: str, **params) -> str:
        sorted_params = json.dumps(params, sort_keys=True, ensure_ascii=False)
        raw = f"{platform}|{method}|{sorted_params}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def lookup(self, platform: str, method: str, **params) -> Optional[Any]:
        key = self._make_key(platform, method, **params)
        value = self._cache.get(key)
        if value is not None:
            self._hits += 1
            return value
        self._misses += 1
        return None

    def store(self, platform: str, method: str, value: Any, **params) -> None:
        key = self._make_key(platform, method, **params)
        self._cache[key] = value

    def stats(self) -> dict:
        total = self._hits + self._misses
        hit_rate = (self._hits / total) if total else 0.0
        return {
            "name": self.name,
            "size": len(self._cache),
            "max_size": self._cache.maxsize,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 4),
        }
