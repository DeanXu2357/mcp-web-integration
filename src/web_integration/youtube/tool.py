"""MCP tool implementation for YouTube transcript extraction."""

from typing import Any, Dict, List
import json
from mcp.types import Tool
import mcp.types as types
from mcp.shared.exceptions import McpError

from .config import YouTubeConfig
from .schemas import TranscriptRequest
from .extractor import YouTubeTranscriptExtractor

class YouTubeTranscriptTool:
    """MCP tool for extracting transcripts from YouTube videos."""

    def __init__(self):
        """Initialize transcript tool."""
        self.config = YouTubeConfig.from_env()
        self.extractor = YouTubeTranscriptExtractor(self.config)

    @property
    def tool_definition(self) -> Tool:
        """Get tool definition."""
        return Tool(
            name="youtube_transcript",
            description="Extract transcript from YouTube videos",
            inputSchema={
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "YouTube video URL or ID",
                    },
                    "language": {
                        "type": "string",
                        "description": "Preferred language code (e.g., 'en', 'es'). If not available, will try to translate from available languages.",
                    }
                },
            },
        )

    async def handle_request(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Handle transcript extraction request."""
        try:
            params = TranscriptRequest(**arguments)
            transcript = await self.extractor.get_transcript(
                url=params.url,
                language=params.language
            )

            # Format results in a user-friendly way
            result_text = [
                f"Language: {transcript.language}",
                "\nTranscript:",
                transcript.text,
                "\nTimestamped Segments:",
                *[
                    f"[{segment.start:.1f}s - {segment.start + segment.duration:.1f}s] {segment.text}"
                    for segment in transcript.segments
                ]
            ]

            return [types.TextContent(text="\n".join(result_text), type="text")]

        except Exception as e:
            return [types.TextContent(text=f"Transcript extraction failed: {str(e)}", type="text")]

    async def close(self) -> None:
        """Clean up resources."""
        # No cleanup needed for now
        pass
