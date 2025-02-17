"""MCP tool implementation for SearxNG search."""

from typing import Any, Dict, List, Sequence
import json
from mcp.types import Tool
import mcp.types as types
from mcp.shared.exceptions import McpError

from .config import SearxNGConfig
from .schemas import SearchParams
from .searcher import SearxNGSearcher


class SearxNGSearchTool:
    """MCP tool for performing searches with SearxNG."""

    def __init__(self):
        """Initialize search tool."""
        self.config = SearxNGConfig.from_env()
        self.searcher = SearxNGSearcher(self.config)

    @property
    def tool_definition(self) -> Tool:
        """Get tool definition."""
        return Tool(
            name="searxng_search",
            description="Search the web using SearxNG",
            inputSchema={
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Number of results (1-50, default 3)",
                        "default": 3,
                        "minimum": 1,
                        "maximum": 50,
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range filter. Filter data from selected time range to now",
                        "enum": ["day", "week", "month", "year"],
                    },
                },
            },
        )

    async def handle_request(
        self, name: str, arguments: Dict[str, Any]
    ) -> types.CallToolResult:
        """Handle search request."""
        try:
            params = SearchParams(**arguments)
            search_response = await self.searcher.search(params)

            # Format results in a user-friendly way
            result_texts = []
            for idx, result in enumerate(search_response.results, 1):
                result_texts.append(
                    f"{idx}. {result.title}\n"
                    f"URL: {result.url}\n"
                    f"Description: {result.snippet}\n"
                )

            summary = (
                f"Found {search_response.total_count} results "
                f"(showing top {len(search_response.results)})"
            )

            return [
                types.TextContent(type="text", text=summary),
                types.TextContent(type="text", text="\n\n" + "\n".join(result_texts)),
            ]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Search failed: {str(e)}")]

    async def close(self) -> None:
        """Clean up resources."""
        await self.searcher.close()
