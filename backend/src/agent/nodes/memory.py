"""Module: Memory node — persists intelligence to Cognee's knowledge graph.

This node runs after synthesis and stores all collected intelligence
(signals, entities, relationships, insights) in Cognee's persistent
memory layer. Uses a short timeout to avoid blocking the pipeline if
the Cognee API is unavailable — falls back to simulated storage.
"""

import asyncio
import logging
from src.agent.state import AgentState
from src.agent.tools.real.cognee import get_cognee_tool, CogneeMemoryTool
from src.sse.manager import sse_manager
from src.config import get_settings

logger = logging.getLogger(__name__)

# Timeout for Cognee API calls — cognify can take a few seconds
COGNEE_TIMEOUT = 15.0


async def memory_node(state: AgentState) -> dict:
    """Persist all intelligence outputs to Cognee's knowledge graph.

    Stores signals, entities, relationships, and insights as structured
    memory. Broadcasts a 'memory' SSE event when storage is complete.
    Uses a short timeout so the pipeline never hangs on Cognee.
    """
    deployment_id = state["deployment_id"]
    await sse_manager.broadcast(deployment_id, "node_start", {"node": "memory"})

    settings = get_settings()
    # Use simulated Cognee when data_simulation is True or no API key
    force_sim = state.get("data_simulation", False)
    cognee = get_cognee_tool(None if force_sim else settings.cognee_api_key)

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

    # Determine if we're using real Cognee or simulated
    is_real_cognee = isinstance(cognee, CogneeMemoryTool)
    stored = False

    if is_real_cognee:
        dataset_name = f"zelene-{company_name.lower().replace(' ', '-')}"
        try:
            # Store with timeout — don't block pipeline if Cognee is slow
            stored = await asyncio.wait_for(
                cognee.store_intelligence(
                    company_name=company_name,
                    signals=state.get("signals", []),
                    entities=state.get("entities", []),
                    relationships=state.get("relationships", []),
                    insights=state.get("insights", []),
                ),
                timeout=COGNEE_TIMEOUT,
            )
            if stored:
                await asyncio.wait_for(cognee.cognify([dataset_name]), timeout=COGNEE_TIMEOUT)
        except (asyncio.TimeoutError, Exception) as exc:
            logger.warning("Cognee API call failed/timed out, using session memory: %s", exc)
            # Fall back to simulated storage
            from src.agent.tools.real.cognee import SimulatedCogneeTool
            sim = SimulatedCogneeTool()
            stored = await sim.store_intelligence(
                company_name=company_name,
                signals=state.get("signals", []),
                entities=state.get("entities", []),
                relationships=state.get("relationships", []),
                insights=state.get("insights", []),
            )
            is_real_cognee = False
    else:
        stored = await cognee.store_intelligence(
            company_name=company_name,
            signals=state.get("signals", []),
            entities=state.get("entities", []),
            relationships=state.get("relationships", []),
            insights=state.get("insights", []),
        )

    await asyncio.sleep(1.0 * sse_manager.speed)

    # Broadcast memory completion
    memory_type = "cognee" if is_real_cognee else "session"
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
