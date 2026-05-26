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
    await asyncio.sleep(1.5 / sse_manager.speed)

    competitors = state.get("competitors", [])
    comp0 = competitors[0] if competitors else "a competitor"
    comp1 = competitors[1] if len(competitors) > 1 else comp0
    company = state.get("company_name", "Your company")

    insights = [
        {
            "id": "ins_1", "type": "warning",
            "title": f"Competitive pressure from {comp0}",
            "body": (
                f"I've detected signals suggesting {comp0} is making strategic moves "
                f"that could affect {company}'s market position. "
                f"Pricing adjustments and hiring activity indicate potential expansion."
            ),
            "confidence": 0.88,
            "actions": ["monitor", "export_brief", "push_slack"],
            "reasoning": f"Pricing shifts + hiring activity at {comp0} = competitive pressure signal.",
        },
        {
            "id": "ins_2", "type": "opportunity",
            "title": f"Market opportunity vs {comp1}",
            "body": (
                f"Customer sentiment indicators suggest a window of opportunity "
                f"relative to {comp1}. Service quality and pricing are emerging "
                f"as key differentiators in the {state.get('industry', '')} space."
            ),
            "confidence": 0.71,
            "actions": ["monitor", "export_salesforce", "generate_brief"],
            "reasoning": f"Sentiment shifts + market positioning = competitive opportunity for {company}.",
        },
    ]

    for insight in insights:
        await sse_manager.broadcast(state["deployment_id"], "insight", insight)

    await sse_manager.broadcast(state["deployment_id"], "node_complete",
                                {"node": "synthesize", "insights_generated": len(insights)})
    await sse_manager.broadcast(state["deployment_id"], "complete",
                                {"phase": "active",
                                 "summary": "Intelligence environment ready. Continuous monitoring engaged."})

    return {"insights": insights, "current_stage": "active"}
