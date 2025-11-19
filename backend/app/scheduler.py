"""Background scheduler for periodic story updates."""
import logging
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .database import SessionLocal
from .story_service import StoryService
from .config import settings
from .ws import get_connection_manager
from .schemas import StoryVersionResponse
from .openai_client import ImageGenerator
from .models import GeneratedImage

logger = logging.getLogger(__name__)


class StoryUpdateScheduler:
    """Manages periodic story generation updates."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    async def run_update_job(self):
        """
        Run a single update cycle: ingest feeds and generate new story.

        This is the core periodic task.
        """
        if self.is_running:
            logger.warning("Update job already running, skipping this cycle")
            return

        self.is_running = True
        start_time = datetime.now()

        logger.info("=" * 80)
        logger.info("Starting scheduled story update")
        logger.info("=" * 80)

        db = SessionLocal()

        try:
            service = StoryService(db)

            # Step 1: Ingest RSS feeds
            logger.info("Step 1: Ingesting RSS feeds")
            new_items = service.ingest_feeds()
            logger.info(f"Ingested {new_items} new feed items")

            # Step 2: Generate new story version
            logger.info("Step 2: Generating new story version")
            new_story = service.generate_next_story_version()

            if new_story:
                logger.info(f"Successfully generated story version {new_story.id}")

                # Step 3: Check if we should generate an image
                if settings.singl_image_generation_enabled:
                    story_count = service.get_story_count()
                    if story_count % settings.singl_image_generation_interval == 0:
                        logger.info("Step 3a: Generating AI image for story")
                        try:
                            image_gen = ImageGenerator()
                            image_data = image_gen.generate_image_from_story(
                                new_story.full_text,
                                new_story.summary
                            )

                            # Save image to database
                            generated_image = GeneratedImage(
                                story_version_id=new_story.id,
                                prompt=image_data["prompt"],
                                image_url=image_data["image_url"],
                                revised_prompt=image_data.get("revised_prompt"),
                                model=settings.singl_image_model,
                                size=settings.singl_image_size,
                                quality=settings.singl_image_quality,
                            )
                            db.add(generated_image)
                            db.commit()
                            logger.info(f"Image saved with ID {generated_image.id}")
                        except Exception as e:
                            logger.error(f"Error generating image: {e}", exc_info=True)

                # Step 4: Broadcast to WebSocket clients
                logger.info("Step 4: Broadcasting to WebSocket clients")
                manager = get_connection_manager()

                # Convert to response schema
                story_response = StoryVersionResponse(
                    id=new_story.id,
                    created_at=new_story.created_at,
                    full_text=new_story.full_text,
                    summary=new_story.summary,
                    context_summary=new_story.context_summary,
                    sources_snapshot=new_story.sources_snapshot,
                    token_stats=new_story.token_stats,
                )

                await manager.broadcast_story_update(story_response)
                logger.info("Broadcast complete")
            else:
                logger.warning("Story generation failed")

        except Exception as e:
            logger.error(f"Error in update job: {e}", exc_info=True)

        finally:
            db.close()
            self.is_running = False

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Update job completed in {duration:.2f} seconds")
            logger.info("=" * 80)

    def start(self):
        """Start the scheduler."""
        logger.info(f"Starting scheduler with {settings.singl_update_minutes} minute intervals")

        # Add job with interval trigger
        self.scheduler.add_job(
            self.run_update_job,
            trigger=IntervalTrigger(minutes=settings.singl_update_minutes),
            id="story_update",
            name="Generate story update",
            replace_existing=True,
        )

        # Run immediately on startup (after a short delay)
        self.scheduler.add_job(
            self.run_update_job,
            trigger="date",
            run_date=None,  # Run immediately
            id="initial_update",
            name="Initial story generation",
        )

        self.scheduler.start()
        logger.info("Scheduler started successfully")

    def shutdown(self):
        """Shutdown the scheduler."""
        logger.info("Shutting down scheduler")
        self.scheduler.shutdown()


# Global scheduler instance
_scheduler = None


def get_scheduler() -> StoryUpdateScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = StoryUpdateScheduler()
    return _scheduler
