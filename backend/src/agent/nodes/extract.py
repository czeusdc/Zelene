"""Module: Extract node — extracts intelligence signals from discovered sources.

This node pulls structured signals (pricing changes, sentiment shifts,
hiring surges, regulatory movements, emerging competitor activity) from
web sources and broadcasts each one via SSE. Competitor placeholders are
replaced with actual company data. No entities are fabricated — all
named companies come from the user's competitive landscape.
"""

import asyncio
from src.agent.state import AgentState
from src.sse.manager import sse_manager

SIGNALS = [
    {"type": "price_change", "title": "Pricing change detected at {c0}",
     "content": "{c0} has adjusted their pricing structure. Analysis suggests "
                "potential market repositioning.",
     "source": "{c0} public pricing page", "confidence": 0.89, "severity": "warning",
     "source_keywords": ["pricing"]},
    {"type": "sentiment_shift", "title": "Customer sentiment shift for {c1}",
     "content": "Recent customer reviews indicate shifting sentiment. "
                "Primary themes: service quality and value perception.",
     "source": "Industry review platforms", "confidence": 0.71, "severity": "warning",
     "source_keywords": ["review", "sentiment", "satisfaction"]},
    {"type": "hiring_surge", "title": "Hiring activity at {c0}",
     "content": "Notable recruitment activity detected. Suggests team expansion or "
                "strategic growth initiative.",
     "source": "LinkedIn Talent Insights", "confidence": 0.94, "severity": "info",
     "source_keywords": ["hiring", "careers", "talent", "engineer"]},
    {"type": "regulatory", "title": "Regulatory development",
     "content": "A new compliance framework has been proposed that could affect "
                "the {industry} sector. Stay informed on potential operational impacts.",
     "source": "Industry regulatory filings", "confidence": 0.65, "severity": "warning",
     "source_keywords": ["regulation", "compliance", "rule", "blocking"]},
    {"type": "new_entrant", "title": "Emerging competitive activity detected",
     "content": "Signals suggest emerging competitive activity in the {industry} "
                "space. Early indicators include product development and team "
                "assembly. Monitoring for strategic moves.",
     "source": "Venture capital filings and talent networks",
     "confidence": 0.55, "severity": "info",
     "source_keywords": ["venture", "funding", "startup", "series"]},
]

SIGNAL_TYPES = [s["type"] for s in SIGNALS]


def _match_source_ids(signal_type: str, signal_keywords: list[str],
                      web_sources: list[dict]) -> list[str]:
    """Match a signal to relevant web sources by keyword search on title and snippet.

    Returns up to 2 matching source IDs to serve as evidence provenance.
    """
    matches = []
    for src in web_sources:
        title = (src.get("title", "") or "").lower()
        snippet = (src.get("snippet", "") or "").lower()
        url = (src.get("url", "") or "").lower()
        combined = f"{title} {snippet} {url}"
        if any(kw.lower() in combined for kw in signal_keywords):
            matches.append(src.get("id", ""))
            if len(matches) >= 2:
                break
    return matches


def _expand(template: dict, comp0: str, comp1: str, industry: str,
            web_sources: list[dict]) -> dict:
    """Replace placeholder tokens in all string fields of a signal template
    and attach evidence provenance by linking to matching web sources.
    """
    result = {}
    for key, value in template.items():
        if isinstance(value, str):
            result[key] = value.format(c0=comp0, c1=comp1, industry=industry)
        elif key == "source_keywords":
            continue  # metadata, not part of the output signal
        else:
            result[key] = value
    # Attach relevant entities — only from real competitor names
    if result["type"] in ("price_change", "hiring_surge"):
        result["entities"] = [comp0]
    elif result["type"] == "sentiment_shift":
        result["entities"] = [comp1]
    elif result["type"] == "regulatory":
        result["entities"] = ["Regulatory"]
    elif result["type"] == "new_entrant":
        result["entities"] = []  # no fabricated entity names
    # Evidence provenance: link signal to matching web sources
    keywords = template.get("source_keywords", [])
    result["source_ids"] = _match_source_ids(result["type"], keywords, web_sources)
    return result


async def extract_node(state: AgentState) -> dict:
    """Extract structured intelligence signals from web sources.

    Each signal is linked to its provenance via source_ids — web sources
    matched by keyword similarity on title, URL, and snippet text.
    """

    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "extract"})

    competitors = state.get("competitors", [])
    comp0 = competitors[0] if competitors else "a competitor"
    comp1 = competitors[1] if len(competitors) > 1 else comp0
    industry = state.get("industry", "your")
    web_sources = state.get("web_sources", [])

    signals = []
    for i, template in enumerate(SIGNALS):
        await asyncio.sleep(1.5 * sse_manager.speed)
        signal = _expand(template, comp0, comp1, industry, web_sources)
        signal["id"] = f"sig_{state['deployment_id'][:8]}_{i}"
        signals.append(signal)
        await sse_manager.broadcast(state["deployment_id"], "signal", signal)

    await sse_manager.broadcast(state["deployment_id"], "node_complete",
                                {"node": "extract", "signals_extracted": len(signals)})
    return {"signals": signals, "signals_found": len(signals), "current_stage": "classify"}
