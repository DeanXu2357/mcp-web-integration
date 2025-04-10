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
            description="search the web using searXNG. This will aggregate the results from google, bing, brave, duckduckgo and many others. Use this to find information on the web. Even if you do not have access to the internet, you can still use this tool to search the web.",
            inputSchema={
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string",
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range filter. Filter data from selected time range to now",
                        "enum": ["day", "week", "month", "year"],
                    },
                    "page": {
                        "type": "number",
                        "description": "Page number (starts from 1)",
                        "default": 1,
                        "minimum": 1,
                    },
                },
            },
        )

    async def handle_request(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:

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
            types.TextContent(text=summary, type="text"),
            types.TextContent(text="\n\n" + "\n".join(result_texts), type="text"),
        ]

    async def close(self) -> None:
        """Clean up resources."""
        await self.searcher.close()
