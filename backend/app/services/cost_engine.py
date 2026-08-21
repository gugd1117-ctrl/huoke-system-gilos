from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.cost_log import CostLog, CostCategory
from app.database import SessionLocal
from typing import Optional
import threading


_TOKENS_PER_USD = 1_000_000 / 2.50
_USD_TO_CNY = 7.25


class CostEngine:
    _thread_local = threading.local()

    def __init__(self, task_id: int):
        self.task_id = task_id

    def _log(self, category: CostCategory, platform: Optional[str] = None,
             tokens: int = 0, api_calls: int = 0, usd: float = 0.0,
             description: Optional[str] = None):
        cny = usd * _USD_TO_CNY
        db = SessionLocal()
        try:
            log = CostLog(
                task_id=self.task_id,
                platform_name=platform,
                category=category,
                amount_usd=round(usd, 6),
                amount_cny=round(cny, 4),
                tokens_used=tokens,
                api_calls=api_calls,
                description=description,
            )
            db.add(log)
            db.commit()
        finally:
            db.close()

    def log_llm(self, tokens: int, platform: Optional[str] = None,
                description: Optional[str] = None, model_level: str = "advanced"):
        price_per_m = {"rule": 0.0, "light": 0.15, "advanced": 2.50, "vision": 10.0}.get(model_level, 2.50)
        usd = (tokens / 1_000_000) * price_per_m
        self._log(CostCategory.LLM_TOKEN, platform=platform, tokens=tokens, usd=usd, description=description or f"LLM ({model_level})")

    def log_platform_api(self, platform: str, api_calls: int = 1, usd_per_call: float = 0.001,
                         description: Optional[str] = None):
        usd = api_calls * usd_per_call
        self._log(CostCategory.PLATFORM_API, platform=platform, api_calls=api_calls, usd=usd,
                  description=description or f"{platform} API call")

    def log_proxy(self, platform: Optional[str] = None, usd: float = 0.0, description: Optional[str] = None):
        self._log(CostCategory.PROXY, platform=platform, usd=usd, description=description or "Proxy usage")

    @classmethod
    def summarize_task(cls, db: Session, task_id: int) -> dict:
        rows = db.query(CostLog).filter(CostLog.task_id == task_id).all()
        total_usd = sum(r.amount_usd for r in rows)
        total_cny = sum(r.amount_cny for r in rows)
        total_tokens = sum(r.tokens_used for r in rows)
        total_calls = sum(r.api_calls for r in rows)
        by_category = {}
        for r in rows:
            key = r.category.value
            if key not in by_category:
                by_category[key] = {"usd": 0.0, "cny": 0.0, "tokens": 0, "calls": 0, "count": 0}
            by_category[key]["usd"] += r.amount_usd
            by_category[key]["cny"] += r.amount_cny
            by_category[key]["tokens"] += r.tokens_used
            by_category[key]["calls"] += r.api_calls
            by_category[key]["count"] += 1
        return {
            "total_usd": round(total_usd, 6),
            "total_cny": round(total_cny, 4),
            "total_tokens": total_tokens,
            "total_api_calls": total_calls,
            "by_category": by_category,
            "logs_count": len(rows),
        }
