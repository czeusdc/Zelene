from abc import ABC, abstractmethod
from typing import AsyncIterator
import dataclasses

@dataclasses.dataclass
class AgentMessage:
    role: str
    content: str

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[AgentMessage]) -> str: ...
    @abstractmethod
    async def stream(self, messages: list[AgentMessage]) -> AsyncIterator[str]: ...

class SearchTool(ABC):
    @abstractmethod
    async def search(self, query: str, num_results: int = 10) -> list[dict]: ...

class ScraperTool(ABC):
    @abstractmethod
    async def scrape(self, url: str) -> str: ...
