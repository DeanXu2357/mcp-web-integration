"""Configuration settings for YouTube transcript tool."""
from pydantic import BaseModel

class YouTubeConfig(BaseModel):
    """Configuration for YouTube transcript extraction."""
    max_retries: int = 3
    timeout: int = 30
    cookies_enabled: bool = False
    default_language: str = "en"
    # Placeholder for future proxy or API key settings if needed
    proxy: str | None = None
    api_key: str | None = None
