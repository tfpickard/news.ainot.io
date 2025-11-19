"""Service for generating trend analytics from story data."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import re

from .models import StoryVersion, StoryAnalytics, FeedItem, FeedConfiguration
from .schemas import (
    TrendDataPoint,
    SentimentTrendResponse,
    KeywordFrequency,
    KeywordCloudResponse,
    AbsurdityDataPoint,
    AbsurdityTrendResponse,
    SourceContribution,
    SourceDominanceResponse,
    PredictionAccuracy,
    PredictionTrackingResponse,
    TrendAnalyticsResponse,
)

logger = logging.getLogger(__name__)


class TrendsService:
    """Service for generating trend analytics."""

    def __init__(self, db: Session):
        self.db = db

    def get_sentiment_trends(
        self, days: int = 7, limit: Optional[int] = None
    ) -> SentimentTrendResponse:
        """
        Get sentiment trends over time.

        Args:
            days: Number of days to look back
            limit: Optional limit on number of stories
        """
        cutoff = datetime.now() - timedelta(days=days)

        # Query stories with analytics
        query = (
            self.db.query(StoryVersion, StoryAnalytics)
            .join(StoryAnalytics, StoryVersion.id == StoryAnalytics.story_version_id)
            .filter(StoryVersion.created_at >= cutoff)
            .order_by(StoryVersion.created_at)
        )

        if limit:
            query = query.limit(limit)

        results = query.all()

        positive_trend = []
        negative_trend = []
        neutral_trend = []
        overall_trend = []

        for story, analytics in results:
            if analytics.sentiment_score:
                sentiment = analytics.sentiment_score
                timestamp = story.created_at

                positive_trend.append(
                    TrendDataPoint(
                        timestamp=timestamp,
                        value=sentiment.get("positive", 0.0),
                        story_id=story.id,
                        label=story.summary[:50],
                    )
                )

                negative_trend.append(
                    TrendDataPoint(
                        timestamp=timestamp,
                        value=sentiment.get("negative", 0.0),
                        story_id=story.id,
                        label=story.summary[:50],
                    )
                )

                neutral_trend.append(
                    TrendDataPoint(
                        timestamp=timestamp,
                        value=sentiment.get("neutral", 0.0),
                        story_id=story.id,
                        label=story.summary[:50],
                    )
                )

                overall_trend.append(
                    {
                        "story_id": story.id,
                        "timestamp": timestamp.isoformat(),
                        "sentiment": analytics.overall_sentiment,
                        "scores": sentiment,
                    }
                )

        return SentimentTrendResponse(
            positive_trend=positive_trend,
            negative_trend=negative_trend,
            neutral_trend=neutral_trend,
            overall_trend=overall_trend,
        )

    def get_keyword_cloud(
        self, days: int = 7, limit: Optional[int] = None, min_freq: int = 2
    ) -> KeywordCloudResponse:
        """
        Extract keyword frequencies from stories.

        Args:
            days: Number of days to look back
            limit: Optional limit on number of stories
            min_freq: Minimum frequency for a keyword to be included
        """
        cutoff = datetime.now() - timedelta(days=days)

        query = self.db.query(StoryVersion).filter(StoryVersion.created_at >= cutoff)

        if limit:
            query = query.limit(limit)

        stories = query.all()

        # Extract keywords from all stories
        keyword_stories: Dict[str, List[int]] = {}
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "been",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
            "they",
            "their",
            "them",
            "we",
            "our",
            "you",
            "your",
        }

        for story in stories:
            # Extract words (simple tokenization)
            text = f"{story.summary} {story.full_text}"
            words = re.findall(r"\b[a-z]{4,}\b", text.lower())

            # Filter stop words and count
            for word in words:
                if word not in stop_words:
                    if word not in keyword_stories:
                        keyword_stories[word] = []
                    if story.id not in keyword_stories[word]:
                        keyword_stories[word].append(story.id)

        # Convert to KeywordFrequency objects
        keywords = [
            KeywordFrequency(keyword=word, count=len(story_ids), stories=story_ids)
            for word, story_ids in keyword_stories.items()
            if len(story_ids) >= min_freq
        ]

        # Sort by frequency
        keywords.sort(key=lambda k: k.count, reverse=True)

        # Limit to top 100 keywords
        keywords = keywords[:100]

        date_range = {}
        if stories:
            date_range = {
                "start": min(s.created_at for s in stories),
                "end": max(s.created_at for s in stories),
            }

        return KeywordCloudResponse(
            keywords=keywords, total_keywords=len(keywords), date_range=date_range
        )

    def get_absurdity_trends(
        self, days: int = 7, limit: Optional[int] = None
    ) -> AbsurdityTrendResponse:
        """
        Get absurdity score trends over time.

        Args:
            days: Number of days to look back
            limit: Optional limit on number of stories
        """
        cutoff = datetime.now() - timedelta(days=days)

        # For now, we'll use bias indicators and fact-check data to compute absurdity
        query = (
            self.db.query(StoryVersion, StoryAnalytics)
            .join(StoryAnalytics, StoryVersion.id == StoryAnalytics.story_version_id)
            .filter(StoryVersion.created_at >= cutoff)
            .order_by(StoryVersion.created_at)
        )

        if limit:
            query = query.limit(limit)

        results = query.all()

        data_points = []
        total_score = 0.0

        for story, analytics in results:
            # Calculate absurdity score based on various factors
            absurdity = 5.0  # Base score

            # Factor 1: Bias extremity
            if analytics.bias_score and "lean_score" in analytics.bias_score:
                lean = abs(analytics.bias_score.get("lean_score", 0))
                absurdity += lean * 2  # Max +2 points

            # Factor 2: Loaded language count
            if analytics.bias_indicators and "loaded_language" in analytics.bias_indicators:
                loaded = len(analytics.bias_indicators.get("loaded_language", []))
                absurdity += min(loaded / 5, 2)  # Max +2 points

            # Factor 3: Unverified/misleading claims
            if analytics.fact_checks:
                misleading = sum(
                    1
                    for fc in analytics.fact_checks
                    if fc.get("verdict") in ["unverified", "misleading", "false"]
                )
                absurdity += min(misleading / 2, 3)  # Max +3 points

            # Cap at 10
            absurdity = min(absurdity, 10.0)
            total_score += absurdity

            # Try to find a quote (simplified - would integrate with quote service)
            top_quote = story.summary[:100] + "..." if len(story.summary) > 100 else story.summary

            data_points.append(
                AbsurdityDataPoint(
                    timestamp=story.created_at,
                    story_id=story.id,
                    absurdity_score=round(absurdity, 2),
                    top_quote=top_quote,
                )
            )

        average_score = total_score / len(data_points) if data_points else 5.0
        peak = max(data_points, key=lambda x: x.absurdity_score) if data_points else None

        if not peak:
            # Create a dummy peak
            peak = AbsurdityDataPoint(
                timestamp=datetime.now(),
                story_id=0,
                absurdity_score=5.0,
                top_quote="No data available",
            )

        return AbsurdityTrendResponse(
            data_points=data_points,
            average_score=round(average_score, 2),
            peak_absurdity=peak,
        )

    def get_source_dominance(
        self, days: int = 7
    ) -> SourceDominanceResponse:
        """
        Get source contribution and dominance metrics.

        Args:
            days: Number of days to look back
        """
        cutoff = datetime.now() - timedelta(days=days)

        # Get all stories in time range
        stories = (
            self.db.query(StoryVersion)
            .filter(StoryVersion.created_at >= cutoff)
            .all()
        )

        # Get feed items and configurations
        feed_items = (
            self.db.query(FeedItem)
            .filter(FeedItem.fetched_at >= cutoff)
            .all()
        )

        feed_configs = self.db.query(FeedConfiguration).all()
        feed_config_map = {fc.url: fc for fc in feed_configs}

        # Aggregate by source
        source_stats: Dict[str, Dict[str, Any]] = {}

        for item in feed_items:
            source_name = item.feed_name
            if source_name not in source_stats:
                config = feed_config_map.get(item.feed_url)
                source_stats[source_name] = {
                    "article_count": 0,
                    "categories": set(),
                    "sentiments": [],
                }
                if config and config.category:
                    source_stats[source_name]["categories"].add(config.category)

            source_stats[source_name]["article_count"] += 1

        # Convert to SourceContribution objects
        sources = []
        for source_name, stats in source_stats.items():
            avg_sentiment = (
                sum(stats["sentiments"]) / len(stats["sentiments"])
                if stats["sentiments"]
                else 0.0
            )

            sources.append(
                SourceContribution(
                    source_name=source_name,
                    story_count=len(stories),  # All sources contribute to all stories in this model
                    article_count=stats["article_count"],
                    avg_sentiment=round(avg_sentiment, 2),
                    categories=list(stats["categories"]),
                )
            )

        # Sort by article count
        sources.sort(key=lambda s: s.article_count, reverse=True)

        date_range = {}
        if stories:
            date_range = {
                "start": min(s.created_at for s in stories),
                "end": max(s.created_at for s in stories),
            }

        return SourceDominanceResponse(
            sources=sources, total_stories=len(stories), date_range=date_range
        )

    def get_full_trends(
        self, days: int = 7, limit: Optional[int] = None
    ) -> TrendAnalyticsResponse:
        """
        Get complete trend analytics.

        Args:
            days: Number of days to look back
            limit: Optional limit on number of stories
        """
        sentiment_trends = self.get_sentiment_trends(days=days, limit=limit)
        keyword_cloud = self.get_keyword_cloud(days=days, limit=limit)
        absurdity_trends = self.get_absurdity_trends(days=days, limit=limit)
        source_dominance = self.get_source_dominance(days=days)

        cutoff = datetime.now() - timedelta(days=days)
        story_count = (
            self.db.query(func.count(StoryVersion.id))
            .filter(StoryVersion.created_at >= cutoff)
            .scalar()
        )

        date_range = {
            "start": datetime.now() - timedelta(days=days),
            "end": datetime.now(),
        }

        return TrendAnalyticsResponse(
            sentiment_trends=sentiment_trends,
            keyword_cloud=keyword_cloud,
            absurdity_trends=absurdity_trends,
            source_dominance=source_dominance,
            date_range=date_range,
            total_stories_analyzed=story_count or 0,
        )
