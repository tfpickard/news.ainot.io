"""REST API endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from .database import get_db
from .story_service import StoryService
from .quote_service import QuoteExtractor
from .image_service import QuoteImageGenerator
from .models import FeedItem, FeedConfiguration, StoryVersion
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
    FeedConfigurationResponse,
    FeedConfigurationCreate,
    FeedConfigurationUpdate,
    LoginRequest,
    LoginResponse,
)
from .config import settings
from .auth import require_auth, get_admin_api_key

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


@router.get("/story/{story_id}/quote-image")
def get_quote_image(
    story_id: int,
    quote_index: int = 0,
    db: Session = Depends(get_db)
):
    """
    Generate a shareable quote card image.

    Args:
        story_id: Story version ID
        quote_index: Index of the quote to generate image for (0-based, default 0)

    Returns:
        PNG image of the quote card
    """
    service = StoryService(db)
    story = service.get_story_by_id(story_id)

    if not story:
        raise HTTPException(status_code=404, detail=f"Story {story_id} not found")

    # Extract quotes
    extractor = QuoteExtractor()
    quotes = extractor.extract_quotes(story.full_text, count=10)

    if not quotes or quote_index >= len(quotes):
        raise HTTPException(
            status_code=404,
            detail=f"Quote index {quote_index} not found (story has {len(quotes)} quotes)"
        )

    quote = quotes[quote_index]

    # Generate image
    generator = QuoteImageGenerator()
    image_bytes = generator.generate_quote_image(
        quote_text=quote['text'],
        category=quote['category'],
        absurdity_score=quote['absurdity_score']
    )

    return StreamingResponse(
        image_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename=singl_quote_{story_id}_{quote_index}.png"
        }
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


# Admin authentication endpoints

@router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Exchange password for API key.

    Args:
        request: Login request with password

    Returns:
        API key if password is correct
    """
    import os
    admin_password = os.getenv('SINGL_ADMIN_PASSWORD', 'singl2025')

    if request.password != admin_password:
        raise HTTPException(status_code=401, detail="Invalid password")

    return LoginResponse(
        api_key=get_admin_api_key(),
        message="Store this key securely. Use it in Authorization: Bearer {key} header."
    )


@router.post("/auth/verify")
async def verify_auth(auth: str = Depends(require_auth)):
    """Verify authentication credentials."""
    return {"authenticated": True, "message": "Valid credentials"}


@router.get("/auth/key")
async def get_api_key_info(auth: str = Depends(require_auth)):
    """Get API key information (for already authenticated users)."""
    return {
        "key": get_admin_api_key(),
        "message": "Store this key securely. It will not be shown again."
    }


# Feed Configuration Management Endpoints (Protected)

@router.get("/feeds", response_model=List[FeedConfigurationResponse])
def get_feeds(
    active_only: bool = False,
    db: Session = Depends(get_db),
    auth: str = Depends(require_auth)
):
    """
    Get all configured RSS feeds.

    Args:
        active_only: If True, only return active feeds
    """
    query = db.query(FeedConfiguration)

    if active_only:
        query = query.filter(FeedConfiguration.is_active == True)

    feeds = query.order_by(FeedConfiguration.priority.desc(), FeedConfiguration.name).all()
    return feeds


@router.get("/feeds/{feed_id}", response_model=FeedConfigurationResponse)
def get_feed(feed_id: int, db: Session = Depends(get_db), auth: str = Depends(require_auth)):
    """Get a specific feed configuration by ID."""
    feed = db.query(FeedConfiguration).filter(FeedConfiguration.id == feed_id).first()

    if not feed:
        raise HTTPException(status_code=404, detail=f"Feed {feed_id} not found")

    return feed


@router.post("/feeds", response_model=FeedConfigurationResponse)
def create_feed(feed: FeedConfigurationCreate, db: Session = Depends(get_db), auth: str = Depends(require_auth)):
    """Create a new feed configuration."""
    # Check if URL already exists
    existing = db.query(FeedConfiguration).filter(FeedConfiguration.url == feed.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Feed URL already exists")

    db_feed = FeedConfiguration(**feed.dict())
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)

    logger.info(f"Created new feed: {db_feed.name} ({db_feed.url})")
    return db_feed


