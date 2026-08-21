import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class SearchMode(str, enum.Enum):
    CUSTOMERS = "customers"
    COMPANIES = "companies"
    DEMANDS = "demands"
    SUPPLIERS = "suppliers"
    PARTNERS = "partners"
    OPPORTUNITIES = "opportunities"
    FAMILY_BUCKET = "family_bucket"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(500), nullable=False, index=True)
    search_mode = Column(Enum(SearchMode), default=SearchMode.FAMILY_BUCKET, nullable=False)
    platforms = Column(JSON, default=list)
    expanded_keywords = Column(JSON, default=list)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    progress = Column(Float, default=0.0)
    current_step = Column(String(200), default="")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    error_message = Column(Text, nullable=True)

    total_contents = Column(Integer, default=0)
    total_companies = Column(Integer, default=0)
    total_communities = Column(Integer, default=0)
    total_demands = Column(Integer, default=0)
    total_high_intent_leads = Column(Integer, default=0)
    total_company_opportunities = Column(Integer, default=0)
    total_trends = Column(Integer, default=0)
    total_competitions = Column(Integer, default=0)

    platform_results = relationship("PlatformResult", back_populates="task", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="task", cascade="all, delete-orphan")
    cost_logs = relationship("CostLog", back_populates="task", cascade="all, delete-orphan")
