import asyncio
from src.agent.state import AgentState
from src.sse.manager import sse_manager

async def deploy_node(state: AgentState) -> dict:
    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "deploy"})
    await asyncio.sleep(2 / sse_manager._speed)
    await sse_manager.broadcast(state["deployment_id"], "signal", {
        "type": "status", "title": "Scanning public web for signals...",
        "content": f"Searching for intelligence related to {state['company_name']} and {len(state['competitors'])} competitors.",
    })
    await sse_manager.broadcast(state["deployment_id"], "signal", {
        "type": "status", "title": "Found 47 potential sources", "content": "Beginning signal extraction.",
    })
    await sse_manager.broadcast(state["deployment_id"], "node_complete", {"node": "deploy", "sources_found": 47})
    return {"current_stage": "extract"}
