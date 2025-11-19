"""Tests for RSS client."""
import pytest
from app.rss_client import RSSClient, RSSItem


def test_rss_item_hash_generation():
    """Test that RSSItem generates consistent hashes."""
    item1 = RSSItem(
        feed_url="http://example.com/feed",
        feed_name="Example",
        title="Test Article",
        summary="Summary",
        link="http://example.com/article"
    )

    item2 = RSSItem(
        feed_url="http://example.com/feed",
        feed_name="Example",
        title="Test Article",
        summary="Summary",
        link="http://example.com/article"
    )

    # Same link and title should produce same hash
    assert item1.content_hash == item2.content_hash


def test_rss_item_different_hash():
    """Test that different items have different hashes."""
    item1 = RSSItem(
        feed_url="http://example.com/feed",
        feed_name="Example",
        title="Article One",
        summary="Summary",
        link="http://example.com/article1"
    )

    item2 = RSSItem(
        feed_url="http://example.com/feed",
        feed_name="Example",
        title="Article Two",
        summary="Summary",
        link="http://example.com/article2"
    )

    assert item1.content_hash != item2.content_hash


def test_rss_client_creation():
    """Test creating RSS client."""
    client = RSSClient(timeout=15)
    assert client.timeout == 15


# Note: Actual RSS feed fetching tests would require mocking
# or using test feeds, which is beyond scope of basic tests
