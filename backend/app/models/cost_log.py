import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class CostCategory(str, enum.Enum):
    PLATFORM_API = "platform_api"
    LLM_TOKEN = "llm_token"
    PROXY = "proxy"
    DATABASE = "database"
    COMPUTE = "compute"
    OTHER = "other"


class CostLog(Base):
    __tablename__ = "cost_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    platform_name = Column(String(100), nullable=True)
    category = Column(Enum(CostCategory), default=CostCategory.OTHER, nullable=False)

    amount_usd = Column(Float, default=0.0)
    amount_cny = Column(Float, default=0.0)
    tokens_used = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)

    description = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    task = relationship("Task", back_populates="cost_logs")
