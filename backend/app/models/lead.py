import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class LeadCategory(str, enum.Enum):
    CUSTOMER = "customer"
    COMPANY = "company"
    DEMAND = "demand"
    PAIN_POINT = "pain_point"
    OPPORTUNITY = "opportunity"
    TREND = "trend"
    COMPETITION = "competition"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    category = Column(Enum(LeadCategory), nullable=False, index=True)

    title = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(1000), nullable=True)
    author = Column(String(300), nullable=True)
    author_profile = Column(String(1000), nullable=True)
    company_name = Column(String(300), nullable=True)
    location = Column(String(200), nullable=True)
    language = Column(String(50), nullable=True)
    tags = Column(JSON, default=list)

    source_platform = Column(String(100), nullable=True)
    source_id = Column(String(300), nullable=True)
    published_at = Column(DateTime, nullable=True)

    intent_score = Column(Float, default=0.0)
    opportunity_score = Column(Float, default=0.0)
    urgency_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0, index=True)

    analysis_notes = Column(Text, nullable=True)
    recommendations = Column(JSON, default=list)
    evidence_links = Column(JSON, default=list)

    is_high_intent = Column(Integer, default=0, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    task = relationship("Task", back_populates="leads")
