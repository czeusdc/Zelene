import asyncio
from src.agent.state import AgentState
from src.sse.manager import sse_manager

SIGNALS = [
    {"type": "price_change", "title": "Pricing change detected", "content": "CompetitorX reduced enterprise pricing by 12%. Analysis suggests market expansion play.",
     "source": "CompetitorX public pricing page", "confidence": 0.89, "severity": "warning", "entities": ["CompetitorX"]},
    {"type": "sentiment_shift", "title": "Customer sentiment decline", "content": "47 new negative reviews in 24 hours on G2. Primary complaints: support and pricing.",
     "source": "G2 Enterprise Software Reviews, Q2 2026", "confidence": 0.71, "severity": "warning", "entities": ["CompetitorY"]},
    {"type": "hiring_surge", "title": "Hiring surge detected", "content": "32 engineering roles posted this week, concentrated in APAC. Suggests regional expansion.",
     "source": "LinkedIn Talent Insights", "confidence": 0.94, "severity": "info", "entities": ["CompetitorX"]},
    {"type": "regulatory", "title": "Regulatory movement", "content": "New compliance framework proposed affecting SaaS data handling.",
     "source": "SEC EDGAR filing analysis", "confidence": 0.65, "severity": "warning", "entities": ["Regulatory"]},
]

async def extract_node(state: AgentState) -> dict:
    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "extract"})
    signals = []
    for i, template in enumerate(SIGNALS):
        await asyncio.sleep(1.5 / sse_manager._speed)
        comp0 = state["competitors"][0] if state["competitors"] else "CompetitorX"
        comp1 = state["competitors"][1] if len(state["competitors"]) > 1 else "CompetitorY"
        signal = {**template, "id": f"sig_{state['deployment_id'][:8]}_{i}",
                  "title": template["title"].replace("CompetitorX", comp0).replace("CompetitorY", comp1)}
        signals.append(signal)
        await sse_manager.broadcast(state["deployment_id"], "signal", signal)

    await sse_manager.broadcast(state["deployment_id"], "node_complete", {"node": "extract", "signals_extracted": len(signals)})
    return {"signals": signals, "signals_found": len(signals), "current_stage": "classify"}
