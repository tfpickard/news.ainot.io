"""Tests for database models."""
import pytest
from datetime import datetime, timezone

from app.models import StoryVersion, FeedItem


def test_create_story_version(test_db):
    """Test creating a story version."""
    story = StoryVersion(
        full_text="This is a test story about global events.",
        summary="Test story summary",
        context_summary="Brief context",
        sources_snapshot={"items": [1, 2, 3]},
        token_stats={"total": 150}
    )

    test_db.add(story)
    test_db.commit()
    test_db.refresh(story)

    assert story.id is not None
    assert story.created_at is not None
    assert story.full_text == "This is a test story about global events."
    assert story.summary == "Test story summary"


def test_create_feed_item(test_db):
    """Test creating a feed item."""
    feed_item = FeedItem(
        feed_url="http://example.com/rss",
        feed_name="Example Feed",
        title="Test Article",
        summary="This is a test article",
        link="http://example.com/article",
        published_at=datetime.now(timezone.utc),
        content_hash="abc123",
        raw={"key": "value"}
    )

    test_db.add(feed_item)
    test_db.commit()
    test_db.refresh(feed_item)

    assert feed_item.id is not None
    assert feed_item.title == "Test Article"
    assert feed_item.content_hash == "abc123"


def test_feed_item_unique_constraint(test_db):
    """Test that duplicate feed items are prevented."""
    # Create first item
    item1 = FeedItem(
        feed_url="http://example.com/rss",
        feed_name="Example",
        title="Duplicate Test",
        link="http://example.com/dup",
        content_hash="duplicate_hash"
    )
    test_db.add(item1)
    test_db.commit()

    # Try to create duplicate
    item2 = FeedItem(
        feed_url="http://example.com/rss",
        feed_name="Example",
        title="Duplicate Test",
        link="http://example.com/dup",
        content_hash="duplicate_hash"
    )
    test_db.add(item2)

    with pytest.raises(Exception):  # Should raise IntegrityError
        test_db.commit()
