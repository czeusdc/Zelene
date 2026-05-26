"""Module: Real Bright Data web scraper using the Python SDK.

This module wraps the Bright Data Python SDK's URL scraping capabilities and
exposes them through the ScraperTool interface. Falls back to an empty result
when the API key is unavailable or the SDK cannot be loaded.
"""

import logging
from src.agent.tools.base import ScraperTool

logger = logging.getLogger(__name__)


class BrightDataScraperTool(ScraperTool):
    """Real web page scraper powered by Bright Data's Web Scraper / Unlocker API.

    Accepts a Bright Data API key. Each call fetches a single URL and returns
    the page content as a plain-text string (HTML or markdown depending on the
    configuration).
    """

    def __init__(self, api_key: str, company_context: dict | None = None):
        self.api_key = api_key
        self.context = company_context or {}

    async def scrape(self, url: str) -> str:
        """Fetch the content of *url* through Bright Data and return it."""
        try:
            from brightdata import BrightDataClient
        except ImportError:
            logger.warning(
                "brightdata-sdk not installed. Install it with: "
                "pip install brightdata-sdk"
            )
            return ""

        try:
            async with BrightDataClient(token=self.api_key) as client:
                response = await client.scrape_url(
                    url,
                    data_format="markdown",
                )
        except Exception as exc:
            logger.error("Bright Data scrape request failed for %s: %s", url, exc)
            return ""

        if not response.success:
            logger.warning("Bright Data scraper returned unsuccessful response")
            return ""

        return getattr(response, "data", "") or ""
