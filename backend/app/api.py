"""REST API endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import get_db
from .story_service import StoryService
from .quote_service import QuoteExtractor
from .models import FeedItem
from .schemas import (
    StoryVersionResponse,
    StoryVersionSummary,
    MetaResponse,
    HealthResponse,
    QuotesResponse,
    QuoteResponse,
    SourcesResponse,
    SourceDetail,
    SEOMetadata,
    APIDocumentation,
)
from .config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/story/current", response_model=StoryVersionResponse)
def get_current_story(db: Session = Depends(get_db)):
    """Get the latest story version."""
    service = StoryService(db)
    story = service.get_latest_story()

    if not story:
        raise HTTPException(status_code=404, detail="No stories available yet")

    return story


@router.get("/story/history", response_model=List[StoryVersionSummary])
def get_story_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Get paginated story history.

    Args:
        limit: Number of stories to return (max 100)
        offset: Number of stories to skip
    """
    # Enforce max limit
    limit = min(limit, 100)

    service = StoryService(db)
    stories = service.get_story_history(limit=limit, offset=offset)

    # Convert to summary format
    summaries = []
    for story in stories:
        preview = story.full_text[:200]
        if len(story.full_text) > 200:
            preview += "..."

        summaries.append(
            StoryVersionSummary(
                id=story.id,
                created_at=story.created_at,
                summary=story.summary,
                preview=preview,
            )
        )

    return summaries


@router.get("/story/{story_id}", response_model=StoryVersionResponse)
def get_story_by_id(story_id: int, db: Session = Depends(get_db)):
    """Get a specific story version by ID."""
    service = StoryService(db)
    story = service.get_story_by_id(story_id)

    if not story:
        raise HTTPException(status_code=404, detail=f"Story {story_id} not found")

    return story


@router.get("/meta", response_model=MetaResponse)
def get_meta(db: Session = Depends(get_db)):
    """Get metadata about the service."""
    service = StoryService(db)

    latest_story = service.get_latest_story()
    story_count = service.get_story_count()

    feed_urls = settings.get_feed_list()

    return MetaResponse(
        feed_urls=feed_urls,
        feed_count=len(feed_urls),
        update_minutes=settings.singl_update_minutes,
        context_steps=settings.singl_context_steps,
        last_update=latest_story.created_at if latest_story else None,
        story_count=story_count,
        model_name=settings.singl_model_name,
    )


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        service = StoryService(db)
        latest_story = service.get_latest_story()
        story_count = service.get_story_count()

        return HealthResponse(
            status="healthy",
            database_connected=True,
            last_story_at=latest_story.created_at if latest_story else None,
            story_count=story_count,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            database_connected=False,
            last_story_at=None,
            story_count=0,
        )


@router.get("/story/{story_id}/quotes", response_model=QuotesResponse)
def get_story_quotes(story_id: int, count: int = 5, db: Session = Depends(get_db)):
    """
    Get shareable quotes from a specific story.

    Args:
        story_id: Story version ID
        count: Number of quotes to extract (default 5, max 10)
    """
    service = StoryService(db)
    story = service.get_story_by_id(story_id)

    if not story:
        raise HTTPException(status_code=404, detail=f"Story {story_id} not found")

    # Limit count
    count = min(count, 10)

    extractor = QuoteExtractor()
    quotes = extractor.extract_quotes(story.full_text, count=count)

    return QuotesResponse(
        story_id=story_id,
        quotes=[QuoteResponse(**q) for q in quotes]
    )


