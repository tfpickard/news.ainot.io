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


class LoginRequest(BaseModel):
    """Schema for login request."""
    password: str


class LoginResponse(BaseModel):
    """Schema for login response."""
    api_key: str
    message: str
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


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings."""
    theme: Optional[str] = None  # "light", "dark", or "auto"


class UserSettingsResponse(BaseModel):
    """Schema for user settings response."""
    theme: str  # "light", "dark", or "auto"


class SentimentScore(BaseModel):
    """Schema for sentiment scores."""
    positive: float
    negative: float
    neutral: float


class BiasScore(BaseModel):
    """Schema for bias metrics."""
    political_lean: str  # "left", "center", "right", "unknown"
    lean_score: float  # -1.0 (left) to 1.0 (right)
    loaded_language_count: int
    emotional_language_score: float


class SourceAnalysis(BaseModel):
    """Schema for per-source analysis."""
    source_name: str
    sentiment: SentimentScore
    bias: BiasScore
    article_count: int


class FactCheck(BaseModel):
    """Schema for fact check results."""
    claim: str
    verdict: str  # "true", "false", "partially-true", "unverified", "misleading"
    confidence: float  # 0.0 to 1.0
    explanation: str
    sources: List[str] = []  # Default to empty list if not provided


class EventData(BaseModel):
    """Schema for extracted events."""
    title: str
    description: str
    timestamp: Optional[str] = None
    category: str  # "political", "economic", "social", "conflict", "disaster", etc.
    importance: int  # 1-10 scale


class Prediction(BaseModel):
    """Schema for forecasting predictions."""
    scenario: str
    probability: float  # 0.0 to 1.0
    timeframe: str  # "short-term", "medium-term", "long-term"
    reasoning: str
    related_events: List[str]


class StoryAnalyticsResponse(BaseModel):
    """Schema for story analytics response."""
    story_version_id: int
    created_at: datetime
    overall_sentiment: Optional[str] = None
    sentiment_score: Optional[SentimentScore] = None
    bias_score: Optional[BiasScore] = None
    bias_indicators: Optional[Dict[str, Any]] = None
    source_analysis: Optional[List[SourceAnalysis]] = None
    fact_checks: Optional[List[FactCheck]] = None
    predictions: Optional[List[Prediction]] = None
    events: Optional[List[EventData]] = None

    class Config:
        from_attributes = True
