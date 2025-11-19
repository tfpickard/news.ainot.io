"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class StoryVersionBase(BaseModel):
    """Base schema for story version."""
    full_text: str
    summary: str
    context_summary: Optional[str] = None
    sources_snapshot: Optional[Dict[str, Any]] = None
    token_stats: Optional[Dict[str, Any]] = None


class StoryVersionCreate(StoryVersionBase):
    """Schema for creating a story version."""
    pass


class StoryVersionResponse(StoryVersionBase):
    """Schema for story version responses."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StoryVersionSummary(BaseModel):
    """Condensed story version for history lists."""
    id: int
    created_at: datetime
    summary: str
    preview: str  # First ~200 chars of full_text

    class Config:
        from_attributes = True


class FeedItemBase(BaseModel):
    """Base schema for feed item."""
    feed_url: str
    feed_name: str
    title: str
    summary: Optional[str] = None
    link: str
    published_at: Optional[datetime] = None
    content_hash: str
    raw: Optional[Dict[str, Any]] = None


class FeedItemCreate(FeedItemBase):
    """Schema for creating a feed item."""
    pass


class FeedItemResponse(FeedItemBase):
    """Schema for feed item responses."""
    id: int
    fetched_at: datetime

    class Config:
        from_attributes = True


class MetaResponse(BaseModel):
    """Schema for meta information about the service."""
    feed_urls: List[str]
    feed_count: int
    update_minutes: int
    context_steps: int
    last_update: Optional[datetime] = None
    story_count: int
    model_name: str


class HealthResponse(BaseModel):
    """Schema for health check."""
    status: str
    database_connected: bool
    last_story_at: Optional[datetime] = None
    story_count: int


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""
    type: str  # "initial" or "update"
    story: StoryVersionResponse


class QuoteResponse(BaseModel):
    """Schema for extracted quotes."""
    text: str
    category: str
    absurdity_score: int
    keywords: List[str]


class QuotesResponse(BaseModel):
    """Schema for multiple quotes from a story."""
    story_id: int
    quotes: List[QuoteResponse]


class SourceDetail(BaseModel):
    """Schema for detailed source information."""
    id: int
    title: str
    source: str
    published_at: Optional[str] = None
    link: Optional[str] = None


class SourcesResponse(BaseModel):
    """Schema for story sources."""
    story_id: int
    item_count: int
    sources: List[SourceDetail]


class SEOMetadata(BaseModel):
    """Schema for SEO metadata."""
    title: str
    description: str
    keywords: List[str]
    og_title: str
    og_description: str
    og_type: str = "article"
    twitter_card: str = "summary_large_image"


class APIDocumentation(BaseModel):
    """Schema for API documentation."""
    version: str
    endpoints: List[Dict[str, Any]]
    examples: List[Dict[str, Any]]
    rate_limits: Dict[str, Any]


class FeedConfigurationBase(BaseModel):
    """Base schema for feed configuration."""
    name: str
    url: str
    category: Optional[str] = None
    is_active: bool = True
    priority: int = 0


class FeedConfigurationCreate(FeedConfigurationBase):
    """Schema for creating a feed configuration."""
    pass


class FeedConfigurationUpdate(BaseModel):
    """Schema for updating a feed configuration."""
    name: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class FeedConfigurationResponse(FeedConfigurationBase):
    """Schema for feed configuration responses."""
    id: int
    created_at: datetime
    last_fetched: Optional[datetime] = None
    fetch_error: Optional[str] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Schema for login request."""
    password: str


class LoginResponse(BaseModel):
    """Schema for login response."""
    api_key: str
    message: str
