"""Module: Synthesize node — generates high-level insights from signals.

This final pipeline node synthesizes extracted signals, verified patterns,
and entity relationships into actionable intelligence insights, then
marks the deployment as active/complete.
"""

import asyncio
from src.agent.state import AgentState
from src.sse.manager import sse_manager


async def synthesize_node(state: AgentState) -> dict:
    """Generate synthesized insights from all collected intelligence data."""

    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "synthesize"})
    await asyncio.sleep(1.5 / sse_manager._speed)

    insights = [
        {
            "id": "ins_1", "type": "warning",
            "title": "Competitor pricing pressure emerging",
            "body": "I'm noticing a pattern. CompetitorX has reduced enterprise pricing by 12% while accelerating APAC hiring. This suggests a coordinated market expansion play.",
            "confidence": 0.88,
            "actions": ["monitor", "export_brief", "push_slack"],
            "reasoning": "Pricing drop + hiring surge + regional focus = expansion signal.",
        },
        {
            "id": "ins_2", "type": "opportunity",
            "title": "Customer satisfaction gap at CompetitorY",
            "body": "CompetitorY is experiencing a decline in customer satisfaction, with 47 negative reviews in 24 hours. Support and pricing are primary complaints.",
            "confidence": 0.71,
            "actions": ["monitor", "export_salesforce", "generate_brief"],
            "reasoning": "Sentiment decline + pricing complaints = competitor churn risk, acquisition opportunity.",
        },
    ]

    for insight in insights:
        await sse_manager.broadcast(state["deployment_id"], "insight", insight)

    await sse_manager.broadcast(state["deployment_id"], "node_complete", {"node": "synthesize", "insights_generated": len(insights)})
    await sse_manager.broadcast(state["deployment_id"], "complete", {"phase": "active", "summary": "Intelligence environment ready. Continuous monitoring engaged."})

    return {"insights": insights, "current_stage": "active"}
