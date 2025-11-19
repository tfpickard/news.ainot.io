"""WebSocket support for real-time story updates."""
import logging
import asyncio
import json
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from .database import SessionLocal
from .story_service import StoryService
from .schemas import StoryVersionResponse, WebSocketMessage

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_story_update(self, story_version: StoryVersionResponse):
        """Broadcast a new story version to all clients."""
        message = {
            "type": "update",
            "story": {
                "id": story_version.id,
                "created_at": story_version.created_at.isoformat(),
                "full_text": story_version.full_text,
                "summary": story_version.summary,
                "sources_snapshot": story_version.sources_snapshot,
                "token_stats": story_version.token_stats,
            },
        }

        await self.broadcast(message)
        logger.info(f"Broadcasted story update {story_version.id} to {len(self.active_connections)} clients")


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for story updates."""
    await manager.connect(websocket)

    # Send initial story
    db = SessionLocal()
    try:
        service = StoryService(db)
        latest_story = service.get_latest_story()

        if latest_story:
            initial_message = {
                "type": "initial",
                "story": {
                    "id": latest_story.id,
                    "created_at": latest_story.created_at.isoformat(),
                    "full_text": latest_story.full_text,
                    "summary": latest_story.summary,
                    "sources_snapshot": latest_story.sources_snapshot,
                    "token_stats": latest_story.token_stats,
                },
            }
            await manager.send_personal_message(initial_message, websocket)
        else:
            # No stories yet
            await manager.send_personal_message(
                {
                    "type": "initial",
                    "story": None,
                    "message": "No stories available yet. The first story is being generated.",
                },
                websocket,
            )

    except Exception as e:
        logger.error(f"Error sending initial story: {e}")
    finally:
        db.close()

    # Keep connection alive and listen for client messages (if any)
    try:
        while True:
            # We don't expect client messages, but keep connection alive
            data = await websocket.receive_text()
            # Could add ping/pong or other client commands here if needed

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    return manager
