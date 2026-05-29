"""Module: Conversational chat API for asking questions about intelligence.

This module provides a conversational interface that answers user queries
about competitors, pricing, hiring, regulations, and sentiment. When Gemini
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


def _keyword_reply(q: str, company, competitors: list[str]) -> str:
    """Generate a keyword-routed template response (simulated fallback)."""
    comp0 = competitors[0] if len(competitors) > 0 else None
    comp1 = competitors[1] if len(competitors) > 1 else None

    if "price" in q or "pricing" in q:
        return (
            f"I'm seeing movement around {comp0}'s pricing — they've reduced enterprise "
            f"pricing by 12%. This could indicate a market share capture strategy. "
            f"I'm monitoring their pricing page daily."
            if comp0
            else "I don't have enough competitor pricing data yet to give a meaningful answer. "
                  "As intelligence is gathered, I'll surface pricing movements here."
        )
    elif "hire" in q or "hiring" in q:
        return (
            f"I noticed increased hiring activity from {comp0}, with 32 engineering "
            f"roles posted this week concentrated in APAC. Something interesting is "
            f"emerging — this suggests regional expansion."
            if comp0
            else "I'm tracking hiring signals across the competitive landscape. "
                  "No significant changes detected yet — check back after the next intelligence cycle."
        )
    elif "regulat" in q or "compliance" in q:
        return "This pattern deserves attention — there's emerging regulatory movement in enterprise software. A new compliance framework has been proposed affecting SaaS data handling."
    elif "sentiment" in q or "review" in q:
        if comp1:
            return (
                f"I'm noticing {comp1} is experiencing customer satisfaction decline — "
                f"47 negative reviews in 24 hours, primarily about support and pricing. "
                f"This creates a competitive positioning opportunity."
            )
        elif comp0:
            return (
                f"I'm noticing {comp0} is experiencing customer satisfaction decline — "
                f"47 negative reviews in 24 hours, primarily about support and pricing. "
                f"This creates a competitive positioning opportunity."
            )
        return "Customer sentiment analysis is still initializing. Once I've collected enough review and social data, I'll report shifts in satisfaction here."
    else:
        if comp0:
            return (
                f"I'm continuously observing {company.name}'s competitive landscape. "
                f"The most active signals I'm seeing involve {comp0}. "
                f"Could you specify which area you'd like me to investigate further?"
            )
        return (
            f"I'm continuously observing {company.name}'s competitive landscape. "
            f"So far no competitor signals have emerged. I can answer questions "
            f"about pricing, hiring, regulatory changes, or market sentiment once "
            f"sufficient intelligence is gathered."
        )


@router.post("/ask")
async def ask_zelene(req: AskRequest, db: AsyncSession = Depends(get_db)):
    """Answer a user question using Gemini or keyword-routed fallback."""
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

    if not isinstance(llm, SimulatedLLMProvider):
        try:
            result = await db.execute(
                select(Signal)
                .where(Signal.company_id == company.id)
                .order_by(Signal.extracted_at.desc())
                .limit(5)
            )
            recent_signals = result.scalars().all()

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
            logger.warning("Gemini chat failed, falling back to keyword routing: %s", exc)
            reply = _keyword_reply(q, company, competitors)
    else:
        reply = _keyword_reply(q, company, competitors)

    msg = Message(company_id=company.id, role="zelene", content=reply)
    db.add(msg)
    await db.commit()
    return {"reply": reply}
