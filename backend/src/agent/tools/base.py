"""Module: Abstract tool interfaces for the Zelene agent framework.

This module defines the abstract base classes that all tool providers must
implement: LLMProvider, SearchTool, and ScraperTool. Each supports both real
and simulated backends through a common interface.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator
import dataclasses


@dataclasses.dataclass
class AgentMessage:
    """A single message in a chat conversation with role and content."""

    role: str
    content: str


class LLMProvider(ABC):
    """Abstract interface for language-model providers (chat and streaming)."""

    @abstractmethod
    async def chat(self, messages: list[AgentMessage]) -> str: ...

    @abstractmethod
    async def stream(self, messages: list[AgentMessage]) -> AsyncIterator[str]: ...


class SearchTool(ABC):
    """Abstract interface for web-search tool providers."""

    @abstractmethod
    async def search(self, query: str, num_results: int = 10) -> list[dict]: ...


class ScraperTool(ABC):
    """Abstract interface for web-page scraper tool providers."""

    @abstractmethod
    async def scrape(self, url: str) -> str: ...
