"""Core crawling functionality for Crawl4AI integration."""

import httpx
from typing import Dict, Any
from .config import Crawl4AIConfig
from .schemas import CrawlParams, CrawlResponse, CrawlResult

import sys


class Crawl4AICrawler:
    """Handles crawling operations with Crawl4AI."""

    def __init__(self, config: Crawl4AIConfig):
        """Initialize crawler with configuration."""
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
        self.headers = (
            {"Authorization": f"Bearer {self.config.api_token}"}
            if self.config.api_token
            else {}
        )

    def _build_request_data(self, params: CrawlParams) -> Dict[str, Any]:
        """Build request data from params and config."""

        request_data = {
            "urls": params.url,
            "priority": 5,
            "cache_mode": params.cache_mode or "enabled",
            "crawler_params": {
                "headless": self.config.headless,
                "verbose": self.config.verbose,
                "word_count_threshold": self.config.word_count_threshold,
            },
        }

        # Add optional parameters from config if set
        if self.config.wait_for:
            request_data["wait_for"] = self.config.wait_for
        if self.config.wait_time:
            request_data["wait_time"] = self.config.wait_time
        if self.config.js_code:
            request_data["js_code"] = self.config.js_code

        # Add extra headers if provided
        if params.extra_headers:
            request_data["headers"] = params.extra_headers

        return request_data

    async def crawl(self, params: CrawlParams) -> CrawlResponse:
        """Perform crawl using Crawl4AI direct API."""
        try:
            request_data = self._build_request_data(params)

            # Use crawl_direct for immediate response
            response = await self.client.post(
                f"{self.config.base_url}/crawl_direct",
                json=request_data,
                headers=self.headers,
                timeout=params.timeout or self.config.timeout,
            )
            response.raise_for_status()
            data = response.json()

            # Extract and format results
            results = [
                CrawlResult(
                    url=params.url,
                    content=data["result"]["markdown"],
                    status="completed",
                    success=data["result"]["success"],
                    error=data.get("error"),
                    links={
                        "internal": [
                            {
                                "href": link.get("href", ""),
                                "text": link.get("text", ""),
                                "title": link.get("title", ""),
                            }
                            for link in data["result"]["links"].get("internal", [])
                        ],
                        "external": [
                            {
                                "href": link.get("href", ""),
                                "text": link.get("text", ""),
                                "title": link.get("title", ""),
                            }
                            for link in data["result"]["links"].get("external", [])
                        ],
                    },
                )
            ]

            return CrawlResponse(results=results, total_count=len(results))

        except httpx.HTTPError as e:
            # Handle HTTP related errors
            return CrawlResponse(
                results=[
                    CrawlResult(
                        url=params.url,
                        content="",
                        status="failed",
                        success=False,
                        error=f"HTTP request failed: {str(e)}",
                        links={"internal": [], "external": []},
                    )
                ],
                total_count=1,
            )
        except Exception as e:
            # Handle other errors
            return CrawlResponse(
                results=[
                    CrawlResult(
                        url=params.url,
                        content="",
                        status="failed",
                        success=False,
                        error=f"Crawl operation failed: {str(e)}",
                        links={"internal": [], "external": []},
                    )
                ],
                total_count=1,
            )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
