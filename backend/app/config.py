"""Configuration management for UnioNews backend."""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
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

    # RSS Feeds - diverse sources for erratic story generation
    singl_feeds: str = (
        # Major World News
        "http://rss.cnn.com/rss/cnn_topstories.rss,"
        "http://feeds.bbci.co.uk/news/world/rss.xml,"
        "https://www.theguardian.com/world/rss,"
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml,"
        "http://feeds.reuters.com/reuters/topNews,"
        "https://www.aljazeera.com/xml/rss/all.xml,"
        # Technology & Science
        "https://techcrunch.com/feed/,"
        "http://feeds.arstechnica.com/arstechnica/index.xml,"
        "https://www.wired.com/feed/rss,"
        "https://www.sciencedaily.com/rss/all.xml,"
        "https://phys.org/rss-feed/,"
        "https://www.theverge.com/rss/index.xml,"
        # Business & Finance
        "https://feeds.a.dj.com/rss/RSSWorldNews.xml,"
        "https://www.ft.com/rss/home,"
        "https://www.economist.com/the-world-this-week/rss.xml,"
        # Entertainment & Culture
        "https://variety.com/feed/,"
        "https://www.rollingstone.com/feed/,"
        "https://www.theonion.com/rss,"
        # Sports
        "http://www.espn.com/espn/rss/news,"
        "http://feeds.bbci.co.uk/sport/rss.xml,"
        # Health & Wellness
        "https://www.medicalnewstoday.com/rss,"
        "https://www.healthline.com/rss,"
        # Environment & Climate
        "https://grist.org/feed/,"
        "https://www.treehugger.com/feeds/rss,"
        # Weird & Unusual
        "https://boingboing.net/feed,"
        "https://www.vice.com/en/rss,"
        # International Perspectives
        "https://www.scmp.com/rss/91/feed,"
        "https://www.rt.com/rss,"
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms,"
        # Arts & Books
        "https://www.artforum.com/rss.xml,"
        "https://lithub.com/feed/"
    )

    # Logging
    singl_log_level: str = "INFO"

    # WebSocket
    singl_ws_origin: str = "*"

    # Control Panel
    singl_admin_password: str = "singl2025"

    # Image Generation
    singl_image_generation_enabled: bool = True
    singl_image_generation_interval: int = 5
    singl_image_model: str = "dall-e-3"
    singl_image_size: str = "1024x1024"
    singl_image_quality: str = "standard"

    # Fine-tuning Controls
    singl_temperature: float = 0.8  # Only used for non-GPT-5 models
    singl_max_tokens: int = 4000

    # GPT-5 specific parameters (not supported by other models)
    singl_reasoning_effort: str = "low"  # minimal, low, medium, high
    singl_text_verbosity: str = "medium"  # low, medium, high

    # App
    app_name: str = "UnioNews Backend"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def get_feed_list(self) -> List[str]:
        """Parse comma-separated feed URLs into a list."""
        return [feed.strip() for feed in self.singl_feeds.split(",") if feed.strip()]


# Global settings instance
settings = Settings()

# Debug logging for configuration (only shows on startup)
print("=" * 80)
print("🔧 UNIONEWS CONFIGURATION LOADED")
print("=" * 80)
print(f"📊 Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'configured'}")
print(f"🤖 OpenAI Key: {'✓ SET (' + settings.openai_api_key[-4:] + ')' if settings.openai_api_key else '✗ NOT SET'}")
print(f"🎨 Model: {settings.singl_model_name}")
print(f"⏱️  Update Interval: {settings.singl_update_minutes} minutes")
print(f"🔐 Admin Password: {'✓ SET' if settings.singl_admin_password else '✗ NOT SET'}")
print(f"📡 Active Feeds: {len(settings.get_feed_list())}")
print("=" * 80)