@router.put("/feeds/{feed_id}", response_model=FeedConfigurationResponse)
def update_feed(
    feed_id: int,
    feed_update: FeedConfigurationUpdate,
    db: Session = Depends(get_db),
    auth: str = Depends(require_auth)
):
    """Update an existing feed configuration."""
    db_feed = db.query(FeedConfiguration).filter(FeedConfiguration.id == feed_id).first()

    if not db_feed:
        raise HTTPException(status_code=404, detail=f"Feed {feed_id} not found")

    # Update only provided fields
    update_data = feed_update.dict(exclude_unset=True)

    # Check if URL is being changed and if it conflicts
    if "url" in update_data and update_data["url"] != db_feed.url:
        existing = db.query(FeedConfiguration).filter(
            FeedConfiguration.url == update_data["url"],
            FeedConfiguration.id != feed_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Feed URL already exists")

    for key, value in update_data.items():
        setattr(db_feed, key, value)

    db.commit()
    db.refresh(db_feed)

    logger.info(f"Updated feed: {db_feed.name} ({db_feed.id})")
    return db_feed


@router.delete("/feeds/{feed_id}")
def delete_feed(feed_id: int, db: Session = Depends(get_db), auth: str = Depends(require_auth)):
    """Delete a feed configuration."""
    db_feed = db.query(FeedConfiguration).filter(FeedConfiguration.id == feed_id).first()

    if not db_feed:
        raise HTTPException(status_code=404, detail=f"Feed {feed_id} not found")

    feed_name = db_feed.name
    db.delete(db_feed)
    db.commit()

    logger.info(f"Deleted feed: {feed_name} ({feed_id})")
    return {"message": f"Feed {feed_id} deleted successfully"}


@router.post("/feeds/import-defaults")
def import_default_feeds(db: Session = Depends(get_db), auth: str = Depends(require_auth)):
    """Import default feeds from config into database."""
    from .config import settings

    feed_urls = settings.get_feed_list()
    imported = 0
    skipped = 0

    for url in feed_urls:
        # Check if already exists
        existing = db.query(FeedConfiguration).filter(FeedConfiguration.url == url).first()
        if existing:
            skipped += 1
            continue

        # Extract name from URL
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        name = domain.split('.')[0].title() if domain else url

        # Create feed
        feed = FeedConfiguration(
            name=name,
            url=url,
            is_active=True,
            priority=0
        )
        db.add(feed)
        imported += 1

    db.commit()

    logger.info(f"Imported {imported} default feeds, skipped {skipped} existing")
    return {
        "imported": imported,
        "skipped": skipped,
        "total": len(feed_urls)
    }


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), auth: str = Depends(require_auth)):
    """Get comprehensive statistics about THE STORY."""
    from sqlalchemy import func, distinct
    from datetime import datetime, timedelta, timezone

    service = StoryService(db)

    # Story statistics
    total_stories = service.get_story_count()
    latest_story = service.get_latest_story()

    # Time-based story stats
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    stories_today = db.query(StoryVersion).filter(StoryVersion.created_at >= today_start).count()
    stories_this_week = db.query(StoryVersion).filter(StoryVersion.created_at >= week_start).count()
    stories_this_month = db.query(StoryVersion).filter(StoryVersion.created_at >= month_start).count()

    # Feed statistics
    total_feeds = db.query(FeedConfiguration).count()
    active_feeds = db.query(FeedConfiguration).filter(FeedConfiguration.is_active == True).count()
    feeds_with_errors = db.query(FeedConfiguration).filter(FeedConfiguration.fetch_error.isnot(None)).count()

    # Feed item statistics
    total_feed_items = db.query(FeedItem).count()
    feed_items_today = db.query(FeedItem).filter(FeedItem.fetched_at >= today_start).count()
    feed_items_this_week = db.query(FeedItem).filter(FeedItem.fetched_at >= week_start).count()

    # Unique sources
    unique_sources = db.query(func.count(distinct(FeedItem.feed_name))).scalar()

    # Token usage statistics (from story versions)
    total_tokens = 0
    total_cost = 0.0  # Rough estimate
    story_versions = db.query(StoryVersion).all()
    for story in story_versions:
        if story.token_stats and 'total_tokens' in story.token_stats:
            total_tokens += story.token_stats['total_tokens']
            # Rough cost estimate: $0.01 per 1K tokens for GPT-4
            total_cost += (story.token_stats['total_tokens'] / 1000) * 0.01

    # Average story length
    avg_story_length = db.query(func.avg(func.length(StoryVersion.full_text))).scalar() or 0

    # Most active feeds (by item count)
    top_feeds = (
        db.query(
            FeedItem.feed_name,
            func.count(FeedItem.id).label('count')
        )
        .group_by(FeedItem.feed_name)
        .order_by(func.count(FeedItem.id).desc())
        .limit(10)
        .all()
    )

    # Recent story generation rate
    if total_stories > 1:
        first_story = db.query(StoryVersion).order_by(StoryVersion.created_at.asc()).first()
        time_span = (latest_story.created_at - first_story.created_at).total_seconds()
        stories_per_hour = (total_stories / time_span) * 3600 if time_span > 0 else 0
    else:
        stories_per_hour = 0

    return {
        "stories": {
            "total": total_stories,
            "today": stories_today,
            "this_week": stories_this_week,
            "this_month": stories_this_month,
            "per_hour": round(stories_per_hour, 2),
            "latest_at": latest_story.created_at.isoformat() if latest_story else None,
            "avg_length": int(avg_story_length)
        },
        "feeds": {
            "total": total_feeds,
            "active": active_feeds,
            "inactive": total_feeds - active_feeds,
            "with_errors": feeds_with_errors,
            "unique_sources": unique_sources
        },
        "feed_items": {
            "total": total_feed_items,
            "today": feed_items_today,
            "this_week": feed_items_this_week,
            "avg_per_story": round(total_feed_items / total_stories, 1) if total_stories > 0 else 0
        },
        "ai_usage": {
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(total_cost, 2),
            "avg_tokens_per_story": round(total_tokens / total_stories) if total_stories > 0 else 0
        },
        "top_feeds": [
            {"name": feed[0], "item_count": feed[1]}
            for feed in top_feeds
        ]
    }
