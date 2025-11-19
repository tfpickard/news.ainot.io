"""REST API endpoints."""
import logging
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from .database import get_db
from .story_service import StoryService
from .schemas import (
    StoryVersionResponse,
    StoryVersionSummary,
    MetaResponse,
    HealthResponse,
    GeneratedImageResponse,
    StatsResponse,
    ControlPanelAuthRequest,
    ControlPanelAuthResponse,
    ConfigUpdateRequest,
    ConfigResponse,
)
from .config import settings
from .models import GeneratedImage, StoryVersion, FeedItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# Simple in-memory token store (in production, use Redis or similar)
_active_tokens = {}
_app_start_time = datetime.now()

security = HTTPBearer()


def create_auth_token() -> str:
    """Create a new authentication token."""
    token = secrets.token_urlsafe(32)
    _active_tokens[token] = datetime.now() + timedelta(hours=24)
    return token


def verify_auth_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Verify authentication token."""
    token = credentials.credentials
    if token not in _active_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Check if token is expired
    if datetime.now() > _active_tokens[token]:
        del _active_tokens[token]
        raise HTTPException(status_code=401, detail="Token expired")

    return True


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


# ============================================================================
# Image Endpoints
# ============================================================================

@router.get("/images/latest", response_model=Optional[GeneratedImageResponse])
def get_latest_image(db: Session = Depends(get_db)):
    """Get the most recent generated image."""
    image = db.query(GeneratedImage).order_by(GeneratedImage.created_at.desc()).first()
    return image


@router.get("/images", response_model=List[GeneratedImageResponse])
def get_images(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Get paginated list of generated images.

    Args:
        limit: Number of images to return (max 100)
        offset: Number of images to skip
    """
    limit = min(limit, 100)
    images = (
        db.query(GeneratedImage)
        .order_by(GeneratedImage.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return images


@router.get("/images/{image_id}", response_model=GeneratedImageResponse)
def get_image_by_id(image_id: int, db: Session = Depends(get_db)):
    """Get a specific generated image by ID."""
    image = db.query(GeneratedImage).filter(GeneratedImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found")
    return image


@router.get("/story/{story_id}/image", response_model=Optional[GeneratedImageResponse])
def get_image_by_story(story_id: int, db: Session = Depends(get_db)):
    """Get the generated image for a specific story version."""
    image = (
        db.query(GeneratedImage)
        .filter(GeneratedImage.story_version_id == story_id)
        .first()
    )
    return image


# ============================================================================
# Stats Endpoint (Public)
# ============================================================================

@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Get public statistics about the service."""
    # Total counts
    total_stories = db.query(func.count(StoryVersion.id)).scalar()
    total_images = db.query(func.count(GeneratedImage.id)).scalar()
    total_feed_items = db.query(func.count(FeedItem.id)).scalar()

    # Latest timestamps
    latest_story = db.query(StoryVersion).order_by(StoryVersion.created_at.desc()).first()
    latest_image = db.query(GeneratedImage).order_by(GeneratedImage.created_at.desc()).first()

    # Last 24 hours counts
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    stories_last_24h = (
        db.query(func.count(StoryVersion.id))
        .filter(StoryVersion.created_at >= twenty_four_hours_ago)
        .scalar()
    )
    images_last_24h = (
        db.query(func.count(GeneratedImage.id))
        .filter(GeneratedImage.created_at >= twenty_four_hours_ago)
        .scalar()
    )

    # Uptime
    uptime_hours = (datetime.now() - _app_start_time).total_seconds() / 3600

    return StatsResponse(
        total_stories=total_stories,
        total_images=total_images,
        total_feed_items=total_feed_items,
        latest_story_at=latest_story.created_at if latest_story else None,
        latest_image_at=latest_image.created_at if latest_image else None,
        update_frequency_minutes=settings.singl_update_minutes,
        feeds_count=len(settings.get_feed_list()),
        model_name=settings.singl_model_name,
        uptime_hours=uptime_hours,
        stories_last_24h=stories_last_24h,
        images_last_24h=images_last_24h,
    )


# ============================================================================
# Control Panel Endpoints (Protected)
# ============================================================================

@router.post("/control-panel/auth", response_model=ControlPanelAuthResponse)
def authenticate_control_panel(auth_request: ControlPanelAuthRequest):
    """Authenticate for control panel access."""
    if auth_request.password == settings.singl_admin_password:
        token = create_auth_token()
        return ControlPanelAuthResponse(
            success=True,
            message="Authentication successful",
            token=token,
        )
    else:
        return ControlPanelAuthResponse(
            success=False,
            message="Invalid password",
        )


@router.get("/control-panel/config", response_model=ConfigResponse)
def get_config(authenticated: bool = Depends(verify_auth_token)):
    """Get current configuration (requires authentication)."""
    return ConfigResponse(
        singl_model_name=settings.singl_model_name,
        singl_update_minutes=settings.singl_update_minutes,
        singl_context_steps=settings.singl_context_steps,
        singl_temperature=settings.singl_temperature,
        singl_max_tokens=settings.singl_max_tokens,
        singl_image_generation_enabled=settings.singl_image_generation_enabled,
        singl_image_generation_interval=settings.singl_image_generation_interval,
        singl_image_model=settings.singl_image_model,
        singl_image_size=settings.singl_image_size,
        singl_image_quality=settings.singl_image_quality,
        feed_count=len(settings.get_feed_list()),
    )


@router.post("/control-panel/config", response_model=ConfigResponse)
def update_config(
    config_update: ConfigUpdateRequest,
    authenticated: bool = Depends(verify_auth_token),
):
    """Update configuration (requires authentication)."""
    # Update settings dynamically
    # Note: These changes are in-memory only and will reset on restart
    # For persistent changes, you would need to update the .env file

    if config_update.singl_model_name is not None:
        settings.singl_model_name = config_update.singl_model_name

    if config_update.singl_update_minutes is not None:
        settings.singl_update_minutes = config_update.singl_update_minutes

    if config_update.singl_context_steps is not None:
        settings.singl_context_steps = config_update.singl_context_steps

    if config_update.singl_temperature is not None:
        settings.singl_temperature = config_update.singl_temperature

    if config_update.singl_max_tokens is not None:
        settings.singl_max_tokens = config_update.singl_max_tokens

    if config_update.singl_image_generation_enabled is not None:
        settings.singl_image_generation_enabled = config_update.singl_image_generation_enabled

    if config_update.singl_image_generation_interval is not None:
        settings.singl_image_generation_interval = config_update.singl_image_generation_interval

    if config_update.singl_image_model is not None:
        settings.singl_image_model = config_update.singl_image_model

    if config_update.singl_image_size is not None:
        settings.singl_image_size = config_update.singl_image_size

    if config_update.singl_image_quality is not None:
        settings.singl_image_quality = config_update.singl_image_quality

    if config_update.singl_feeds is not None:
        settings.singl_feeds = config_update.singl_feeds

    logger.info("Configuration updated via control panel")

    return ConfigResponse(
        singl_model_name=settings.singl_model_name,
        singl_update_minutes=settings.singl_update_minutes,
        singl_context_steps=settings.singl_context_steps,
        singl_temperature=settings.singl_temperature,
        singl_max_tokens=settings.singl_max_tokens,
        singl_image_generation_enabled=settings.singl_image_generation_enabled,
        singl_image_generation_interval=settings.singl_image_generation_interval,
        singl_image_model=settings.singl_image_model,
        singl_image_size=settings.singl_image_size,
        singl_image_quality=settings.singl_image_quality,
        feed_count=len(settings.get_feed_list()),
    )
