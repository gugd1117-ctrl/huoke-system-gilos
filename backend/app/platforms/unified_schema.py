from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    POST = "post"
    COMMENT = "comment"
    VIDEO = "video"
    ARTICLE = "article"
    REVIEW = "review"
    PROFILE = "profile"
    JOB_POSTING = "job_posting"
    PRODUCT = "product"
    SEARCH_RESULT = "search_result"


@dataclass
class UnifiedContent:
    platform: str
    content_type: ContentType
    raw_id: str
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None

    author_name: Optional[str] = None
    author_url: Optional[str] = None
    author_company: Optional[str] = None
    author_location: Optional[str] = None

    published_at: Optional[datetime] = None
    language: Optional[str] = None
    location: Optional[str] = None

    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    engagement: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "content_type": self.content_type.value,
            "raw_id": self.raw_id,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "author_name": self.author_name,
            "author_url": self.author_url,
            "author_company": self.author_company,
            "author_location": self.author_location,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "language": self.language,
            "location": self.location,
            "tags": self.tags,
            "metadata": self.metadata,
            "engagement": self.engagement,
        }
