"""Module: Cognee memory tool for persistent intelligence storage.

Provides store and query operations against the Cognee knowledge graph
service. When the API key is configured, stores signals, entities,
relationships, and insights as structured memory that persists across
deployments. Falls back to a simulated in-memory store when unavailable.
"""

import logging
import json
from typing import Any

import httpx

logger = logging.getLogger(__name__)

COGNEE_BASE_URL = "https://api.aws.cognee.ai/api/v1"


class CogneeMemoryTool:
    """Persistent intelligence memory backed by Cognee's knowledge graph.

    Stores strategic observations as structured text that Cognee processes
    into a queryable knowledge graph. Supports adding data, triggering
    graph construction, and searching for relevant context.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            headers={
                "X-Api-Key": api_key,
                "Content-Type": "application/json",
            },
        )

    async def aclose(self):
        """Release the underlying HTTP client."""
        await self._client.aclose()

    async def add(self, text: str, dataset_name: str = "zelene-intelligence") -> bool:
        """Add text data to Cognee for knowledge graph processing.

        Args:
            text: The intelligence data to store (signal, entity, etc.).
            dataset_name: Logical grouping name for the data.

        Returns:
            True if the data was accepted, False on error.
        """
        try:
            resp = await self._client.post(
                f"{COGNEE_BASE_URL}/add",
                json={"text": text, "dataset_name": dataset_name},
            )
            resp.raise_for_status()
            return True
        except Exception as exc:
            logger.warning("Cognee add failed: %s", exc)
            return False

    async def cognify(self) -> bool:
        """Trigger knowledge graph construction from added data.

        Returns:
            True if processing was initiated, False on error.
        """
        try:
            resp = await self._client.post(f"{COGNEE_BASE_URL}/cognify")
            resp.raise_for_status()
            return True
        except Exception as exc:
            logger.warning("Cognee cognify failed: %s", exc)
            return False

    async def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Search the knowledge graph for relevant intelligence context.

        Args:
            query: Natural language search query.
            limit: Maximum number of results to return.

        Returns:
            List of matching knowledge graph results.
        """
        try:
            resp = await self._client.post(
                f"{COGNEE_BASE_URL}/search",
                json={"query": query, "limit": limit},
            )
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                return data
            return data.get("results", [])
        except Exception as exc:
            logger.warning("Cognee search failed: %s", exc)
            return []

    async def store_intelligence(
        self,
        company_name: str,
        signals: list[dict],
        entities: list[dict],
        relationships: list[dict],
        insights: list[dict],
    ) -> bool:
        """Store a complete intelligence snapshot in Cognee's memory.

        Formats all pipeline outputs as structured text and adds them
        to Cognee for knowledge graph processing.

        Args:
            company_name: The company this intelligence is about.
            signals: List of signal dicts from the extract node.
            entities: List of entity dicts from the relate node.
            relationships: List of relationship dicts from the relate node.
            insights: List of insight dicts from the synthesize node.

        Returns:
            True if all data was accepted.
        """
        parts = [f"Intelligence report for {company_name}."]

        for sig in signals[:10]:
            severity = sig.get("severity", "info")
            parts.append(
                f"Signal ({severity}): {sig.get('title', '')}. "
                f"{sig.get('content', '')} "
                f"Confidence: {sig.get('confidence', 0):.0%}."
            )

        for ent in entities[:10]:
            parts.append(
                f"Entity: {ent.get('name', '')} ({ent.get('type', 'unknown')}). "
                f"{ent.get('description', '')}"
            )

        for rel in relationships[:10]:
            parts.append(
                f"Relationship: {rel.get('entity_a', '')} "
                f"{rel.get('relationship_type', 'related_to')} "
                f"{rel.get('entity_b', '')}. "
                f"Strength: {rel.get('strength', 0):.0%}."
            )

        for ins in insights[:5]:
            parts.append(
                f"Insight ({ins.get('type', 'observation')}): "
                f"{ins.get('title', '')}. {ins.get('body', '')} "
                f"Confidence: {ins.get('confidence', 0):.0%}."
            )

        full_text = "\n\n".join(parts)
        return await self.add(full_text, dataset_name=f"zelene-{company_name.lower().replace(' ', '-')}")


class SimulatedCogneeTool:
    """In-memory fallback when Cognee API is unavailable.

    Stores intelligence data locally and returns it on search queries.
    Provides the same interface as CogneeMemoryTool for seamless fallback.
    """

    def __init__(self):
        self._store: list[str] = []

    async def add(self, text: str, dataset_name: str = "zelene-intelligence") -> bool:
        self._store.append(text)
        return True

    async def cognify(self) -> bool:
        return True

    async def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        results = []
        for item in self._store[-limit:]:
            results.append({"text": item[:200], "score": 0.85})
        return results

    async def store_intelligence(
        self,
        company_name: str,
        signals: list[dict],
        entities: list[dict],
        relationships: list[dict],
        insights: list[dict],
    ) -> bool:
        parts = [f"Intelligence for {company_name}:"]
        for sig in signals[:5]:
            parts.append(f"Signal: {sig.get('title', '')}")
        for ent in entities[:5]:
            parts.append(f"Entity: {ent.get('name', '')}")
        self._store.append("\n".join(parts))
        return True


def get_cognee_tool(api_key: str | None = None) -> CogneeMemoryTool | SimulatedCogneeTool:
    """Return the appropriate Cognee tool based on API key availability."""
    if api_key:
        return CogneeMemoryTool(api_key)
    return SimulatedCogneeTool()
