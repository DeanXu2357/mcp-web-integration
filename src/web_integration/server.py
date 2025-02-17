"""MCP server implementation."""

import anyio
import click
import os
import sys
from typing import Sequence
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.shared.exceptions import McpError

from web_integration.searxng import SearxNGSearchTool

# Global instance for the SearxNG tool
searxng_tool = None

# Initialize server with name
app = Server("mcp-web-integration")


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Handle list tools request."""
    if searxng_tool:
        return [searxng_tool.tool_definition]
    return []


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> types.CallToolResult:
    """Handle tool call request."""
    if searxng_tool and name == "searxng_search":
        if not arguments or "query" not in arguments:
            raise McpError(types.INVALID_PARAMS, "Missing required parameter: 'query'")
        return await searxng_tool.handle_request(name, arguments)
    raise McpError(types.METHOD_NOT_FOUND, "Tool not found")


@click.command()
@click.option(
    "--searxng-url",
    envvar="SEARXNG_URL",
    help="SearxNG instance URL",
)
def main(searxng_url: str | None = None) -> int:
    """Run the MCP server."""
    if searxng_url:
        os.environ["SEARXNG_URL"] = searxng_url

    async def arun():
        global searxng_tool
        try:
            # Initialize the tool before server starts
            searxng_tool = SearxNGSearchTool()

            async with stdio_server() as (read, write):
                # Initialize with required options
                init_options = InitializationOptions(
                    server_name="mcp-web-integration",
                    server_version="0.1.0",
                    capabilities=types.ServerCapabilities(
                        tools=types.ToolsCapability(listChanged=False)
                    ),
                )
                await app.run(
                    read,
                    write,
                    init_options,
                )
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        finally:
            if searxng_tool:
                await searxng_tool.close()

    return anyio.run(arun)


if __name__ == "__main__":
    sys.exit(main())
