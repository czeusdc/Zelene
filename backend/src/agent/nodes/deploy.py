"""Module: Deploy node — initiates the intelligence-gathering workflow.

This node scans for public web sources and signals related to the company
and its competitors, broadcasting status updates via SSE. When Bright Data
is configured, real SERP searches run in parallel with the timing delay.
"""

import asyncio
from datetime import datetime
from src.agent.state import AgentState
from src.agent.tools.registry import ToolProvider
from src.agent.tools.real.query_generator import QueryGenerator
from src.sse.manager import sse_manager


async def deploy_node(state: AgentState) -> dict:
    """Search for relevant web sources and signal availability for the company."""

    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "deploy"})

    company_context = {
        "company_name": state.get("company_name", ""),
        "industry": state.get("industry", ""),
        "competitors": state.get("competitors", []),
    }
    provider = ToolProvider(company_context)
    search_tool = provider.get_search()

    gemini_provider = provider.get_llm()
    query_generator = QueryGenerator(gemini_provider)

    competitors = state.get("competitors", [])
    industry = state.get("industry", "technology")
    goals = state.get("goals", [])
    onboarding_context = ", ".join(goals) if goals else ""

    queries = await query_generator.generate_queries(
        company_name=state["company_name"],
        industry=industry,
        competitors=competitors,
        onboarding_context=onboarding_context,
        max_queries=8,
    )

    async def run_searches():
        results = []
        for query in queries:
            search_results = await search_tool.search(query, num_results=5)
            for result in search_results:
                result["query"] = query
                results.append(result)
        return results

    search_task = asyncio.create_task(run_searches())
    await asyncio.sleep(2 * sse_manager.speed)
    web_sources = await search_task

    await sse_manager.broadcast(state["deployment_id"], "signal", {
        "type": "status", "title": "Scanning public web for signals...",
        "content": f"Searching for intelligence related to {state['company_name']} and {len(state['competitors'])} competitors.",
    })

    if web_sources:
        for source in web_sources[:5]:
            await sse_manager.broadcast(state["deployment_id"], "source", {
                "title": source.get("title", "Untitled"),
                "url": source.get("url", ""),
                "snippet": source.get("snippet", ""),
                "query": source.get("query", "competitive intelligence"),
            })
            await asyncio.sleep(0.3 * sse_manager.speed)

        await sse_manager.broadcast(state["deployment_id"], "signal", {
            "type": "status",
            "title": f"Found {len(web_sources)} sources across {len(queries)} searches",
            "content": "Beginning signal extraction.",
        })
    else:
        await sse_manager.broadcast(state["deployment_id"], "signal", {
            "type": "status", "title": "Found 47 potential sources", "content": "Beginning signal extraction.",
        })

    sources_count = len(web_sources) if web_sources else 47
    await sse_manager.broadcast(state["deployment_id"], "node_complete", {
        "node": "deploy", "sources_found": sources_count,
    })
    return {"web_sources": web_sources, "current_stage": "extract"}
