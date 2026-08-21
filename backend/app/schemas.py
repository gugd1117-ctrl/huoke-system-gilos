from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from app.models.task import TaskStatus, SearchMode
from app.models.lead import LeadCategory
from app.models.platform_result import PlatformStatus


class SearchModeOption(BaseModel):
    value: str
    label: str
    description: str


class PlatformInfo(BaseModel):
    name: str
    display_name: str
    tier: str
    enabled: bool


class CreateTaskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="搜索主题/关键词")
    search_mode: SearchMode = SearchMode.FAMILY_BUCKET
    platforms: Optional[List[str]] = None


class TaskBrief(BaseModel):
    id: int
    query: str
    search_mode: str
    status: TaskStatus
    progress: float
    current_step: str
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_contents: int = 0
    total_high_intent_leads: int = 0
    total_companies: int = 0
    total_demands: int = 0
    total_company_opportunities: int = 0
    total_trends: int = 0
    total_competitions: int = 0

    class Config:
        from_attributes = True


class PlatformResultBrief(BaseModel):
    id: int
    platform_name: str
    platform_tier: str
    status: PlatformStatus
    raw_items_count: int
    unified_items_count: int
    leads_extracted: int
    progress: float
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeadBrief(BaseModel):
    id: int
    category: LeadCategory
    title: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None
    tags: List[str] = []
    source_platform: Optional[str] = None
    published_at: Optional[datetime] = None
    intent_score: float = 0.0
    opportunity_score: float = 0.0
    urgency_score: float = 0.0
    overall_score: float = 0.0
    analysis_notes: Optional[str] = None
    recommendations: List[str] = []
    is_high_intent: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class TaskDetail(BaseModel):
    task: TaskBrief
    platforms: List[PlatformResultBrief]
    expanded_keywords: List[str] = []
    cost_summary: Dict[str, Any] = {}


class LeadListResponse(BaseModel):
    total: int
    high_intent_total: int
    items: List[LeadBrief]
