# MCP Web Integration

A collection of web integration tools for Model Context Protocol (MCP).

## Available Tools

### SearxNG Search
Search functionality using SearxNG API. This tool provides web search capabilities with the following features:
- Configurable number of results (1-50)
- Time range filtering (day/week/month/year)
- Formatted results with titles, URLs, and descriptions

### Crawl4AI Web Crawler
Web content extraction using Crawl4AI. Features include:
- Content extraction from web pages
- Internal and external link extraction
- Configurable caching modes
- Custom HTTP header support
- Error handling and reporting

## Requirements

- Python >= 3.13
- Dependencies:
  - httpx >= 0.28.1
  - mcp[cli] >= 1.2.1
  - pydantic >= 2.10.6

## Configuration

```json
{
  "mcpServers": {
    "web-integration": {
      "command": "uv",
      "args": ["-p", "@executeautomation/mcp-web-integration", "run", "mcp-web-integration"],
      "env": {
        "SEARXNG_URL": "YOUR_SEARXNG_INSTANCE_URL",
        "CRAWL4AI_URL": "http://localhost:11235",
        "CRAWL4AI_API_TOKEN": "YOUR_API_TOKEN",
        "CRAWL4AI_HEADLESS": "true",
        "CRAWL4AI_VERBOSE": "false",
        "CRAWL4AI_WORD_COUNT_THRESHOLD": "10",
        "CRAWL4AI_TIMEOUT": "300"
      }
    }
  }
}
```

### Configuration Options

#### SearxNG Options
| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `SEARXNG_URL` | SearxNG instance URL | Required |

#### Crawl4AI Options
| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `CRAWL4AI_URL` | Crawl4AI server URL | http://localhost:11235 |
| `CRAWL4AI_API_TOKEN` | API token for authentication | Required |
| `CRAWL4AI_HEADLESS` | Run browser in headless mode | true |
| `CRAWL4AI_VERBOSE` | Enable verbose logging | false |
| `CRAWL4AI_WORD_COUNT_THRESHOLD` | Minimum word count for content | 10 |
| `CRAWL4AI_TIMEOUT` | Request timeout in seconds | 300 |

## Development

### Local Development Setup

1. Clone the repository
2. Create a Python virtual environment:
```bash
uv env
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -e .
```

### Running with Inspector

To test the integration with MCP Inspector:

```bash
npx -y @modelcontextprotocol/inspector uv run mcp-web-integration \
  --searxng-url YOUR_SEARXNG_URL \
  --crawl4ai-url YOUR_CRAWL4AI_URL \
  --crawl4ai-token YOUR_API_TOKEN
```

