"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base


class StoryVersion(Base):
    """Represents a version of the single, evolving story."""

    __tablename__ = "story_versions"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    full_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    context_summary = Column(Text)  # Compressed narrative context for future generations
    sources_snapshot = Column(JSON)  # Which feeds/items influenced this version
    token_stats = Column(JSON)  # OpenAI usage statistics

    def __repr__(self):
        return f"<StoryVersion(id={self.id}, created_at={self.created_at})>"


class FeedItem(Base):
    """Represents an individual item from an RSS feed."""

    __tablename__ = "feed_items"

    id = Column(Integer, primary_key=True, index=True)
    feed_url = Column(String, nullable=False, index=True)
    feed_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text)
    link = Column(String, nullable=False)
    published_at = Column(DateTime(timezone=True), index=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    content_hash = Column(String, nullable=False, unique=True)  # For deduplication
    raw = Column(JSON)  # Raw feed item data

    __table_args__ = (
        UniqueConstraint('link', 'title', name='uix_link_title'),
    )

    def __repr__(self):
        return f"<FeedItem(id={self.id}, title='{self.title[:50]}...')>"


class FeedConfiguration(Base):
    """Configurable RSS feed sources."""

    __tablename__ = "feed_configurations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Human-readable name
    url = Column(String, nullable=False, unique=True, index=True)
    category = Column(String)  # e.g., "tech", "politics", "sports"
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_fetched = Column(DateTime(timezone=True))
    fetch_error = Column(Text)  # Store last error if any
    priority = Column(Integer, default=0)  # Higher priority feeds checked first

    def __repr__(self):
        return f"<FeedConfiguration(id={self.id}, name='{self.name}', active={self.is_active})>"
class GeneratedImage(Base):
    """Represents an AI-generated image inspired by the news story."""

    __tablename__ = "generated_images"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    story_version_id = Column(Integer, nullable=False, index=True)  # Associated story version
    prompt = Column(Text, nullable=False)  # The prompt used to generate the image
    image_url = Column(String, nullable=False)  # OpenAI image URL
    revised_prompt = Column(Text)  # OpenAI's revised prompt (if available)
    model = Column(String, nullable=False)  # Model used (e.g., dall-e-3)
    size = Column(String, nullable=False)  # Image size (e.g., 1024x1024)
    quality = Column(String, nullable=False)  # Quality setting (standard/hd)

    def __repr__(self):
        return f"<GeneratedImage(id={self.id}, story_version_id={self.story_version_id})>"


class UserSettings(Base):
    """Stores user preferences and application settings."""

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, nullable=False, unique=True, index=True)  # Setting key (e.g., "theme", "model_name")
    value = Column(JSON, nullable=False)  # Setting value (flexible JSON storage)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<UserSettings(key='{self.key}', value={self.value})>"


class StoryAnalytics(Base):
    """Analytics data for story versions including sentiment, bias, and forecasting."""

    __tablename__ = "story_analytics"

    id = Column(Integer, primary_key=True, index=True)
    story_version_id = Column(Integer, nullable=False, index=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Sentiment analysis
    overall_sentiment = Column(String, nullable=True)  # positive, negative, neutral
    sentiment_score = Column(JSON, nullable=True)  # {positive: 0.3, negative: 0.1, neutral: 0.6}

    # Bias analysis
    bias_indicators = Column(JSON, nullable=True)  # {political_lean: "center", loaded_language: [...], ...}
    bias_score = Column(JSON, nullable=True)  # Numerical bias metrics

    # Source-specific sentiment/bias
    source_analysis = Column(JSON, nullable=True)  # Per-source breakdown

    # Fact checking results
    fact_checks = Column(JSON, nullable=True)  # List of claims and their verification status

    # Forecasting/predictions
    predictions = Column(JSON, nullable=True)  # What might happen next

    # Event extraction
    events = Column(JSON, nullable=True)  # Key events extracted from story

    def __repr__(self):
        return f"<StoryAnalytics(story_version_id={self.story_version_id})>"
