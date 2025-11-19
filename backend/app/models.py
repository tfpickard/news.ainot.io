"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, UniqueConstraint
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
