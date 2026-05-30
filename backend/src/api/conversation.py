"""Module: Conversational chat API for asking questions about intelligence.

This module provides a conversational interface that answers user queries
about competitors, pricing, hiring, regulations, and sentiment. When the LLM
is configured, responses are generated from real signal data. Otherwise,
keyword-routed template responses are used as fallback.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
from src.db.connection import get_db
from src.db.models import CompanyProfile, Message, Signal
from src.agent.tools.registry import ToolProvider
from src.agent.tools.simulated.llm import SimulatedLLMProvider
from src.agent.tools.base import AgentMessage
from src.agent.tools.real.prompts import CHAT_PROMPT
from src.agent.personality import filter_tone, filter_length

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversation", tags=["conversation"])


class AskRequest(BaseModel):
    """A question asked to Zelene about the company's intelligence."""

    company_id: str
    message: str
    entity: str | None = None


def _keyword_reply(q: str, company, competitors: list[str],
                   recent_signals: list[dict] | None = None) -> str:
    """Generate a signal-aware response. Looks up actual signals before replying
    to prevent fabricating observations that don't exist in the signal feed."""
    comp0 = competitors[0] if len(competitors) > 0 else None
    comp1 = competitors[1] if len(competitors) > 1 else None
    signals = recent_signals or []

    # Helper: check if a signal type exists for an entity
    def _has_signal(entity: str, signal_type: str | None = None) -> dict | None:
        if not entity:  # empty string matches all strings in Python — guard against it
            return None
        for s in signals:
            entities = s.get("entities", []) if isinstance(s, dict) else []
            name = s.get("title", "") if isinstance(s, dict) else ""
            if entity.lower() in name.lower() or entity.lower() in [e.lower() for e in entities]:
                if signal_type is None or s.get("type", "") == signal_type:
                    return s
        return None

    if "price" in q or "pricing" in q:
        matched = _has_signal(comp0 or "", "price_change") or _has_signal(comp1 or "", "price_change")
        if matched:
            return (
                f"I'm seeing movement around {comp0 or comp1}'s pricing. "
                f"Their recent adjustments suggest potential market repositioning. "
                f"I'm monitoring their pricing page daily."
            )
        return ("I don't have enough competitor pricing data yet to give a meaningful answer. "
                "As intelligence is gathered, I'll surface pricing movements here.")

    elif "hire" in q or "hiring" in q:
        matched = _has_signal(comp0 or "", "hiring_surge")
        if matched:
            return (
                f"I noticed increased hiring activity from {comp0}. "
                f"Notable recruitment activity suggests team expansion or a growth initiative."
            )
        return ("I'm tracking hiring signals across the competitive landscape. "
                "No significant changes detected yet. Check back after the next intelligence cycle.")

    elif "regulat" in q or "compliance" in q:
        matched = _has_signal("Regulatory", "regulatory")
        if matched:
            return ("This pattern deserves attention. There's emerging regulatory movement "
                    "in the industry. A new compliance framework has been proposed that could "
                    "affect operations.")
        return ("I haven't observed specific regulatory signals for {industry} yet. "
                "I'll surface any compliance developments as they emerge.".format(
                    industry=company.industry or "your industry"))

    elif "sentiment" in q or "review" in q:
        matched = _has_signal(comp1 or comp0 or "", "sentiment_shift")
        if matched:
            target = comp1 or comp0
            return (
                f"I'm noticing {target} is experiencing customer satisfaction shifts. "
                f"Recent reviews indicate changing sentiment around service quality and value perception."
            )
        return ("Customer sentiment analysis is still initializing. Once I've collected "
                "enough review and social data, I'll report shifts in satisfaction here.")

    else:
        # General question — reference what signals we DO have
        if signals and comp0:
            signal_types = ", ".join(set(
                s.get("type", "activity") for s in signals if isinstance(s, dict)
            ))
            return (
                f"I'm continuously observing {company.name}'s competitive landscape. "
                f"The most active signals I'm seeing involve {comp0}. "
                f"Current observation areas: {signal_types}. "
                f"Could you specify which area you'd like me to investigate further?"
            )
        return (
            f"I'm continuously observing {company.name}'s competitive landscape. "
            f"I can answer questions about pricing, hiring, regulatory changes, "
            f"or customer sentiment once sufficient intelligence is gathered."
        )


@router.post("/ask")
async def ask_zelene(req: AskRequest, db: AsyncSession = Depends(get_db)):
    """Answer a user question using the LLM or keyword-routed fallback."""
    company = await db.get(CompanyProfile, UUID(req.company_id))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    q = req.message.lower()
    competitors = company.competitors or []

    company_context = {
        "company_name": company.name,
        "industry": company.industry or "",
        "competitors": competitors,
    }
    provider = ToolProvider(company_context)
    llm = provider.get_llm()

    # Fetch recent signals for context-aware responses (both LLM and simulated)
    try:
        result = await db.execute(
            select(Signal)
            .where(Signal.company_id == company.id)
            .order_by(Signal.extracted_at.desc())
            .limit(5)
        )
        recent_signals = result.scalars().all()
    except Exception:
        recent_signals = []

    if not isinstance(llm, SimulatedLLMProvider):
        try:
            if recent_signals:
                signals_summary = "; ".join(
                    f"{s.signal_type}: {s.title}" for s in recent_signals
                )
            else:
                signals_summary = "No signals gathered yet"

            prompt = CHAT_PROMPT.format(
                company_name=company.name,
                industry=company.industry or "unknown",
                competitors=", ".join(competitors) if competitors else "none identified",
                recent_signals_summary=signals_summary,
                user_message=req.message,
            )

            raw_reply = await llm.chat([AgentMessage(role="user", content=prompt)])
            reply = filter_length(filter_tone(raw_reply), max_words=100)
        except Exception as exc:
            logger.warning("LLM chat failed, falling back to keyword routing: %s", exc)
            reply = _keyword_reply(q, company, competitors, [
                {"type": s.signal_type, "title": s.title, "entities": s.entities or []}
                for s in recent_signals
            ])
    else:
        reply = _keyword_reply(q, company, competitors, [
            {"type": s.signal_type, "title": s.title, "entities": s.entities or []}
            for s in recent_signals
        ])

    msg = Message(company_id=company.id, role="zelene", content=reply)
    db.add(msg)
    await db.commit()
    return {"reply": reply}
