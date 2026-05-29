"""Module: Extract node — extracts intelligence signals from discovered sources.

This node simulates pulling structured signals (pricing changes, sentiment
shifts, hiring surges, regulatory movements, new entrants) from the web
and broadcasts each one via SSE. Competitor placeholders are replaced with
actual company data. New entrant names are generated from industry-specific
adjective+noun pools.
"""

import asyncio
import random
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
    {"type": "new_entrant", "title": "Potential new entrant detected: {entrant_name}",
     "content": "{entrant_name} appears to be entering the {industry} space. "
                "Early signals suggest product development and team assembly. "
                "Monitoring for strategic moves.",
     "source": "Venture capital filings and talent networks",
     "confidence": 0.55, "severity": "info"},
]

# Industry-specific name components for generating realistic potential competitor names
INDUSTRY_NAME_PARTS = {
    "Technology": (["Nova", "Quantum", "Apex", "Nexus", "Pulse", "Vertex", "Orbit", "Catalyst", "Fusion", "Dynamo"],
                   ["Core", "Wave", "Byte", "Mind", "Lens", "Forge", "Grid", "Shift", "Flow", "Stack"]),
    "Finance": (["Alpha", "Pivot", "Titan", "Vanguard", "Summit", "Merit", "Prime", "Elevate", "Strata"],
                ["Capital", "Vault", "Ledger", "Trust", "Yield", "Shield", "Crest", "Bridge", "Peak"]),
    "Healthcare": (["Vita", "Cura", "Pure", "Aegis", "Nova", "Helix", "Synergy", "Apex", "Rena"],
                   ["Health", "Care", "Path", "Shield", "Pulse", "Wave", "Core", "Link", "Gene"]),
    "Retail": (["Flux", "Loop", "Knit", "Mosaic", "Pivot", "Bloom", "Crate", "Route"],
               ["Cart", "Shelf", "Aisle", "Market", "Port", "Row", "Hub", "Mode"]),
    "Manufacturing": (["Forge", "Anvil", "Titan", "Cast", "Firm", "Stead", "Bolt", "Rigid"],
                      ["Works", "Line", "Mill", "Fab", "Build", "Form", "Tek", "Core"]),
    "Real Estate": (["Key", "Stone", "Tower", "Pivot", "Summit", "Layer", "Block", "Grid"],
                    ["Reality", "Trust", "Group", "Holdings", "View", "Place", "Point", "Square"]),
    "Education": (["Edu", "Learn", "Skill", "Bright", "Mind", "Apex", "North", "Open"],
                  ["Path", "Lab", "Hub", "Gate", "Bridge", "Forge", "Canvas", "Way"]),
    "Hospitality & Food Service": (["Table", "Stone", "Brick", "Golden", "Harvest", "Plated", "Fresh", "Turntable"],
                                   ["Kitchen", "Dish", "Brew", "Table", "Crate", "Bite", "Plate", "Leaf"]),
    "Media & Entertainment": (["Pulse", "Arc", "Lens", "Bright", "Echo", "Nova", "Crest", "Rhythm"],
                              ["Media", "Stream", "Story", "Wave", "View", "Play", "Sound", "Reel"]),
    "Energy": (["Helios", "Volt", "Grid", "Pure", "Apex", "Sol", "Flux", "Terra"],
               ["Energy", "Power", "Cell", "Dyne", "Grid", "Watt", "Sun", "Source"]),
    "Insurance": (["Sure", "Safe", "Shield", "Aegis", "Titan", "Prime", "Secure", "Vantage"],
                  ["Assure", "Guard", "Trust", "Protect", "Cover", "Bond", "Risk", "Care"]),
    "Agriculture": (["Green", "Pure", "Harvest", "Field", "Terra", "Root", "Verdant", "Crop"],
                    ["Agri", "Grow", "Farm", "Yield", "Grain", "Bloom", "Soil", "Feed"]),
    "Telecommunications": (["Wave", "Link", "Pulse", "Connect", "Sky", "Beam", "Nova", "Apex"],
                           ["Net", "Link", "Wave", "Com", "Tel", "Connect", "Fiber", "Cast"]),
    "Legal": (["Bench", "Shield", "Scale", "Justice", "Merit", "Aegis", "Verdict", "Counsel"],
              ["Law", "Legal", "Group", "Firm", "Partners", "Advocate", "Right", "Bar"]),
    "Consulting": (["Apex", "Pivot", "Strata", "Summit", "Merit", "Catalyst", "Vantage", "Nexus"],
                   ["Advisory", "Consulting", "Group", "Partners", "Strategies", "Insight", "Solutions", "Collective"]),
    "Cybersecurity": (["Shield", "Aegis", "Fort", "Watch", "Dark", "Iron", "Cyber", "Secure"],
                      ["Guard", "Wall", "Shield", "Gate", "Sentinel", "Defense", "Lock", "Shield"]),
    "Transportation & Logistics": (["Freight", "Swift", "Route", "Link", "Pivot", "Transit", "Tide", "Nexus"],
                                   ["Logistics", "Haul", "Way", "Fleet", "Path", "Courier", "Line", "Flow"]),
}


def _generate_entrant_name(industry: str) -> str:
    """Generate a realistic company name for a potential new entrant based on industry."""
    adj_list, noun_list = INDUSTRY_NAME_PARTS.get(industry, INDUSTRY_NAME_PARTS["Technology"])
    adjective = random.choice(adj_list)
    noun = random.choice(noun_list)
    return f"{adjective}{noun}"


SIGNAL_TYPES = [s["type"] for s in SIGNALS]


def _expand(template: dict, comp0: str, comp1: str, industry: str) -> dict:
    """Replace placeholder tokens in all string fields of a signal template.

    For new_entrant signals, generates a realistic company name from
    the industry-specific adjective+noun pools.
    """
    result = {}
    entrant_name = _generate_entrant_name(industry) if template["type"] == "new_entrant" else None
    for key, value in template.items():
        if isinstance(value, str):
            kwargs = {"c0": comp0, "c1": comp1, "industry": industry}
            if entrant_name:
                kwargs["entrant_name"] = entrant_name
            result[key] = value.format(**kwargs)
        else:
            result[key] = value
    # Attach relevant entities
    if result["type"] in ("price_change", "hiring_surge"):
        result["entities"] = [comp0]
    elif result["type"] == "sentiment_shift":
        result["entities"] = [comp1]
    elif result["type"] == "new_entrant":
        result["entities"] = [entrant_name]
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
        await asyncio.sleep(1.5 * sse_manager.speed)
        signal = _expand(template, comp0, comp1, industry)
        signal["id"] = f"sig_{state['deployment_id'][:8]}_{i}"
        signals.append(signal)
        await sse_manager.broadcast(state["deployment_id"], "signal", signal)

    await sse_manager.broadcast(state["deployment_id"], "node_complete",
                                {"node": "extract", "signals_extracted": len(signals)})
    return {"signals": signals, "signals_found": len(signals), "current_stage": "classify"}
