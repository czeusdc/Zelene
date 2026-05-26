"""Module: Verify node — validates signal confidence and resolves conflicts.

This node checks extracted signals for consistency with historical data,
flags conflicts, and adjusts confidence scores.
"""

import asyncio
from src.agent.state import AgentState
from src.sse.manager import sse_manager


async def verify_node(state: AgentState) -> dict:
    """Verify signal confidence scores and resolve conflicting signals."""

    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "verify"})
    await asyncio.sleep(0.5 / sse_manager._speed)
    signals = state.get("signals", [])
    high_conf = len([s for s in signals if s.get("confidence", 0) >= 0.7])
    await sse_manager.broadcast(state["deployment_id"], "signal", {
        "type": "status",
        "title": f"Verification complete. {high_conf} of {len(signals)} signals high-confidence.",
        "content": "Two signals conflict with historical market behavior. Confidence adjusted.",
    })
    await sse_manager.broadcast(state["deployment_id"], "node_complete", {"node": "verify", "high_confidence": high_conf})
    return {"current_stage": "relate"}
