"""Core crawling functionality for Crawl4AI integration."""

import json
import sys
import httpx
from typing import Dict, Any, Optional
from .config import Crawl4AIConfig
from .schemas import CrawlParams, CrawlResponse, CrawlResult


class Crawl4AICrawler:
    """Handles crawling operations with Crawl4AI."""

    def __init__(self, config: Crawl4AIConfig):
        """Initialize crawler with configuration."""
        print("[INFO] Initializing Crawl4AICrawler", file=sys.stderr)
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
        self.headers = (
            {"Authorization": f"Bearer {self.config.api_token}"}
            if self.config.api_token
            else {}
        )
        print("[INFO] Crawl4AICrawler initialized successfully", file=sys.stderr)

    def _build_request_data(self, params: CrawlParams) -> Dict[str, Any]:
        """Build request data from params and config."""
        print(f"[INFO] Building request data for URL: {params.url}", file=sys.stderr)

        request_data = {
            "urls": params.url,
            "priority": 5,
            "cache_mode": params.cache_mode,  # Default is already set in Pydantic model
            "crawler_params": {
                "headless": self.config.headless,
                "verbose": self.config.verbose,
                "word_count_threshold": self.config.word_count_threshold,
            },
        }

        # Add optional parameters from config if set
        if self.config.wait_for:
            request_data["wait_for"] = self.config.wait_for
        if self.config.js_code:
            request_data["js_code"] = self.config.js_code

        # Add extra headers if provided
        if params.extra_headers:
            request_data["headers"] = params.extra_headers

        return request_data

    def _validate_response_data(self, data: Dict[str, Any]) -> None:
        """Validate response data structure."""
        print("[INFO] Validating response data", file=sys.stderr)
        if not isinstance(data, dict):
            error_msg = "Invalid response format: expected dictionary"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            raise ValueError(error_msg)

        if "result" not in data:
            error_msg = "Missing required field: result"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            raise ValueError(error_msg)

        result = data["result"]
        required_fields = ["markdown", "success", "links"]
        for field in required_fields:
            if field not in result:
                error_msg = f"Missing required field in result: {field}"
                print(f"[ERROR] {error_msg}", file=sys.stderr)
                raise ValueError(error_msg)

    def _build_error_response(self, url: str, error: str) -> CrawlResponse:
        """Build standardized error response."""
        return CrawlResponse(
            results=[
                CrawlResult(
                    url=url,
                    content="Error occurred while crawling",  # More descriptive default content
                    status="failed",
                    success=False,
                    error=error,
                    links={"internal": [], "external": []},
                )
            ],
            total_count=1,
        )

    async def crawl(self, params: CrawlParams) -> CrawlResponse:
        """Perform crawl using Crawl4AI direct API."""
        print(f"[INFO] Starting crawl for URL: {params.url}", file=sys.stderr)
        try:
            request_data = self._build_request_data(params)
            print(f"[INFO] Sending request to Crawl4AI API", file=sys.stderr)

            response = await self.client.post(
                f"{self.config.base_url}/crawl_direct",
                json=request_data,
                headers=self.headers,
                timeout=params.timeout or self.config.timeout,
            )

            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP {e.response.status_code}: {str(e)}"
                print(f"[ERROR] {error_msg}", file=sys.stderr)
                return self._build_error_response(params.url, error_msg)

            try:
                data = response.json()
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON response: {str(e)}"
                print(f"[ERROR] {error_msg}", file=sys.stderr)
                return self._build_error_response(params.url, error_msg)

            try:
                self._validate_response_data(data)
            except ValueError as e:
                print(f"[ERROR] Response validation failed: {e}", file=sys.stderr)
                return self._build_error_response(params.url, str(e))

            print(
                "[INFO] Successfully extracted and validated crawl results",
                file=sys.stderr,
            )
            results = [
                CrawlResult(
                    url=params.url,
                    content=data["result"]["markdown"] or "",  # Ensure content is never None
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

        except httpx.TimeoutException as e:
            error_msg = f"Request timeout: {str(e)}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            return self._build_error_response(params.url, error_msg)

        except httpx.TransportError as e:
            error_msg = f"HTTP/2 transport error: {str(e)}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            return self._build_error_response(params.url, error_msg)

        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            return self._build_error_response(params.url, error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            return self._build_error_response(params.url, error_msg)

    async def close(self) -> None:
        """Close the HTTP client."""
        print("[INFO] Closing HTTP client", file=sys.stderr)
        try:
            await self.client.aclose()
            print("[INFO] HTTP client closed successfully", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Failed to close HTTP client: {e}", file=sys.stderr)
