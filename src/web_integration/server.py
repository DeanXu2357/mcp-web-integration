"""MCP server implementation."""

import anyio
import click
import os
import sys
from typing import Sequence, Optional
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData

from web_integration.searxng import SearxNGSearchTool
from web_integration.crawl4ai import Crawl4AITool

# Global instances for tools
searxng_tool: Optional[SearxNGSearchTool] = None
crawl4ai_tool: Optional[Crawl4AITool] = None

# Initialize server with name
app = Server("mcp-web-integration")


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Handle list tools request."""
    print("[INFO] Handling list tools request", file=sys.stderr)
    tools = []
    if searxng_tool:
        tools.append(searxng_tool.tool_definition)
    if crawl4ai_tool:
        tools.append(crawl4ai_tool.tool_definition)
    return tools


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> types.CallToolResult:
    """Handle tool call request."""
    print(f"[INFO] Handling tool call: {name}", file=sys.stderr)
    
    if arguments is None:
        arguments = {}

    if name == "searxng_search" and searxng_tool:
        if not arguments or "query" not in arguments:
            error_msg = "Missing required parameter: 'query'"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            raise ValueError(error_msg)
        return await searxng_tool.handle_request(name, arguments)

    if name == "crawl4ai_extract" and crawl4ai_tool:
        if not arguments or "url" not in arguments:
            error_msg = "Missing required parameter: 'url'"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            raise ValueError(error_msg)
        return await crawl4ai_tool.handle_request(name, arguments)

    error_msg = f"Unknown tool: {name}"
    print(f"[ERROR] {error_msg}", file=sys.stderr)
    raise ValueError(error_msg)


@click.command()
@click.option(
    "--searxng-url",
    envvar="SEARXNG_URL",
    help="SearxNG instance URL",
)
@click.option(
    "--crawl4ai-url",
    envvar="CRAWL4AI_URL",
    help="Crawl4AI server URL",
)
@click.option(
    "--crawl4ai-token",
    envvar="CRAWL4AI_API_TOKEN",
    help="Crawl4AI API token",
)
def main(
    searxng_url: str | None = None,
    crawl4ai_url: str | None = None,
    crawl4ai_token: str | None = None,
) -> int:
    """Run the MCP server."""
    if searxng_url:
        os.environ["SEARXNG_URL"] = searxng_url
    if crawl4ai_url:
        os.environ["CRAWL4AI_URL"] = crawl4ai_url
    if crawl4ai_token:
        os.environ["CRAWL4AI_API_TOKEN"] = crawl4ai_token

    async def arun():
        """Run the server with basic error handling."""
        print("[INFO] Starting MCP Web Integration server", file=sys.stderr)
        
        try:
            # Initialize tools before server starts
            print("[INFO] Initializing tools...", file=sys.stderr)
            global searxng_tool, crawl4ai_tool
            searxng_tool = SearxNGSearchTool()
            crawl4ai_tool = Crawl4AITool()
            print("[INFO] Tools initialized successfully", file=sys.stderr)

            async with stdio_server() as (read, write):
                init_options = InitializationOptions(
                    server_name="mcp-web-integration",
                    server_version="0.1.0",
                    capabilities=types.ServerCapabilities(
                        tools=types.ToolsCapability(listChanged=False)
                    ),
                )
                await app.run(read, write, init_options)
            return 0
            
        except Exception as e:
            print(f"[ERROR] Server error: {str(e)}", file=sys.stderr)
            return 1
            
        finally:
            print("[INFO] Server shutting down...", file=sys.stderr)
            if searxng_tool:
                try:
                    await searxng_tool.close()
                except Exception as e:
                    print(f"[ERROR] Failed to close SearxNG tool: {e}", file=sys.stderr)
            if crawl4ai_tool:
                try:
                    await crawl4ai_tool.close()
                except Exception as e:
                    print(f"[ERROR] Failed to close Crawl4AI tool: {e}", file=sys.stderr)

    return anyio.run(arun)


if __name__ == "__main__":
    sys.exit(main())
