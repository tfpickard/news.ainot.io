"""Configuration management for Singl News backend."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+psycopg2://singl:singl@db:5432/singl"

    # OpenAI
    openai_api_key: str
    singl_model_name: str = "gpt-4-turbo-preview"

    # Scheduler
    singl_update_minutes: int = 30
    singl_context_steps: int = 10

    # RSS Feeds - default major news sources
    singl_feeds: str = (
        "http://rss.cnn.com/rss/cnn_topstories.rss,"
        "http://feeds.bbci.co.uk/news/world/rss.xml,"
        "https://www.theguardian.com/world/rss,"
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml,"
        "http://feeds.reuters.com/reuters/topNews,"
        "https://www.aljazeera.com/xml/rss/all.xml"
    )

    # Logging
    singl_log_level: str = "INFO"

    # WebSocket
    singl_ws_origin: str = "*"

    # App
    app_name: str = "Singl News Backend"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_feed_list(self) -> List[str]:
        """Parse comma-separated feed URLs into a list."""
        return [feed.strip() for feed in self.singl_feeds.split(",") if feed.strip()]


# Global settings instance
settings = Settings()
