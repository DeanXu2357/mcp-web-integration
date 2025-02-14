"""Configuration module for SearxNG integration."""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SearxNGConfig:
    """Configuration for SearxNG integration."""
    base_url: str

    @classmethod
    def from_env(cls) -> "SearxNGConfig":
        """Create config from environment variables."""
        base_url = os.getenv("SEARXNG_URL")
        if not base_url:
            raise ValueError("SEARXNG_URL environment variable is required")
        return cls(base_url=base_url)
