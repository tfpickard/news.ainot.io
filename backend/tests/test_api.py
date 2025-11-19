"""Tests for REST API endpoints."""
import pytest
from datetime import datetime, timezone

from app.models import StoryVersion, FeedItem


def test_root_endpoint(client):
    """Test root endpoint returns service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Singl News Backend"
    assert "version" in data


def test_health_endpoint_empty_db(client):
    """Test health endpoint with empty database."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["database_connected"] is True
    assert data["story_count"] == 0


def test_get_current_story_not_found(client):
    """Test getting current story when none exists."""
    response = client.get("/api/story/current")
    assert response.status_code == 404


def test_get_current_story(client, test_db):
    """Test getting current story."""
    # Create a story version
    story = StoryVersion(
        full_text="This is the test story.",
        summary="Test story summary",
        context_summary="Test context",
        sources_snapshot={"items": []},
        token_stats={"total": 100}
    )
    test_db.add(story)
    test_db.commit()
    test_db.refresh(story)

    response = client.get("/api/story/current")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == story.id
    assert data["full_text"] == "This is the test story."
    assert data["summary"] == "Test story summary"


def test_get_story_by_id(client, test_db):
    """Test getting specific story by ID."""
    story = StoryVersion(
        full_text="Story by ID test.",
        summary="ID test summary"
    )
    test_db.add(story)
    test_db.commit()
    test_db.refresh(story)

    response = client.get(f"/api/story/{story.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == story.id
    assert data["full_text"] == "Story by ID test."


def test_get_story_by_id_not_found(client):
    """Test getting non-existent story."""
    response = client.get("/api/story/9999")
    assert response.status_code == 404


def test_get_story_history(client, test_db):
    """Test getting story history."""
    # Create multiple stories
    for i in range(5):
        story = StoryVersion(
            full_text=f"Story {i}",
            summary=f"Summary {i}"
        )
        test_db.add(story)
    test_db.commit()

    response = client.get("/api/story/history?limit=3&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all("preview" in item for item in data)


def test_get_meta(client, test_db):
    """Test meta endpoint."""
    # Add a story
    story = StoryVersion(
        full_text="Meta test",
        summary="Meta summary"
    )
    test_db.add(story)
    test_db.commit()

    response = client.get("/api/meta")
    assert response.status_code == 200
    data = response.json()
    assert "feed_urls" in data
    assert "update_minutes" in data
    assert "story_count" in data
    assert data["story_count"] == 1
