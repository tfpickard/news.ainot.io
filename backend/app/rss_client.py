"""RSS feed fetching and parsing."""
import feedparser
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)


class RSSItem:
    """Normalized representation of an RSS/Atom feed item."""

    def __init__(
        self,
        feed_url: str,
        feed_name: str,
        title: str,
        summary: str,
        link: str,
        published_at: Optional[datetime] = None,
        raw: Optional[Dict[str, Any]] = None,
    ):
        self.feed_url = feed_url
        self.feed_name = feed_name
        self.title = title
        self.summary = summary
        self.link = link
        self.published_at = published_at
        self.raw = raw
        self.content_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """Generate a unique hash for deduplication."""
        content = f"{self.link}|{self.title}".encode("utf-8")
        return hashlib.sha256(content).hexdigest()


class RSSClient:
    """Client for fetching and parsing RSS feeds."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def fetch_feed(self, feed_url: str) -> List[RSSItem]:
        """
        Fetch and parse a single RSS feed.

        Args:
            feed_url: URL of the RSS feed

        Returns:
            List of normalized RSSItem objects
        """
        items = []

        try:
            logger.info(f"Fetching feed: {feed_url}")
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")

            feed_name = feed.feed.get("title", feed_url)

            for entry in feed.entries:
                try:
                    item = self._parse_entry(feed_url, feed_name, entry)
                    if item:
                        items.append(item)
                except Exception as e:
                    logger.error(f"Error parsing entry from {feed_url}: {e}", exc_info=True)
                    continue

            logger.info(f"Fetched {len(items)} items from {feed_url}")

        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}", exc_info=True)

        return items

    def _parse_entry(self, feed_url: str, feed_name: str, entry) -> Optional[RSSItem]:
        """Parse a single feed entry into an RSSItem."""
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()

        if not title or not link:
            return None

        # Get summary/description
        summary = (
            entry.get("summary", "") or
            entry.get("description", "") or
            entry.get("content", [{}])[0].get("value", "")
        ).strip()

        # Parse published date
        published_at = None
        for date_field in ["published", "updated", "created"]:
            date_str = entry.get(date_field)
            if date_str:
                try:
                    published_at = parsedate_to_datetime(date_str)
                    break
                except (ValueError, TypeError):
                    try:
                        # Fallback for different date formats
                        published_at = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        break
                    except (ValueError, AttributeError):
                        continue

        # If no valid date, use current time
        if not published_at:
            published_at = datetime.now(timezone.utc)

        # Ensure timezone-aware
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)

        return RSSItem(
            feed_url=feed_url,
            feed_name=feed_name,
            title=title,
            summary=summary,
            link=link,
            published_at=published_at,
            raw=dict(entry),
        )

    def fetch_all_feeds(self, feed_urls: List[str]) -> List[RSSItem]:
        """
        Fetch and parse multiple RSS feeds.

        Args:
            feed_urls: List of feed URLs to fetch

        Returns:
            Combined list of RSSItem objects from all feeds
        """
        all_items = []

        for url in feed_urls:
            items = self.fetch_feed(url)
            all_items.extend(items)

        logger.info(f"Fetched total of {len(all_items)} items from {len(feed_urls)} feeds")
        return all_items
