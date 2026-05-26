"""Module: Simulated web-scraper tool with mock page content.

This module returns hard-coded page content for recognized URL patterns
(pricing, reviews, careers) so the agent can operate without live scraping.
"""

from src.agent.tools.base import ScraperTool

MOCK_PAGES = {
    "pricing": "Enterprise Plan: $499/month. Growth Plan: $199/month. Starter: $49/month. CompetitorX recently reduced Enterprise tier by 12%.",
    "reviews": "Customer reviews show mixed sentiment. Overall rating: 3.8/5 (down from 4.2). 47 new negative reviews in 24h — primarily about support and pricing.",
    "careers": "Openings: 32 engineering (APAC), 8 sales (NA), 5 product. Notable: Senior ML Engineer, Head of APAC Expansion. Hiring velocity +40% QoQ.",
}

class SimulatedScraperTool(ScraperTool):
    """Simulated scraper that returns mock page text based on URL keywords."""

    def __init__(self, company_context: dict | None = None):
        self.context = company_context or {}

    async def scrape(self, url: str) -> str:
        """Return mock page content for the given URL."""
        url_lower = url.lower()
        if "pricing" in url_lower:
            return MOCK_PAGES["pricing"]
        if "review" in url_lower or "g2" in url_lower:
            return MOCK_PAGES["reviews"]
        if "career" in url_lower or "linkedin" in url_lower:
            return MOCK_PAGES["careers"]
        return "No structured content available."
