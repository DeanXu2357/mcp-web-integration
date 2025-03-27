"""MCP tool implementation for Crawl4AI web content extraction."""

from typing import Any, Dict, List, Sequence
import json
from mcp.types import Tool
import mcp.types as types
from mcp.shared.exceptions import McpError

from .config import Crawl4AIConfig
from .schemas import CrawlParams
from .crawler import Crawl4AICrawler


class Crawl4AITool:
    """MCP tool for extracting web content using Crawl4AI."""

    def __init__(self):
        """Initialize crawler tool."""
        self.config = Crawl4AIConfig.from_env()
        self.crawler = Crawl4AICrawler(self.config)

    @property
    def tool_definition(self) -> Tool:
        """Get tool definition."""
        return Tool(
            name="crawl4ai_extract",
            description="Extract content from web pages using Crawl4AI",
            inputSchema={
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to crawl",
                    },
                    "cache_mode": {
                        "type": "string",
                        "description": "Cache mode for crawling, the default value is 'enabled'",
                        "enum": [
                            "bypass",
                            "enabled",
                            "disabled",
                            "read_only",
                            "write_only",
                        ],
                    },
                    "extra_headers": {
                        "type": "object",
                        "description": "Additional HTTP headers for the request",
                        "additionalProperties": {"type": "string"},
                    },
                },
            },
        )

    async def handle_request(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Handle crawl request."""
        try:
            params = CrawlParams(**arguments)
            crawl_response = await self.crawler.crawl(params)

            # Format results in a user-friendly way
            result_texts = []
            for result in crawl_response.results:
                if result.success:
                    result_texts.extend(
                        [
                            f"URL: {result.url}",
                            "Content:",
                            result.content,
                            "---",
                            "\nInternal Links:",
                            *[
                                f"- {link['text']} ({link['href']})"
                                + (f" [{link['title']}]" if link["title"] else "")
                                for link in result.links["internal"]
                            ],
                            "\nExternal Links:",
                            *[
                                f"- {link['text']} ({link['href']})"
                                + (f" [{link['title']}]" if link["title"] else "")
                                for link in result.links["external"]
                            ],
                        ]
                    )
                else:
                    result_texts.extend(
                        [
                            f"Failed to crawl {result.url}",
                            f"Error: {result.error}",
                            "---",
                        ]
                    )

            return [
                types.TextContent(
                    text="\n\n" + "\n".join(result_texts), type="text"
                ).model_dump(exclude_unset=True)
            ]

        except Exception as e:
            return [types.TextContent(text=f"Crawl failed: {str(e)}", type="text")]

    async def close(self) -> None:
        """Clean up resources."""
        await self.crawler.close()
