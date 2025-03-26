"""Core search functionality for SearxNG integration."""

import sys
from typing import List
import httpx
from .config import SearxNGConfig
from .schemas import SearchParams, SearchResult, SearchResponse


class SearxNGSearcher:
    """Handles search operations with SearxNG."""

    def __init__(self, config: SearxNGConfig):
        """Initialize searcher with configuration."""
        self.config = config
        self.client = httpx.AsyncClient(timeout=10.0)

    async def search(self, params: SearchParams) -> SearchResponse:
        """Perform search using SearxNG API."""
        print(f"[INFO] Starting search for query: {params.query}", file=sys.stderr)
        try:
            api_params = {
                "q": params.query,
                "format": "json",
                "pageno": params.page,
            }

            if params.time_range:
                api_params["time_range"] = params.time_range

            print("[INFO] Sending request to SearxNG", file=sys.stderr)
            response = await self.client.get(
                f"{self.config.base_url}/search",
                params=api_params,
            )
            
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP {e.response.status_code}: {str(e)}"
                print(f"[ERROR] {error_msg}", file=sys.stderr)
                raise RuntimeError(error_msg)

            try:
                data = response.json()
            except ValueError as e:
                error_msg = f"Invalid JSON response: {str(e)}"
                print(f"[ERROR] {error_msg}", file=sys.stderr)
                raise RuntimeError(error_msg)

            # Extract and format results
            results: List[SearchResult] = []
            for result in data.get("results", []):
                try:
                    results.append(
                        SearchResult(
                            title=result["title"],
                            url=result["url"],
                            snippet=result.get("content", "No description available"),
                        )
                    )
                except (KeyError, ValueError) as e:
                    print(f"[WARNING] Skipping malformed result: {str(e)}", file=sys.stderr)
                    continue

            total_count = len(data.get("results", []))
            print(f"[INFO] Search completed successfully. Found {total_count} results", file=sys.stderr)
            return SearchResponse(
                results=results,
                total_count=total_count,
            )

        except httpx.TimeoutException as e:
            error_msg = f"Request timeout: {str(e)}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            raise RuntimeError(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Search operation failed: {str(e)}"
            print(f"[ERROR] {error_msg}", file=sys.stderr)
            raise RuntimeError(error_msg)

    async def close(self) -> None:
        """Close the HTTP client."""
        print("[INFO] Closing HTTP client", file=sys.stderr)
        try:
            await self.client.aclose()
            print("[INFO] HTTP client closed successfully", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Failed to close HTTP client: {e}", file=sys.stderr)
