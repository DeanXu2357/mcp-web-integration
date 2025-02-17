# MCP Web Integration

A collection of web integration tools for Model Context Protocol (MCP).

## Available Tools

### SearxNG Search
Search functionality using SearxNG API.

### Crawl4AI Web Crawler
Web content extraction using Crawl4AI.

## Configuration

```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "uv",
      "args": ["-p", "@executeautomation/mcp-web-integration", "mcp-web-integration"],
      "env": {
        "SEARXNG_URL": "YOUR_SEARXNG_INSTANCE_URL",

        "CRAWL4AI_URL": "http://localhost:11235",
        "CRAWL4AI_API_TOKEN": "YOUR_API_TOKEN",
        
        // Crawler behavior
        "CRAWL4AI_HEADLESS": "true",
        "CRAWL4AI_VERBOSE": "false",
        "CRAWL4AI_WORD_COUNT_THRESHOLD": "10",
        
        // Timing settings
        "CRAWL4AI_TIMEOUT": "300",
        "CRAWL4AI_WAIT_TIME": "5",
        
        // Advanced options
        "CRAWL4AI_WAIT_FOR": ".content",
        "CRAWL4AI_JS_CODE": "[\"window.scrollTo(0, document.body.scrollHeight);\"]"
      }
    }
  }
}
```

### Configuration Options

#### Crawl4AI Options

| Environment Variable            | Description                               | Default                |
| ------------------------------- | ----------------------------------------- | ---------------------- |
| `CRAWL4AI_URL`                  | Crawl4AI server URL                       | http://localhost:11235 |
| `CRAWL4AI_API_TOKEN`            | API token for authentication              | Required               |
| `CRAWL4AI_HEADLESS`             | Run browser in headless mode              | true                   |
| `CRAWL4AI_VERBOSE`              | Enable verbose logging                    | false                  |
| `CRAWL4AI_WORD_COUNT_THRESHOLD` | Minimum word count for content            | 10                     |
| `CRAWL4AI_TIMEOUT`              | Request timeout in seconds                | 300                    |
| `CRAWL4AI_WAIT_TIME`            | Page load wait time in seconds            | 5                      |
| `CRAWL4AI_WAIT_FOR`             | CSS selector to wait for                  | null                   |
| `CRAWL4AI_JS_CODE`              | Custom JavaScript to execute (JSON array) | []                     |

## Development

### Requirements
- Python 3.8+
- Poetry for dependency management

### Installation

### Develope and Inspector
```bash
npx -y @modelcontextprotocol/inspector uv run mcp-web-integration --searxng-url http://fedora41-2:3030
```

## License
MIT License
