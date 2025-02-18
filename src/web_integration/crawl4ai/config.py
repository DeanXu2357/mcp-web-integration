"""Configuration module for Crawl4AI integration."""

import os
import json
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Crawl4AIConfig:
    """Configuration for Crawl4AI integration."""

    base_url: str
    api_token: Optional[str]

    # Crawler behavior params
    headless: bool
    verbose: bool
    word_count_threshold: int
    wait_for: Optional[str]
    js_code: Optional[List[str]]
    timeout: int

    @classmethod
    def from_env(cls) -> "Crawl4AIConfig":
        """Create config from environment variables."""
        return cls(
            base_url=os.getenv("CRAWL4AI_URL", "http://localhost:11235"),
            api_token=os.getenv("CRAWL4AI_API_TOKEN"),
            # Crawler params
            headless=os.getenv("CRAWL4AI_HEADLESS", "true").lower() == "true",
            verbose=os.getenv("CRAWL4AI_VERBOSE", "false").lower() == "true",
            word_count_threshold=int(os.getenv("CRAWL4AI_WORD_COUNT_THRESHOLD", "0")),
            wait_for=os.getenv("CRAWL4AI_WAIT_FOR"),
            js_code=json.loads(os.getenv("CRAWL4AI_JS_CODE", "[]")),
            timeout=int(os.getenv("CRAWL4AI_TIMEOUT", "300")),
        )
