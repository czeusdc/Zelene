"""Module: Real Bright Data Web Unlocker tool.

This module wraps the Bright Data Python SDK's unlocked browsing capabilities
for sites that employ anti-bot protections. Falls back gracefully when the API
key is unavailable.
"""

import logging
from src.agent.tools.base import ScraperTool

logger = logging.getLogger(__name__)


class BrightDataUnlockerTool(ScraperTool):
    """Access protected web pages via Bright Data's Web Unlocker.

    Identical interface to the scraper but explicitly pins the Web Unlocker
    zone and adds geo-targeting options so protected or geo-restricted pages
    can be accessed reliably.
    """

    def __init__(self, api_key: str, country: str = "us"):
        self.api_key = api_key
        self.country = country

    async def scrape(self, url: str) -> str:
        """Fetch *url* through the Web Unlocker and return the raw HTML."""
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
                    country=self.country,
                )
        except Exception as exc:
            logger.error("Bright Data Unlocker request failed for %s: %s", url, exc)
            return ""

        if not response.success:
            logger.warning("Bright Data Unlocker returned unsuccessful response")
            return ""

        return getattr(response, "data", "") or ""
