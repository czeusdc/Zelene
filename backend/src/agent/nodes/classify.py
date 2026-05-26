import asyncio
from src.agent.state import AgentState
from src.sse.manager import sse_manager

async def classify_node(state: AgentState) -> dict:
    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "classify"})
    await asyncio.sleep(1 / sse_manager._speed)
    await sse_manager.broadcast(state["deployment_id"], "signal", {
        "type": "status", "title": "Cross-referencing with historical patterns...",
        "content": "Comparing extracted signals against known market behavior.",
    })
    await sse_manager.broadcast(state["deployment_id"], "node_complete", {"node": "classify", "signals_classified": state.get("signals_found", 4)})
    return {"current_stage": "verify"}
