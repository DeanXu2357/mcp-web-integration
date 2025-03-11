"""Configuration settings for YouTube transcript tool."""
import os
from pydantic import BaseModel

class YouTubeConfig(BaseModel):
    """Configuration for YouTube transcript extraction."""
    max_retries: int = 3
    timeout: int = 30
    cookies_enabled: bool = False
    default_language: str = "en"
    proxy: str | None = None
    api_key: str | None = None

    @classmethod
    def from_env(cls) -> "YouTubeConfig":
        """Create config from environment variables."""
        return cls(
            max_retries=int(os.getenv("YOUTUBE_MAX_RETRIES", "3")),
            timeout=int(os.getenv("YOUTUBE_TIMEOUT", "30")),
            cookies_enabled=bool(os.getenv("YOUTUBE_COOKIES_ENABLED", "false").lower() == "true"),
            default_language=os.getenv("YOUTUBE_DEFAULT_LANGUAGE", "en"),
            proxy=os.getenv("YOUTUBE_PROXY"),
            api_key=os.getenv("YOUTUBE_API_KEY")
        )
