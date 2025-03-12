"""Core search functionality for SearxNG integration."""
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
        try:
            api_params = {
                "q": params.query,
                "format": "json",
                "pageno": params.page,
            }
            
            if params.time_range:
                api_params["time_range"] = params.time_range

            response = await self.client.get(
                f"{self.config.base_url}/search",
                params=api_params,
            )
            response.raise_for_status()
            data = response.json()

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
                    # Skip malformed results
                    continue

            return SearchResponse(
                results=results,
                total_count=len(data.get("results", [])),
            )

        except httpx.HTTPError as e:
            raise RuntimeError(f"HTTP request failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Search operation failed: {str(e)}")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
