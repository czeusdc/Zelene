"""Module: Strategic briefing generator.

Compiles all intelligence outputs (signals, entities, relationships,
insights) into a structured executive briefing using the LLM. Falls
back to a template-based briefing when the LLM is unavailable.
"""

import json
import logging
from datetime import datetime, timezone

from src.agent.tools.base import LLMProvider, AgentMessage
from src.agent.personality import filter_tone, filter_length

logger = logging.getLogger(__name__)

BRIEFING_PROMPT = """You are Zelene, an AI Chief Intelligence Officer. Generate a strategic briefing 
for {company_name} based on the following intelligence data. 

Write in Zelene's voice: observant, calm, confident but never certain. Use discovery language 
("I'm noticing...", "Something is emerging..."). No em dashes, no bullet hyphens, no markdown formatting.

Structure the briefing as:
1. STRATEGIC ASSESSMENT (2-3 sentences on the overall landscape)
2. KEY FINDINGS (3-5 most important observations from the signals)
3. COMPETITIVE LANDSCAPE (what entities and relationships reveal)
4. RECOMMENDED ACTIONS (2-3 concrete next steps)

Signals: {signals_json}
Entities: {entities_json}
Relationships: {relationships_json}
Existing Insights: {insights_json}

Keep the total under 400 words. Be specific to this company's data. Never fabricate information 
not present in the signals."""


def _build_template_briefing(
    company_name: str,
    signals: list[dict],
    entities: list[dict],
    relationships: list[dict],
    insights: list[dict],
) -> dict:
    """Generate a template-based briefing when the LLM is unavailable."""
    comp_names = [e.get("name", "") for e in entities if e.get("type") == "competitor"]
    signal_titles = [s.get("title", "") for s in signals[:5]]

    sections = []

    sections.append({
        "heading": "Strategic Assessment",
        "content": (
            f"I'm observing {len(signals)} signals across {company_name}'s competitive landscape. "
            f"{'Key competitors include ' + ', '.join(comp_names[:3]) + '.' if comp_names else 'The competitive landscape is taking shape.'} "
            f"Patterns are emerging that warrant attention."
        ),
    })

    findings = []
    for sig in signals[:5]:
        title = sig.get("title", "")
        if title:
            findings.append(title)
    sections.append({
        "heading": "Key Findings",
        "content": "\n".join(f"• {f}" for f in findings) if findings else "Intelligence gathering is still in progress.",
    })

    rel_summaries = []
    for rel in relationships[:5]:
        rel_summaries.append(
            f"{rel.get('entity_a', '')} {rel.get('relationship_type', 'related to')} "
            f"{rel.get('entity_b', '')} (strength: {rel.get('strength', 0):.0%})"
        )
    sections.append({
        "heading": "Competitive Landscape",
        "content": "\n".join(f"• {r}" for r in rel_summaries) if rel_summaries else "Relationship mapping in progress.",
    })

    sections.append({
        "heading": "Recommended Actions",
        "content": (
            "• Continue monitoring competitor activity for emerging patterns\n"
            "• Investigate the highest-confidence signals for strategic implications\n"
            "• Schedule a follow-up review as more intelligence accumulates"
        ),
    })

    return {
        "title": f"Strategic Briefing: {company_name}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sections": sections,
        "signal_count": len(signals),
        "entity_count": len(entities),
        "relationship_count": len(relationships),
        "insight_count": len(insights),
    }


async def generate_briefing(
    company_name: str,
    signals: list[dict],
    entities: list[dict],
    relationships: list[dict],
    insights: list[dict],
    llm: LLMProvider | None = None,
) -> dict:
    """Generate a strategic briefing from all intelligence data.

    Uses the LLM when available for natural language synthesis,
    falls back to template-based briefing otherwise.

    Args:
        company_name: The company this briefing is for.
        signals: Signals from the extract node.
        entities: Entities from the relate node.
        relationships: Relationships from the relate node.
        insights: Insights from the synthesize node.
        llm: Optional LLM provider for natural language generation.

    Returns:
        A structured briefing dict with title, sections, and metadata.
    """
    template = _build_template_briefing(company_name, signals, entities, relationships, insights)

    is_real = llm and not isinstance(llm, type) and hasattr(llm, "chat")
    if not is_real:
        return template

    try:
        prompt = BRIEFING_PROMPT.format(
            company_name=company_name,
            signals_json=json.dumps(signals[:10], indent=2, default=str),
            entities_json=json.dumps(entities[:10], indent=2, default=str),
            relationships_json=json.dumps(relationships[:10], indent=2, default=str),
            insights_json=json.dumps(insights[:5], indent=2, default=str),
        )
        raw = await llm.chat([AgentMessage(role="user", content=prompt)])
        filtered = filter_length(filter_tone(raw), max_words=450)

        sections = []
        current_heading = "Strategic Assessment"
        current_content = []

        for line in filtered.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith(("1.", "2.", "3.", "4.", "5.")) or line.isupper():
                if current_content:
                    sections.append({
                        "heading": current_heading,
                        "content": "\n".join(current_content),
                    })
                    current_content = []
                current_heading = line.lstrip("123456789. ").strip()
            else:
                current_content.append(line)

        if current_content:
            sections.append({
                "heading": current_heading,
                "content": "\n".join(current_content),
            })

        if len(sections) < 2:
            return template

        return {
            "title": f"Strategic Briefing: {company_name}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sections": sections,
            "signal_count": len(signals),
            "entity_count": len(entities),
            "relationship_count": len(relationships),
            "insight_count": len(insights),
        }
    except Exception as exc:
        logger.warning("LLM briefing generation failed, using template: %s", exc)
        return template
