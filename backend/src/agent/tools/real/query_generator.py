"""Module: Discovery Intent Generator for dynamic search queries.

Uses the LLM provider to generate contextual search queries based on company
profile, competitors, industry, and onboarding context. Every query must
include the company or competitor name combined with industry or context
terms to avoid irrelevant results from similarly-named entities.
"""

import logging
from typing import List
from src.agent.tools.base import LLMProvider, AgentMessage
from src.agent.tools.real.prompts import QUERY_GENERATION_PROMPT

logger = logging.getLogger(__name__)

_MAX_QUALITY_QUERIES = 6  # fewer, focused queries yield better results than many broad ones


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

        Every generated query must include the company or competitor name
        combined with industry-specific context to prevent Bright Data SERP
        from returning results for unrelated companies with similar names.

        Args:
            company_name: Name of the company being analyzed
            industry: Industry sector
            competitors: List of competitor names
            onboarding_context: Additional context from onboarding (goals, concerns)
            max_queries: Maximum number of queries (capped at _MAX_QUALITY_QUERIES)

        Returns:
            List of search query strings
        """
        actual_max = min(max_queries, _MAX_QUALITY_QUERIES)
        prompt = QUERY_GENERATION_PROMPT.format(
            company_name=company_name,
            industry=industry,
            competitors=", ".join(competitors[:5]),
            onboarding_context=onboarding_context or "No additional context",
            max_queries=actual_max,
        )

        try:
            response = await self.llm.chat([AgentMessage(role="user", content=prompt)])

            queries = [
                line.strip()
                for line in response.strip().split("\n")
                if line.strip() and not line.strip().startswith("#")
            ]

            # Enforce: every query must contain the company name or a competitor name
            all_targets = {company_name.lower(), *(c.lower() for c in competitors[:5])}
            validated = []
            for q in queries:
                q_lower = q.lower()
                if any(target in q_lower for target in all_targets):
                    validated.append(q)
                elif industry.lower() in q_lower:
                    validated.append(q)  # industry-only queries for regulatory/trends

            validated = validated[:actual_max]

            if len(validated) < 3:
                validated = self._fallback_queries(company_name, industry, competitors)

            logger.info("Generated %d validated queries for %s", len(validated), company_name)
            return validated

        except Exception as e:
            logger.error("Query generation failed: %s", e)
            return self._fallback_queries(company_name, industry, competitors)

    def _fallback_queries(
        self, company_name: str, industry: str, competitors: List[str]
    ) -> List[str]:
        """Generate fallback queries that always include company/competitor name + industry."""
        from datetime import datetime
        year = datetime.now().year
        queries = []

        # Company-focused queries first
        queries.append(f"{company_name} {industry} {year}")
        queries.append(f"{company_name} pricing {industry} {year}")
        queries.append(f"{company_name} news {year}")

        # Competitor queries — always include company name for disambiguation
        for comp in competitors[:3]:
            queries.append(f"{comp} {industry} {year}")
            queries.append(f"{comp} pricing {industry} {year}")

        return queries[:_MAX_QUALITY_QUERIES]
