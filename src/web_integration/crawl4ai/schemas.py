"""Schemas for Crawl4AI integration."""

from typing import Any, Dict, List, Optional, Literal
from urllib.parse import urlparse
from pydantic import BaseModel, Field, field_validator


class CrawlParams(BaseModel):
    """Parameters for web crawling."""

    url: str = Field(..., description="URL to crawl")
    timeout: Optional[int] = Field(None, description="Request timeout in seconds")
    cache_mode: Optional[
        Literal["bypass", "enabled", "disabled", "read_only", "write_only"]
    ] = Field(
        default="enabled",
        description="Cache mode: bypass, enabled, disabled, read_only, write_only",
    )
    extra_headers: Optional[Dict[str, str]] = Field(
        None, description="Additional HTTP headers"
    )

    @field_validator("url")
    def validate_url(cls, v):
        """Validate URL format using urllib.parse."""
        result = urlparse(v)
        if not all([result.scheme, result.netloc]):
            raise ValueError("Invalid URL format: must include scheme and host")
        if result.scheme not in ("http", "https"):
            raise ValueError("URL scheme must be http or https")
        return v


class Link(BaseModel):
    """Link structure."""

    href: str = Field(..., description="Link URL")
    text: str = Field(..., description="Link text content")
    title: Optional[str] = Field(None, description="Link title attribute")

    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access to link attributes."""
        return getattr(self, key)


class CrawlResult(BaseModel):
    """Single crawl result."""

    url: str = Field(..., description="Crawled URL")
    content: str = Field(..., description="Extracted content in markdown format")
    status: str = Field(..., description="Crawl status")
    success: bool = Field(..., description="Whether crawl was successful")
    error: Optional[str] = Field(None, description="Error message if crawl failed")
    links: Dict[str, List[Link]] = Field(
        default_factory=lambda: {"internal": [], "external": []},
        description="Dictionary of internal and external links with metadata",
    )

    @field_validator("url")
    def validate_url(cls, v):
        """Validate URL format using urllib.parse."""
        result = urlparse(v)
        if not all([result.scheme, result.netloc]):
            raise ValueError("Invalid URL format: must include scheme and host")
        if result.scheme not in ("http", "https"):
            raise ValueError("URL scheme must be http or https")
        return v


class CrawlResponse(BaseModel):
    """Response containing crawl results."""

    results: List[CrawlResult] = Field(default_factory=list)
    total_count: int = Field(..., description="Total number of URLs crawled")
