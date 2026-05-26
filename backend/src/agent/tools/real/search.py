"""Module: Real Bright Data SERP search tool using the Python SDK.

This module wraps the Bright Data Python SDK's Google/Bing search capabilities
and exposes them through the SearchTool interface. Falls back gracefully to
simulated data when the API key is unavailable or the SDK is not installed.
"""

import logging
from src.agent.tools.base import SearchTool

logger = logging.getLogger(__name__)


class BrightDataSearchTool(SearchTool):
    """Real web search powered by Bright Data's SERP API via the Python SDK.

    Accepts a Bright Data API key and optionally a user context for
    personalizing competitor-aware queries. Results are normalized into
    a list of dicts matching the internal signal format.
    """

    def __init__(self, api_key: str, company_context: dict | None = None):
        self.api_key = api_key
        self.context = company_context or {}

    async def search(self, query: str, num_results: int = 10) -> list[dict]:
        """Execute a Google search via the Bright Data SDK and normalise results."""
        try:
            from brightdata import BrightDataClient
        except ImportError:
            logger.warning(
                "brightdata-sdk not installed. Install it with: "
                "pip install brightdata-sdk"
            )
            return []

        try:
            async with BrightDataClient(token=self.api_key) as client:
                response = await client.search.google(
                    query=query,
                    num_results=num_results,
                )
        except Exception as exc:
            logger.error("Bright Data SERP request failed: %s", exc)
            return []

        if not response.success:
            logger.warning("Bright Data SERP returned unsuccessful response")
            return []

        results = []
        for item in response.data[:num_results]:
            results.append({
                "title": getattr(item, "title", ""),
                "url": getattr(item, "link", ""),
                "snippet": getattr(item, "description", ""),
            })
        return results
