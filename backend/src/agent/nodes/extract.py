"""Module: Extract node — extracts intelligence signals from discovered sources.

This node simulates pulling structured signals (pricing changes, sentiment
shifts, hiring surges, regulatory movements) from the web and broadcasts
each one via SSE. Competitor placeholders are replaced with actual company data.
"""

import asyncio
from src.agent.state import AgentState
from src.sse.manager import sse_manager

SIGNALS = [
    {"type": "price_change", "title": "Pricing change detected at {c0}",
     "content": "{c0} has adjusted their pricing structure. Analysis suggests "
                "potential market repositioning.",
     "source": "{c0} public pricing page", "confidence": 0.89, "severity": "warning"},
    {"type": "sentiment_shift", "title": "Customer sentiment shift for {c1}",
     "content": "Recent customer reviews indicate shifting sentiment. "
                "Primary themes: service quality and value perception.",
     "source": "Industry review platforms", "confidence": 0.71, "severity": "warning"},
    {"type": "hiring_surge", "title": "Hiring activity at {c0}",
     "content": "Notable recruitment activity detected. Suggests team expansion or "
                "strategic growth initiative.",
     "source": "LinkedIn Talent Insights", "confidence": 0.94, "severity": "info"},
    {"type": "regulatory", "title": "Regulatory development",
     "content": "A new compliance framework has been proposed that could affect "
                "the {industry} sector. Stay informed on potential operational impacts.",
     "source": "Industry regulatory filings", "confidence": 0.65, "severity": "warning"},
]


def _expand(template: dict, comp0: str, comp1: str, industry: str) -> dict:
    """Replace placeholder tokens in all string fields of a signal template."""
    result = {}
    for key, value in template.items():
        if isinstance(value, str):
            result[key] = value.format(c0=comp0, c1=comp1, industry=industry)
        else:
            result[key] = value
    # Attach relevant entities
    if result["type"] in ("price_change", "hiring_surge"):
        result["entities"] = [comp0]
    elif result["type"] == "sentiment_shift":
        result["entities"] = [comp1]
    else:
        result["entities"] = ["Regulatory"]
    return result


async def extract_node(state: AgentState) -> dict:
    """Extract structured intelligence signals from web sources."""

    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "extract"})

    competitors = state.get("competitors", [])
    comp0 = competitors[0] if competitors else "a competitor"
    comp1 = competitors[1] if len(competitors) > 1 else comp0
    industry = state.get("industry", "your")

    signals = []
    for i, template in enumerate(SIGNALS):
        await asyncio.sleep(1.5 / sse_manager.speed)
        signal = _expand(template, comp0, comp1, industry)
        signal["id"] = f"sig_{state['deployment_id'][:8]}_{i}"
        signals.append(signal)
        await sse_manager.broadcast(state["deployment_id"], "signal", signal)

    await sse_manager.broadcast(state["deployment_id"], "node_complete",
                                {"node": "extract", "signals_extracted": len(signals)})
    return {"signals": signals, "signals_found": len(signals), "current_stage": "classify"}