@router.get("/story/{story_id}/sources", response_model=SourcesResponse)
def get_story_sources(story_id: int, db: Session = Depends(get_db)):
    """
    Get detailed source information for a specific story.

    Args:
        story_id: Story version ID
    """
    service = StoryService(db)
    story = service.get_story_by_id(story_id)

    if not story:
        raise HTTPException(status_code=404, detail=f"Story {story_id} not found")

    if not story.sources_snapshot or "feed_items" not in story.sources_snapshot:
        return SourcesResponse(
            story_id=story_id,
            item_count=0,
            sources=[]
        )

    # Get full details for each source from the database
    source_details = []
    for item_data in story.sources_snapshot["feed_items"]:
        # Try to get full feed item from database for link
        feed_item = db.query(FeedItem).filter(FeedItem.id == item_data["id"]).first()

        source_details.append(SourceDetail(
            id=item_data["id"],
            title=item_data["title"],
            source=item_data["source"],
            published_at=item_data.get("published_at"),
            link=feed_item.link if feed_item else None
        ))

    return SourcesResponse(
        story_id=story_id,
        item_count=len(source_details),
        sources=source_details
    )


@router.get("/story/{story_id}/seo", response_model=SEOMetadata)
def get_story_seo(story_id: int, db: Session = Depends(get_db)):
    """
    Get SEO metadata for a specific story.

    Args:
        story_id: Story version ID
    """
    service = StoryService(db)
    story = service.get_story_by_id(story_id)

    if not story:
        raise HTTPException(status_code=404, detail=f"Story {story_id} not found")

    # Extract keywords from summary
    import re
    words = re.findall(r'\b[A-Z][a-z]+\b', story.summary)
    keywords = list(set(words))[:10]  # Unique capitalized words as keywords

    # Add some standard keywords
    keywords.extend(["Singl News", "unified news", "continuous narrative", "news synthesis"])

    # Create description from first part of story
    description = story.full_text[:200]
    if len(story.full_text) > 200:
        description += "..."

    return SEOMetadata(
        title=f"{story.summary} - Singl News",
        description=description,
        keywords=keywords,
        og_title=story.summary,
        og_description=description,
        og_type="article",
        twitter_card="summary_large_image"
    )


@router.get("/docs", response_model=APIDocumentation)
def get_api_docs():
    """Get API documentation."""
    return APIDocumentation(
        version="1.0.0",
        endpoints=[
            {
                "method": "GET",
                "path": "/api/story/current",
                "description": "Get the latest story version",
                "response": "StoryVersionResponse"
            },
            {
                "method": "GET",
                "path": "/api/story/history",
                "description": "Get paginated story history",
                "params": ["limit (max 100)", "offset"],
                "response": "List[StoryVersionSummary]"
            },
            {
                "method": "GET",
                "path": "/api/story/{story_id}",
                "description": "Get a specific story version",
                "response": "StoryVersionResponse"
            },
            {
                "method": "GET",
                "path": "/api/story/{story_id}/quotes",
                "description": "Get shareable quotes from a story",
                "params": ["count (max 10)"],
                "response": "QuotesResponse"
            },
            {
                "method": "GET",
                "path": "/api/story/{story_id}/sources",
                "description": "Get detailed source information",
                "response": "SourcesResponse"
            },
            {
                "method": "GET",
                "path": "/api/story/{story_id}/seo",
                "description": "Get SEO metadata for a story",
                "response": "SEOMetadata"
            },
            {
                "method": "GET",
                "path": "/api/meta",
                "description": "Get service metadata",
                "response": "MetaResponse"
            },
            {
                "method": "GET",
                "path": "/api/health",
                "description": "Health check endpoint",
                "response": "HealthResponse"
            },
            {
                "method": "GET",
                "path": "/api/docs",
                "description": "Get this API documentation",
                "response": "APIDocumentation"
            }
        ],
        examples=[
            {
                "name": "Get current story",
                "request": "GET /api/story/current",
                "description": "Fetch the latest version of THE STORY"
            },
            {
                "name": "Get shareable quotes",
                "request": "GET /api/story/123/quotes?count=5",
                "description": "Extract 5 absurd quotes from story #123"
            },
            {
                "name": "Get story sources",
                "request": "GET /api/story/123/sources",
                "description": "Get all news sources that contributed to story #123"
            }
        ],
        rate_limits={
            "default": "100 requests per minute",
            "burst": "200 requests per minute",
            "attribution": "Please include 'Powered by Singl News' when using this API"
        }
    )
