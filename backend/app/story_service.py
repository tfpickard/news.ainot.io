"""Business logic for story evolution and management."""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import StoryVersion, FeedItem
from .schemas import StoryVersionCreate
from .rss_client import RSSClient, RSSItem
from .openai_client import StoryGenerator
from .config import settings

logger = logging.getLogger(__name__)


class StoryService:
    """Service for managing the evolving story."""

    def __init__(self, db: Session):
        self.db = db
        self.rss_client = RSSClient()
        self.story_generator = StoryGenerator()

    def ingest_feeds(self) -> int:
        """
        Fetch latest RSS feeds and store new items in database.

        Returns:
            Number of new items added
        """
        logger.info("Starting RSS feed ingestion")

        feed_urls = settings.get_feed_list()
        rss_items = self.rss_client.fetch_all_feeds(feed_urls)

        new_count = 0

        for item in rss_items:
            # Check if item already exists
            existing = (
                self.db.query(FeedItem)
                .filter(FeedItem.content_hash == item.content_hash)
                .first()
            )

            if not existing:
                feed_item = FeedItem(
                    feed_url=item.feed_url,
                    feed_name=item.feed_name,
                    title=item.title,
                    summary=item.summary,
                    link=item.link,
                    published_at=item.published_at,
                    content_hash=item.content_hash,
                    raw=item.raw,
                )
                self.db.add(feed_item)
                new_count += 1

        self.db.commit()
        logger.info(f"Ingested {new_count} new feed items")

        return new_count

    def get_new_feed_items(self, since: Optional[datetime] = None) -> List[FeedItem]:
        """
        Get feed items published since a given timestamp.

        Args:
            since: Datetime to filter from (default: last story version timestamp)

        Returns:
            List of FeedItem objects
        """
        if since is None:
            # Get timestamp of last story version
            last_story = (
                self.db.query(StoryVersion)
                .order_by(desc(StoryVersion.created_at))
                .first()
            )
            if last_story:
                since = last_story.created_at
            else:
                # No stories yet, get items from last 24 hours
                since = datetime.now(timezone.utc) - timedelta(hours=24)

        items = (
            self.db.query(FeedItem)
            .filter(FeedItem.published_at > since)
            .order_by(desc(FeedItem.published_at))
            .limit(50)  # Limit to most recent 50 items
            .all()
        )

        return items

    def build_narrative_context(self, limit: int = None) -> str:
        """
        Build compressed narrative context from previous story versions.

        Args:
            limit: Number of recent versions to include (default: SINGL_CONTEXT_STEPS)

        Returns:
            String containing condensed narrative context
        """
        if limit is None:
            limit = settings.singl_context_steps

        # Get recent story versions
        versions = (
            self.db.query(StoryVersion)
            .order_by(desc(StoryVersion.created_at))
            .limit(limit)
            .all()
        )

        if not versions:
            return "This is the beginning of THE STORY. The world awaits its first unified narrative."

        # Use most recent version's context_summary if available
        if versions[0].context_summary:
            return versions[0].context_summary

        # Otherwise, build from available versions
        if len(versions) == 1:
            return f"THE STORY SO FAR:\n\n{versions[0].full_text}"

        # For multiple versions, compress older ones
        if len(versions) <= 3:
            # Few versions, just concatenate
            texts = [v.summary for v in reversed(versions)]
            return "THE STORY SO FAR:\n\n" + "\n\n".join(texts)
        else:
            # Many versions: summarize older ones, keep recent ones fuller
            older_texts = [v.summary for v in reversed(versions[3:])]
            context = self.story_generator.generate_context_summary(older_texts)

            recent_texts = [v.summary for v in reversed(versions[:3])]
            context += "\n\nRECENT DEVELOPMENTS:\n" + "\n\n".join(recent_texts)

            return context

    def build_recent_excerpts(self, count: int = 2) -> str:
        """
        Get recent story text excerpts for tone/continuity.

        Args:
            count: Number of recent versions to excerpt

        Returns:
            String containing recent story excerpts
        """
        versions = (
            self.db.query(StoryVersion)
            .order_by(desc(StoryVersion.created_at))
            .limit(count)
            .all()
        )

        if not versions:
            return ""

        excerpts = []
        for v in reversed(versions):
            # Take first 500 chars of each version
            excerpt = v.full_text[:500]
            if len(v.full_text) > 500:
                excerpt += "..."
            excerpts.append(f"[{v.created_at.strftime('%Y-%m-%d %H:%M UTC')}]\n{excerpt}")

        return "\n\n".join(excerpts)

    def build_new_events_summary(self, feed_items: List[FeedItem]) -> str:
        """
        Build a summary of new feed items to incorporate.

        Args:
            feed_items: List of FeedItem objects

        Returns:
            String summarizing new events
        """
        if not feed_items:
            return "No new events to report. Continue developing existing story threads."

        events = []
        for item in feed_items:
            # Format: [Source] Title - Summary
            event = f"• [{item.feed_name}] {item.title}"
            if item.summary:
                # Truncate summary
                summary = item.summary[:200]
                if len(item.summary) > 200:
                    summary += "..."
                event += f"\n  {summary}"
            events.append(event)

        # Limit to 20 events to avoid prompt bloat
        if len(events) > 20:
            events = events[:20]
            events.append(f"... and {len(feed_items) - 20} more developments")

        return "\n\n".join(events)

    def generate_next_story_version(self) -> Optional[StoryVersion]:
        """
        Generate the next version of the evolving story.

        Returns:
            New StoryVersion object or None if generation failed
        """
        logger.info("Generating next story version")

        try:
            # Get new feed items
            new_items = self.get_new_feed_items()

            # Build context
            narrative_context = self.build_narrative_context()
            recent_excerpts = self.build_recent_excerpts()
            new_events = self.build_new_events_summary(new_items)

            # Generate story
            result = self.story_generator.generate_story_continuation(
                narrative_context=narrative_context,
                recent_excerpts=recent_excerpts,
                new_events=new_events,
            )

            # Prepare sources snapshot
            sources_snapshot = {
                "feed_items": [
                    {
                        "id": item.id,
                        "title": item.title,
                        "source": item.feed_name,
                        "published_at": item.published_at.isoformat() if item.published_at else None,
                    }
                    for item in new_items
                ],
                "item_count": len(new_items),
            }

            # Create new context summary for next iteration
            # Combine previous context with new story
            all_recent = (
                self.db.query(StoryVersion)
                .order_by(desc(StoryVersion.created_at))
                .limit(5)
                .all()
            )
            context_texts = [v.full_text for v in reversed(all_recent)] + [result["story"]]
            new_context_summary = self.story_generator.generate_context_summary(context_texts)

            # Create story version
            story_version = StoryVersion(
                full_text=result["story"],
                summary=result["summary"],
                context_summary=new_context_summary,
                sources_snapshot=sources_snapshot,
                token_stats=result["usage"],
            )

            self.db.add(story_version)
            self.db.commit()
            self.db.refresh(story_version)

            logger.info(f"Successfully created story version {story_version.id}")

            return story_version

        except Exception as e:
            logger.error(f"Failed to generate story version: {e}", exc_info=True)
            self.db.rollback()
            return None

    def get_latest_story(self) -> Optional[StoryVersion]:
        """Get the most recent story version."""
        return (
            self.db.query(StoryVersion)
            .order_by(desc(StoryVersion.created_at))
            .first()
        )

    def get_story_by_id(self, story_id: int) -> Optional[StoryVersion]:
        """Get a specific story version by ID."""
        return self.db.query(StoryVersion).filter(StoryVersion.id == story_id).first()

    def get_story_history(self, limit: int = 20, offset: int = 0) -> List[StoryVersion]:
        """
        Get paginated story history.

        Args:
            limit: Number of versions to return
            offset: Number of versions to skip

        Returns:
            List of StoryVersion objects
        """
        return (
            self.db.query(StoryVersion)
            .order_by(desc(StoryVersion.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_story_count(self) -> int:
        """Get total number of story versions."""
        return self.db.query(StoryVersion).count()
