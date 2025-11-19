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
