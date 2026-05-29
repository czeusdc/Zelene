"""Module: Discovery Intent Generator for dynamic search queries.

Uses the LLM provider to generate contextual search queries based on company
profile, competitors, industry, and onboarding context. Replaces hardcoded
query templates with intelligent, context-aware search strategies.
"""

import logging
from typing import List
from src.agent.tools.base import LLMProvider, AgentMessage
from src.agent.tools.real.prompts import QUERY_GENERATION_PROMPT

logger = logging.getLogger(__name__)


class QueryGenerator:
    """Generates dynamic search queries using the LLM based on company context."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def generate_queries(
        self,
        company_name: str,
        industry: str,
        competitors: List[str],
        onboarding_context: str = "",
        max_queries: int = 8,
    ) -> List[str]:
        """Generate contextual search queries for the deploy node.

        Args:
            company_name: Name of the company being analyzed
            industry: Industry sector
            competitors: List of competitor names
            onboarding_context: Additional context from onboarding (goals, concerns)
            max_queries: Maximum number of queries to generate (default 8)

        Returns:
            List of search query strings
        """
        prompt = QUERY_GENERATION_PROMPT.format(
            company_name=company_name,
            industry=industry,
            competitors=", ".join(competitors[:5]),
            onboarding_context=onboarding_context or "No additional context",
            max_queries=max_queries,
        )

        try:
            response = await self.llm.chat([AgentMessage(role="user", content=prompt)])

            queries = [
                line.strip()
                for line in response.strip().split("\n")
                if line.strip() and not line.strip().startswith("#")
            ]

            queries = queries[:max_queries]

            logger.info(f"Generated {len(queries)} queries for {company_name}")
            return queries

        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            return self._fallback_queries(company_name, industry, competitors)

    def _fallback_queries(
        self, company_name: str, industry: str, competitors: List[str]
    ) -> List[str]:
        """Generate fallback queries if Gemini fails."""
        from datetime import datetime
        year = datetime.now().year
        queries = []
        
        for i, comp in enumerate(competitors[:3]):
            if i == 0:
                queries.append(f"{comp} pricing changes {year}")
            elif i == 1:
                queries.append(f"{comp} customer reviews {year}")
            else:
                queries.append(f"{comp} market position {year}")
        
        queries.append(f"{industry} market trends {year}")
        queries.append(f"{company_name} competitive landscape {year}")
        
        return queries[:8]
