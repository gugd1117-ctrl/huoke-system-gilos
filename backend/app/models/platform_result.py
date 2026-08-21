import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class PlatformStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PAUSED = "paused"


class ErrorCode(str, enum.Enum):
    NO_ERROR = "no_error"
    API_ERROR = "api_error"
    RATE_LIMIT = "rate_limit"
    AUTH_ERROR = "auth_error"
    TIMEOUT = "timeout"
    NOT_SUPPORTED = "not_supported"
    DATA_CHANGED = "data_changed"


class PlatformTier(str, enum.Enum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


class PlatformResult(Base):
    __tablename__ = "platform_results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    platform_name = Column(String(100), nullable=False, index=True)
    platform_tier = Column(Enum(PlatformTier), default=PlatformTier.TIER_1)
    status = Column(Enum(PlatformStatus), default=PlatformStatus.PENDING, nullable=False)

    keywords_used = Column(JSON, default=list)
    raw_items_count = Column(Integer, default=0)
    unified_items_count = Column(Integer, default=0)
    leads_extracted = Column(Integer, default=0)

    progress = Column(Float, default=0.0)
    checkpoint = Column(JSON, nullable=True)

    error_code = Column(Enum(ErrorCode), default=ErrorCode.NO_ERROR)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    raw_data_sample = Column(JSON, default=list)
    unified_data = Column(JSON, default=list)

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    task = relationship("Task", back_populates="platform_results")
