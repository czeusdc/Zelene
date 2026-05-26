"""Module: Tool provider factory that resolves the active tool implementations.

This module inspects application settings to decide whether to use real or
simulated tool backends. Currently all paths default to simulated providers.
"""

from src.agent.tools.base import LLMProvider, SearchTool, ScraperTool
from src.agent.tools.simulated.llm import SimulatedLLMProvider
from src.agent.tools.simulated.search import SimulatedSearchTool
from src.agent.tools.simulated.scrape import SimulatedScraperTool
from src.config import get_settings


class ToolProvider:
    """Factory that creates the appropriate LLM, search, and scraper instances."""

    def __init__(self, company_context: dict | None = None):
        self.settings = get_settings()
        self.company_context = company_context

    def get_llm(self) -> LLMProvider:
        """Return the LLM provider (real or simulated based on API key presence)."""
        if self.settings.gemini_api_key:
            return SimulatedLLMProvider(self.company_context)
        return SimulatedLLMProvider(self.company_context)

    def get_search(self) -> SearchTool:
        """Return the search tool provider."""
        if self.settings.bright_data_api_key:
            return SimulatedSearchTool(self.company_context)
        return SimulatedSearchTool(self.company_context)

    def get_scraper(self) -> ScraperTool:
        """Return the scraper tool provider."""
        if self.settings.bright_data_api_key:
            return SimulatedScraperTool(self.company_context)
        return SimulatedScraperTool(self.company_context)
