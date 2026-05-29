"""Module: Tool provider factory that resolves the active tool implementations.

Inspects application settings and user-provided API keys to decide whether to
use real Bright Data / AIMLAPI backends or fall back to simulated providers.
Each tool resolves independently so partial real-mode (e.g. real LLM + simulated
search) is supported. A ``force_simulation`` flag on each getter bypasses API
key checks entirely for demo/presentation mode.
"""

from src.agent.tools.base import LLMProvider, SearchTool, ScraperTool
from src.agent.tools.simulated.llm import SimulatedLLMProvider
from src.agent.tools.simulated.search import SimulatedSearchTool
from src.agent.tools.simulated.scrape import SimulatedScraperTool
from src.agent.tools.real.search import BrightDataSearchTool
from src.agent.tools.real.scrape import BrightDataScraperTool
from src.agent.tools.real.unlocker import BrightDataUnlockerTool
from src.config import get_settings


class ToolProvider:
    """Factory that creates the appropriate LLM, search, and scraper instances.

    Resolution order:
    1. User-provided API key (from settings DB entry)
    2. Environment variable (BRIGHT_DATA_API_KEY / AIML_API_KEY)
    3. Simulated fallback
    """

    def __init__(self, company_context: dict | None = None):
        self.settings = get_settings()
        self.company_context = company_context

    def get_llm(self, reasoning_effort: str = "medium", force_simulation: bool = False) -> LLMProvider:
        """Return the LLM provider (real AIMLAPI when key is present).

        Args:
            reasoning_effort: Reasoning depth for DeepSeek V4 Pro —
                "low" (fast/chatty), "medium" (balanced), "high" (deep analysis).
                Ignored by simulated provider.
            force_simulation: If True, return a simulated provider regardless
                of API key presence. Used for demo/presentation mode.
        """
        if not force_simulation and self.settings.aiml_api_key:
            try:
                from src.agent.tools.real.llm import AIMLAPIProvider
                return AIMLAPIProvider(
                    api_key=self.settings.aiml_api_key,
                    reasoning_effort=reasoning_effort,
                )
            except Exception:
                pass
        return SimulatedLLMProvider(self.company_context)

    def get_search(self, force_simulation: bool = False) -> SearchTool:
        """Return a Bright Data SERP search tool when a key is configured.

        Args:
            force_simulation: If True, return a simulated provider regardless
                of API key presence.
        """
        if not force_simulation and self.settings.bright_data_api_key:
            try:
                return BrightDataSearchTool(
                    api_key=self.settings.bright_data_api_key,
                    company_context=self.company_context,
                )
            except Exception:
                pass  # fall through to simulated
        return SimulatedSearchTool(self.company_context)

    def get_scraper(self) -> ScraperTool:
        """Return a Bright Data scraper when a key is configured."""
        if self.settings.bright_data_api_key:
            try:
                return BrightDataScraperTool(
                    api_key=self.settings.bright_data_api_key,
                    company_context=self.company_context,
                )
            except Exception:
                pass  # fall through to simulated
        return SimulatedScraperTool(self.company_context)

    def get_unlocker(self) -> ScraperTool:
        """Return a Bright Data Web Unlocker when a key is configured."""
        if self.settings.bright_data_api_key:
            try:
                return BrightDataUnlockerTool(
                    api_key=self.settings.bright_data_api_key,
                )
            except Exception:
                pass  # fall through to simulated
        return SimulatedScraperTool(self.company_context)
