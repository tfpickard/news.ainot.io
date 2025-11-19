"""Service for full-text search and entity tracking."""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, text
from collections import Counter
import re

from .models import StoryVersion, FeedItem, StoryAnalytics
from .schemas import StoryVersionSummary

logger = logging.getLogger(__name__)


class SearchService:
    """Service for searching stories and tracking entities."""

    def __init__(self, db: Session):
        self.db = db

    def search_stories(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        include_feed_items: bool = False,
    ) -> Dict[str, Any]:
        """
        Search stories using full-text search.

        Args:
            query: Search query string
            limit: Maximum number of results
            offset: Pagination offset
            include_feed_items: Whether to also search feed items
        """
        # Basic full-text search using PostgreSQL LIKE for simplicity
        # In production, you'd use PostgreSQL's full-text search features
        search_pattern = f"%{query}%"

        # Search in story versions
        story_query = (
            self.db.query(StoryVersion)
            .filter(
                or_(
                    StoryVersion.full_text.ilike(search_pattern),
                    StoryVersion.summary.ilike(search_pattern),
                )
            )
            .order_by(StoryVersion.created_at.desc())
        )

        total_count = story_query.count()
        stories = story_query.offset(offset).limit(limit).all()

        results = []
        for story in stories:
            # Find snippet with query
            snippet = self._extract_snippet(story.full_text, query)

            results.append(
                {
                    "id": story.id,
                    "created_at": story.created_at.isoformat(),
                    "summary": story.summary,
                    "snippet": snippet,
                    "match_type": "story",
                }
            )

        # Optionally search feed items
        feed_results = []
        if include_feed_items:
            feed_query = (
                self.db.query(FeedItem)
                .filter(
                    or_(
                        FeedItem.title.ilike(search_pattern),
                        FeedItem.summary.ilike(search_pattern),
                    )
                )
                .order_by(FeedItem.published_at.desc())
                .limit(10)
            )

            for item in feed_query.all():
                feed_results.append(
                    {
                        "id": item.id,
                        "title": item.title,
                        "feed_name": item.feed_name,
                        "published_at": item.published_at.isoformat()
                        if item.published_at
                        else None,
                        "snippet": item.summary[:200] if item.summary else "",
                    }
                )

        return {
            "query": query,
            "total_results": total_count,
            "offset": offset,
            "limit": limit,
            "results": results,
            "feed_results": feed_results if include_feed_items else [],
        }

    def _extract_snippet(self, text: str, query: str, context_chars: int = 150) -> str:
        """Extract a snippet of text around the search query."""
        query_lower = query.lower()
        text_lower = text.lower()

        # Find first occurrence
        pos = text_lower.find(query_lower)
        if pos == -1:
            # Return start of text if query not found
            return text[:context_chars] + "..."

        # Calculate snippet bounds
        start = max(0, pos - context_chars // 2)
        end = min(len(text), pos + len(query) + context_chars // 2)

        snippet = text[start:end]

        # Add ellipsis
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet

    def track_entities(
        self, story_ids: Optional[List[int]] = None, limit: int = 50
    ) -> Dict[str, Any]:
        """
        Track recurring entities (people, places, organizations) across stories.

        Args:
            story_ids: Optional list of story IDs to analyze (all stories if None)
            limit: Maximum number of recent stories to analyze if story_ids not provided
        """
        # Get stories to analyze
        if story_ids:
            stories = (
                self.db.query(StoryVersion)
                .filter(StoryVersion.id.in_(story_ids))
                .all()
            )
        else:
            stories = (
                self.db.query(StoryVersion)
                .order_by(StoryVersion.created_at.desc())
                .limit(limit)
                .all()
            )

        # Extract entities using simple pattern matching
        # In production, you'd use NLP libraries like spaCy or NLTK
        entities = {
            "people": Counter(),
            "places": Counter(),
            "organizations": Counter(),
            "concepts": Counter(),
        }

        for story in stories:
            text = story.full_text + " " + story.summary

            # Very basic capitalized word detection (simplified entity extraction)
            # Find sequences of capitalized words
            capitalized_phrases = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)

            for phrase in capitalized_phrases:
                # Skip common words
                if phrase.lower() in [
                    "the",
                    "a",
                    "an",
                    "this",
                    "that",
                    "these",
                    "those",
                ]:
                    continue

                # Simple heuristics for categorization
                words = phrase.split()
                if len(words) == 1:
                    # Single capitalized word - could be person or place
                    entities["people"][phrase] += 1
                elif len(words) >= 2:
                    # Multi-word phrase - likely organization or place
                    entities["organizations"][phrase] += 1

        # Convert to lists and get top entities
        result = {}
        for category, counter in entities.items():
            result[category] = [
                {"name": name, "count": count, "category": category}
                for name, count in counter.most_common(50)
            ]

        return {
            "total_stories_analyzed": len(stories),
            "entities": result,
        }

    def get_entity_timeline(self, entity_name: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get timeline of stories mentioning a specific entity.

        Args:
            entity_name: Name of the entity to track
            limit: Maximum number of stories to return
        """
        search_pattern = f"%{entity_name}%"

        stories = (
            self.db.query(StoryVersion)
            .filter(
                or_(
                    StoryVersion.full_text.ilike(search_pattern),
                    StoryVersion.summary.ilike(search_pattern),
                )
            )
            .order_by(StoryVersion.created_at)
            .limit(limit)
            .all()
        )

        timeline = []
        for story in stories:
            snippet = self._extract_snippet(story.full_text, entity_name, 100)
            timeline.append(
                {
                    "story_id": story.id,
                    "created_at": story.created_at.isoformat(),
                    "summary": story.summary,
                    "snippet": snippet,
                }
            )

        return {
            "entity": entity_name,
            "occurrences": len(timeline),
            "timeline": timeline,
        }

    def get_related_stories(self, story_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find stories related to a given story based on keyword similarity.

        Args:
            story_id: ID of the reference story
            limit: Maximum number of related stories to return
        """
        # Get the reference story
        story = (
            self.db.query(StoryVersion).filter(StoryVersion.id == story_id).first()
        )

        if not story:
            return []

        # Extract keywords from the story (simplified)
        text = story.summary.lower()
        words = re.findall(r"\b[a-z]{4,}\b", text)

        # Get stop words
        stop_words = {
            "that",
            "this",
            "with",
            "from",
            "have",
            "been",
            "were",
            "will",
            "would",
            "could",
            "their",
        }
        keywords = [w for w in words if w not in stop_words][:10]

        if not keywords:
            return []

        # Find other stories with similar keywords
        related = []
        for keyword in keywords:
            search_pattern = f"%{keyword}%"
            similar_stories = (
                self.db.query(StoryVersion)
                .filter(
                    StoryVersion.id != story_id,
                    or_(
                        StoryVersion.full_text.ilike(search_pattern),
                        StoryVersion.summary.ilike(search_pattern),
                    ),
                )
                .limit(2)
                .all()
            )

            for s in similar_stories:
                if s.id not in [r["id"] for r in related]:
                    related.append(
                        {
                            "id": s.id,
                            "created_at": s.created_at.isoformat(),
                            "summary": s.summary,
                            "matching_keyword": keyword,
                        }
                    )

                if len(related) >= limit:
                    break

            if len(related) >= limit:
                break

        return related[:limit]
