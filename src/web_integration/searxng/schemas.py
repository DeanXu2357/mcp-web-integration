"""Schemas for SearxNG integration."""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

class SearchParams(BaseModel):
    """Search parameters for SearxNG."""
    query: str = Field(..., description="Search query string")
    limit: int = Field(default=3, ge=1, le=50, description="Number of results to return")
    time_range: Optional[str] = Field(
        default=None,
        description="Time range for search results",
    )
    page: Optional[int] = Field(
        default=1,
        ge=1,
        description="Page number for pagination"
    )

class SearchResult(BaseModel):
    """Single search result from SearxNG."""
    title: str = Field(..., description="Title of the search result")
    url: HttpUrl = Field(..., description="URL of the search result")
    snippet: str = Field(..., description="Snippet/description of the search result")

class SearchResponse(BaseModel):
    """Response containing search results."""
    results: List[SearchResult] = Field(default_factory=list)
    total_count: int = Field(..., description="Total number of results found")
