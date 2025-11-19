"""Main FastAPI application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api import router as api_router
from .ws import websocket_endpoint
from .scheduler import get_scheduler
from .database import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.singl_log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Singl News Backend")

    # Initialize database
    logger.info("Initializing database")
    init_db()

    # Start scheduler
    logger.info("Starting story update scheduler")
    scheduler = get_scheduler()
    scheduler.start()

    logger.info("Singl News Backend started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Singl News Backend")
    scheduler.shutdown()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Backend for Singl News - The world's only unified continuous news story",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.singl_ws_origin == "*" else [settings.singl_ws_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)


# WebSocket endpoint
@app.websocket("/ws/story")
async def websocket_story_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time story updates."""
    await websocket_endpoint(websocket)


# Root endpoint
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": "Singl News Backend",
        "version": "1.0.0",
        "status": "operational",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.singl_log_level.lower(),
    )
