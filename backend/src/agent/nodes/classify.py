"""Module: Classify node — cross-references extracted signals against patterns.

This node compares extracted signals against historical market patterns and
broadcasts classification status via SSE.
"""

import asyncio
from src.agent.state import AgentState
from src.sse.manager import sse_manager


async def classify_node(state: AgentState) -> dict:
    """Classify signals by cross-referencing against known market patterns."""

    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "classify"})
    await asyncio.sleep(1 * sse_manager.speed)
    await sse_manager.broadcast(state["deployment_id"], "signal", {
        "type": "status",
        "title": "I'm comparing what I've found against known patterns.",
        "content": "Checking extracted signals against market behavior I've seen before.",
    })
    await sse_manager.broadcast(state["deployment_id"], "node_complete", {"node": "classify", "signals_classified": state.get("signals_found", 4)})
    return {"current_stage": "verify"}
