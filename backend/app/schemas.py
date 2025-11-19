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


class GeneratedImageResponse(BaseModel):
    """Schema for generated image responses."""
    id: int
    created_at: datetime
    story_version_id: int
    prompt: str
    image_url: str
    revised_prompt: Optional[str] = None
    model: str
    size: str
    quality: str

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """Schema for public stats page."""
    total_stories: int
    total_images: int
    total_feed_items: int
    latest_story_at: Optional[datetime] = None
    latest_image_at: Optional[datetime] = None
    update_frequency_minutes: int
    feeds_count: int
    model_name: str
    uptime_hours: float
    stories_last_24h: int
    images_last_24h: int


class ControlPanelAuthRequest(BaseModel):
    """Schema for control panel authentication."""
    password: str


class ControlPanelAuthResponse(BaseModel):
    """Schema for authentication response."""
    success: bool
    message: str
    token: Optional[str] = None


class ConfigUpdateRequest(BaseModel):
    """Schema for updating configuration."""
    singl_model_name: Optional[str] = None
    singl_update_minutes: Optional[int] = None
    singl_context_steps: Optional[int] = None
    singl_temperature: Optional[float] = None
    singl_max_tokens: Optional[int] = None
    singl_image_generation_enabled: Optional[bool] = None
    singl_image_generation_interval: Optional[int] = None
    singl_image_model: Optional[str] = None
    singl_image_size: Optional[str] = None
    singl_image_quality: Optional[str] = None
    singl_feeds: Optional[str] = None


class ConfigResponse(BaseModel):
    """Schema for configuration response."""
    singl_model_name: str
    singl_update_minutes: int
    singl_context_steps: int
    singl_temperature: float
    singl_max_tokens: int
    singl_image_generation_enabled: bool
    singl_image_generation_interval: int
    singl_image_model: str
    singl_image_size: str
    singl_image_quality: str
    feed_count: int
