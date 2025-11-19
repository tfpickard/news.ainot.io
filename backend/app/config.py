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
        "http://feeds.arstechnica.com/arstechnica/index,"
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
