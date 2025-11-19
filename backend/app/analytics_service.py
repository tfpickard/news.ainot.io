"""Analytics service for sentiment, bias, fact-checking, and forecasting."""
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from openai import OpenAI

from .models import StoryVersion, StoryAnalytics, FeedItem
from .config import settings

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analyzing stories with AI."""

    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.singl_model_name

    def analyze_story(self, story: StoryVersion) -> Optional[StoryAnalytics]:
        """
        Perform comprehensive analysis on a story.

        Args:
            story: StoryVersion to analyze

        Returns:
            StoryAnalytics object with results
        """
        # Capture story ID early to avoid lazy loading issues after rollback
        story_id = story.id
        logger.info(f"Analyzing story {story_id}")

        try:
            # Check if analytics already exist
            existing = (
                self.db.query(StoryAnalytics)
                .filter(StoryAnalytics.story_version_id == story_id)
                .first()
            )

            if existing:
                logger.info(f"Analytics already exist for story {story_id}")
                return existing

            # Perform all analyses
            sentiment = self._analyze_sentiment(story.full_text)
            bias = self._analyze_bias(story.full_text)
            source_analysis = self._analyze_sources(story)
            fact_checks = self._extract_fact_checks(story.full_text)
            predictions = self._generate_predictions(story.full_text)
            events = self._extract_events(story.full_text)

            # Create analytics record
            analytics = StoryAnalytics(
                story_version_id=story_id,
                overall_sentiment=sentiment.get("overall"),
                sentiment_score=sentiment.get("score"),
                bias_indicators=bias.get("indicators"),
                bias_score=bias.get("score"),
                source_analysis=source_analysis,
                fact_checks=fact_checks,
                predictions=predictions,
                events=events,
            )

            self.db.add(analytics)

            try:
                self.db.commit()
                self.db.refresh(analytics)
                logger.info(f"Successfully created analytics for story {story_id}")
                return analytics
            except IntegrityError as ie:
                # Race condition: another request already created analytics for this story
                logger.warning(f"Analytics already exist for story {story_id} (race condition)")
                # Rollback to clear the failed transaction
                self.db.rollback()
                # Expunge all objects to fully reset session state
                self.db.expunge_all()

                # Query for the existing analytics created by the other request
                try:
                    existing = (
                        self.db.query(StoryAnalytics)
                        .filter(StoryAnalytics.story_version_id == story_id)
                        .first()
                    )
                    if existing:
                        return existing
                    else:
                        logger.error(f"Could not find existing analytics for story {story_id} after race condition")
                        return None
                except Exception as query_error:
                    logger.error(f"Error querying for existing analytics: {query_error}")
                    # If we still can't query, just return None
                    # The analytics exist, the caller can retry if needed
                    return None

        except Exception as e:
            logger.error(f"Failed to analyze story {story_id}: {e}", exc_info=True)
            self.db.rollback()
            return None

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the story text."""
        try:
            system_prompt = """You are a sentiment analysis expert. Analyze the overall tone and sentiment of news text.
Return your analysis as JSON with:
- overall: "positive", "negative", or "neutral"
- score: {positive: 0.0-1.0, negative: 0.0-1.0, neutral: 0.0-1.0} (must sum to 1.0)
- reasoning: brief explanation"""

            user_prompt = f"Analyze sentiment of:\n\n{text[:3000]}"

            if "gpt-5" in self.model:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                    max_output_tokens=500,
                    reasoning={"effort": "minimal"},
                    text={"verbosity": "low"},
                )
            else:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                    temperature=0.3,
                    max_output_tokens=500,
                )

            output_text = response.output_text.strip()
            try:
                result = json.loads(output_text)
                return result
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse sentiment JSON: {je}")
                logger.debug(f"Raw output: {output_text[:500]}")
                return {
                    "overall": "neutral",
                    "score": {"positive": 0.33, "negative": 0.33, "neutral": 0.34},
                    "reasoning": "JSON parsing failed"
                }

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                "overall": "neutral",
                "score": {"positive": 0.33, "negative": 0.33, "neutral": 0.34},
                "reasoning": "Analysis unavailable"
            }

    def _analyze_bias(self, text: str) -> Dict[str, Any]:
        """Analyze potential bias in the story."""
        try:
            system_prompt = """You are a media bias detection expert. Analyze news text for bias indicators.
Return JSON with:
- score: {
    political_lean: "left" | "center-left" | "center" | "center-right" | "right" | "unknown",
    lean_score: -1.0 to 1.0 (negative=left, positive=right),
    loaded_language_count: number of loaded/emotional words,
    emotional_language_score: 0.0-1.0
  }
- indicators: {
    loaded_terms: [list of biased words/phrases found],
    omissions: [potential important omissions],
    framing: brief description of how story is framed
  }"""

            user_prompt = f"Analyze bias in:\n\n{text[:3000]}"

            if "gpt-5" in self.model:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                    max_output_tokens=800,
                    reasoning={"effort": "minimal"},
                    text={"verbosity": "medium"},
                )
            else:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                    temperature=0.3,
                    max_output_tokens=800,
                )

            output_text = response.output_text.strip()
            try:
                result = json.loads(output_text)
                return result
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse bias JSON: {je}")
                logger.debug(f"Raw output: {output_text[:500]}")
                return {
                    "score": {
                        "political_lean": "unknown",
                        "lean_score": 0.0,
                        "loaded_language_count": 0,
                        "emotional_language_score": 0.0
                    },
                    "indicators": {"loaded_terms": [], "omissions": [], "framing": "JSON parsing failed"}
                }

        except Exception as e:
            logger.error(f"Bias analysis failed: {e}")
            return {
                "score": {
                    "political_lean": "unknown",
                    "lean_score": 0.0,
                    "loaded_language_count": 0,
                    "emotional_language_score": 0.0
                },
                "indicators": {"loaded_terms": [], "omissions": [], "framing": "Analysis unavailable"}
            }

    def _analyze_sources(self, story: StoryVersion) -> List[Dict[str, Any]]:
        """Analyze sentiment and bias per source."""
        if not story.sources_snapshot or "feed_items" not in story.sources_snapshot:
            return []

        source_map: Dict[str, List[int]] = {}
        for item_data in story.sources_snapshot["feed_items"]:
            source = item_data.get("source", "Unknown")
            if source not in source_map:
                source_map[source] = []
            source_map[source].append(item_data["id"])

        results = []
        for source_name, item_ids in source_map.items():
            # Get feed items for this source
            items = self.db.query(FeedItem).filter(FeedItem.id.in_(item_ids)).all()

            # Combine text from all items from this source
            combined_text = "\n\n".join([
                f"{item.title}\n{item.summary or ''}" for item in items
            ])

            if not combined_text.strip():
                continue

            # Analyze this source's content
            sentiment = self._analyze_sentiment(combined_text)
            bias = self._analyze_bias(combined_text)

            results.append({
                "source_name": source_name,
                "sentiment": sentiment.get("score", {"positive": 0.33, "negative": 0.33, "neutral": 0.34}),
                "bias": bias.get("score", {
                    "political_lean": "unknown",
                    "lean_score": 0.0,
                    "loaded_language_count": 0,
                    "emotional_language_score": 0.0
                }),
                "article_count": len(items)
            })

        return results

    def _extract_fact_checks(self, text: str) -> List[Dict[str, Any]]:
        """Extract and verify factual claims."""
        try:
            system_prompt = """You are a fact-checking expert. Extract factual claims from news text and assess their veracity.
Return JSON with:
- fact_checks: array of {
    claim: "specific factual claim",
    verdict: "true" | "false" | "partially-true" | "unverified" | "misleading",
    confidence: 0.0-1.0,
    explanation: brief reasoning,
    sources: [relevant sources if available]
  }

Focus on verifiable facts, not opinions. Mark as "unverified" if you cannot determine accuracy."""

            user_prompt = f"Extract and verify claims from:\n\n{text[:3000]}"

            if "gpt-5" in self.model:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                    max_output_tokens=1500,
                    reasoning={"effort": "minimal"},
                    text={"verbosity": "medium"},
                )
            else:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                    temperature=0.3,
                    max_output_tokens=1500,
                )

            output_text = response.output_text.strip()
            try:
                result = json.loads(output_text)
                return result.get("fact_checks", [])
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse fact checking JSON: {je}")
                logger.debug(f"Raw output: {output_text[:500]}")
                return []

        except Exception as e:
            logger.error(f"Fact checking failed: {e}")
            return []

    def _generate_predictions(self, text: str) -> List[Dict[str, Any]]:
        """Generate predictions about what might happen next."""
        try:
            system_prompt = """You are a geopolitical analyst and forecaster. Based on current events, predict likely future developments.
Return JSON with:
- predictions: array of {
    scenario: "description of what might happen",
    probability: 0.0-1.0 (estimated likelihood),
    timeframe: "short-term" | "medium-term" | "long-term",
    reasoning: explanation of why this might happen,
    related_events: [list of current events that support this prediction]
  }

Provide 3-5 diverse predictions ranging from likely to possible."""

            user_prompt = f"Based on these events, predict what might happen next:\n\n{text[:3000]}"

            if "gpt-5" in self.model:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                    max_output_tokens=1500,
                    reasoning={"effort": "minimal"},
                    text={"verbosity": "medium"},
                )
            else:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                    temperature=0.7,
                    max_output_tokens=1500,
                )

            output_text = response.output_text.strip()
            try:
                result = json.loads(output_text)
                return result.get("predictions", [])
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse predictions JSON: {je}")
                logger.debug(f"Raw output: {output_text[:500]}")
                return []

        except Exception as e:
            logger.error(f"Prediction generation failed: {e}")
            return []

    def _extract_events(self, text: str) -> List[Dict[str, Any]]:
        """Extract key events for timeline visualization."""
        try:
            system_prompt = """You are an event extraction expert. Identify discrete events from news text.
Return JSON with:
- events: array of {
    title: "brief event title",
    description: "1-2 sentence description",
    timestamp: "ISO date/time if mentioned, or null",
    category: "political" | "economic" | "social" | "conflict" | "disaster" | "technology" | "other",
    importance: 1-10 (how significant is this event)
  }

Extract 5-10 most important events."""

            user_prompt = f"Extract key events from:\n\n{text[:3000]}"

            if "gpt-5" in self.model:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                    max_output_tokens=1200,
                    reasoning={"effort": "minimal"},
                    text={"verbosity": "medium"},
                )
            else:
                response = self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=user_prompt,
                    temperature=0.3,
                    max_output_tokens=1200,
                )

            output_text = response.output_text.strip()
            try:
                result = json.loads(output_text)
                return result.get("events", [])
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse events JSON: {je}")
                logger.debug(f"Raw output: {output_text[:500]}")
                return []

        except Exception as e:
            logger.error(f"Event extraction failed: {e}")
            return []

    def get_analytics(self, story_id: int) -> Optional[StoryAnalytics]:
        """Get analytics for a story, generating if needed."""
        analytics = (
            self.db.query(StoryAnalytics)
            .filter(StoryAnalytics.story_version_id == story_id)
            .first()
        )

        if not analytics:
            # Generate analytics
            story = self.db.query(StoryVersion).filter(StoryVersion.id == story_id).first()
            if story:
                analytics = self.analyze_story(story)

        return analytics

    def get_timeline_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get events from recent stories for timeline visualization."""
        recent_analytics = (
            self.db.query(StoryAnalytics)
            .order_by(StoryAnalytics.created_at.desc())
            .limit(limit)
            .all()
        )

        all_events = []
        for analytics in recent_analytics:
            if analytics.events:
                for event in analytics.events:
                    event["story_id"] = analytics.story_version_id
                    event["story_created_at"] = analytics.created_at.isoformat()
                    all_events.append(event)

        # Sort by importance and recency
        all_events.sort(key=lambda e: (e.get("importance", 0), e.get("story_created_at", "")), reverse=True)

        return all_events[:100]  # Return top 100 events
