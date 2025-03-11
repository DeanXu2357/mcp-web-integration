"""Schema definitions for YouTube transcript tool."""
from typing import List, Optional
from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    """A segment of transcript text with timing information."""
    text: str
    start: float
    duration: float


class TranscriptRequest(BaseModel):
    """Request schema for transcript extraction."""
    url: str
    language: Optional[str] = None


class TranscriptResponse(BaseModel):
    """Response schema containing transcript data."""
    text: str
    language: str
    segments: List[TranscriptSegment]
