"""Module: Synthesize node — generates high-level insights from signals.

This final pipeline node synthesizes extracted signals, verified patterns,
and entity relationships into actionable intelligence insights. When the LLM
is configured, real insights are generated concurrently with the timing delay
and filtered through the personality calibration layer.
"""

import asyncio
import json
import logging
from src.agent.state import AgentState
from src.agent.tools.registry import ToolProvider
from src.agent.tools.base import AgentMessage
from src.agent.tools.real.prompts import SYNTHESIZE_PROMPT
from src.agent.personality import apply_zelene_filters
from src.sse.manager import sse_manager

logger = logging.getLogger(__name__)


def _build_template_insights(state: AgentState) -> list[dict]:
    """Generate fallback template insights when the LLM is unavailable."""
    competitors = state.get("competitors", [])
    comp0 = competitors[0] if competitors else "a competitor"
    comp1 = competitors[1] if len(competitors) > 1 else comp0
    company = state.get("company_name", "Your company")

    return [
        {
            "id": "ins_1", "type": "warning",
            "title": f"I'm seeing increasing pressure from {comp0}",
            "body": (
                f"Something interesting is emerging around {comp0}'s strategic moves "
                f"that could affect {company}'s market position. "
                f"I'm noticing pricing adjustments and hiring activity that suggest potential expansion."
            ),
            "confidence": 0.88,
            "actions": ["monitor", "export_brief", "push_slack"],
            "reasoning": f"Pricing shifts + hiring activity at {comp0} = competitive pressure signal.",
        },
        {
            "id": "ins_2", "type": "opportunity",
            "title": f"Something interesting is emerging with {comp1}",
            "body": (
                f"I'm noticing customer sentiment indicators suggesting a window of opportunity "
                f"relative to {comp1}. Service quality and pricing are emerging "
                f"as key differentiators in the {state.get('industry', '')} space."
            ),
            "confidence": 0.71,
            "actions": ["monitor", "export_salesforce", "generate_brief"],
            "reasoning": f"Sentiment shifts + market positioning = competitive opportunity for {company}.",
        },
    ]


async def synthesize_node(state: AgentState) -> dict:
    """Generate synthesized insights from all collected intelligence data."""

    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "synthesize"})

    company_context = {
        "company_name": state.get("company_name", ""),
        "industry": state.get("industry", ""),
        "competitors": state.get("competitors", []),
    }
    provider = ToolProvider(company_context)
    llm = provider.get_llm(
        reasoning_effort="high",
        force_simulation=state.get("llm_simulation", False),
    )

    template_insights = _build_template_insights(state)
    insights = template_insights

    # Only the real provider exposes chat_structured — simulated falls through to templates
    is_real = not isinstance(llm, type) and hasattr(llm, "chat_structured")
    if is_real:
        prompt = SYNTHESIZE_PROMPT.format(
            company_name=state.get("company_name", "the company"),
            industry=state.get("industry", "technology"),
            signals_json=json.dumps(state.get("signals", [])[:10], indent=2, default=str),
            entities_json=json.dumps(state.get("entities", [])[:10], indent=2, default=str),
            relationships_json=json.dumps(state.get("relationships", [])[:10], indent=2, default=str),
        )

        async def fetch_llm_insights():
            """Call the LLM's structured-output endpoint for insight generation."""
            return await llm.chat_structured(
                [AgentMessage(role="user", content=prompt)],
                schema_description="JSON array of 2 insight objects with id, type, title, body, confidence, actions, reasoning",
            )

        # LLM call runs concurrently with the 1.5s pacing delay
        llm_task = asyncio.create_task(fetch_llm_insights())
        await asyncio.sleep(1.5 * sse_manager.speed)

        try:
            # 120s timeout accommodates DeepSeek V4 Pro reasoning + 5-10KB payload
            raw_insights = await asyncio.wait_for(llm_task, timeout=120.0)
            if isinstance(raw_insights, list) and len(raw_insights) >= 1:
                for i, ins in enumerate(raw_insights):
                    ins.setdefault("id", f"ins_{i + 1}")
                    ins.setdefault("actions", ["monitor", "export_brief"])
                insights = apply_zelene_filters(raw_insights[:2])
        except (asyncio.TimeoutError, Exception) as exc:
            logger.warning("LLM synthesis failed, using templates: %s", exc)
            insights = template_insights
    else:
        await asyncio.sleep(1.5 * sse_manager.speed)

    for insight in insights:
        await sse_manager.broadcast(state["deployment_id"], "insight", insight)

    await sse_manager.broadcast(state["deployment_id"], "node_complete",
                                {"node": "synthesize", "insights_generated": len(insights)})

    return {"insights": insights, "current_stage": "active"}
