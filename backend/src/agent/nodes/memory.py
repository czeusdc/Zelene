"""Module: Memory node — persists intelligence to Cognee's knowledge graph.

This node runs after synthesis and stores all collected intelligence
(signals, entities, relationships, insights) in Cognee's persistent
memory layer. This enables Zelene to recall past intelligence across
deployments and build cumulative strategic understanding.
"""

import asyncio
import logging
from src.agent.state import AgentState
from src.agent.tools.real.cognee import get_cognee_tool
from src.sse.manager import sse_manager
from src.config import get_settings

logger = logging.getLogger(__name__)


async def memory_node(state: AgentState) -> dict:
    """Persist all intelligence outputs to Cognee's knowledge graph.

    Stores signals, entities, relationships, and insights as structured
    memory. Broadcasts a 'memory' SSE event when storage is complete.
    """
    deployment_id = state["deployment_id"]
    await sse_manager.broadcast(deployment_id, "node_start", {"node": "memory"})

    settings = get_settings()
    cognee = get_cognee_tool(settings.cognee_api_key)

    company_name = state.get("company_name", "Unknown")

    # Brief pause for dramatic timing
    await asyncio.sleep(1.5 * sse_manager.speed)

    # Broadcast a status message in Zelene's voice
    signal_count = len(state.get("signals", []))
    await sse_manager.broadcast(deployment_id, "signal", {
        "type": "status",
        "title": f"Building memory from {signal_count} observations.",
        "content": "Storing what I've learned so I can recall it later.",
    })

    await asyncio.sleep(1.0 * sse_manager.speed)

    # Store all intelligence in Cognee
    stored = await cognee.store_intelligence(
        company_name=company_name,
        signals=state.get("signals", []),
        entities=state.get("entities", []),
        relationships=state.get("relationships", []),
        insights=state.get("insights", []),
    )

    if stored:
        # Trigger knowledge graph construction
        await cognee.cognify()

    await asyncio.sleep(1.0 * sse_manager.speed)

    # Broadcast memory completion
    memory_type = "cognee" if settings.cognee_api_key else "session"
    await sse_manager.broadcast(deployment_id, "memory", {
        "stored": stored,
        "type": memory_type,
        "entity_count": len(state.get("entities", [])),
        "relationship_count": len(state.get("relationships", [])),
        "signal_count": signal_count,
        "company": company_name,
    })

    await sse_manager.broadcast(deployment_id, "node_complete", {
        "node": "memory",
        "stored": stored,
        "memory_type": memory_type,
    })

    return {"memory_stored": stored}
