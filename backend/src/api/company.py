"""Module: Company onboarding API endpoints.

This module provides the conversational onboarding flow that collects company
profile information from the user and persists it to the database.
"""

import logging
from uuid import uuid4, UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from src.db.connection import get_db
from src.db.models import CompanyProfile, UserSettings
from src.agent.tools.registry import ToolProvider
from src.agent.tools.simulated.llm import SimulatedLLMProvider, _extract_company_name, _infer_industry
from src.agent.personality import filter_tone
from src.agent.tools.real.prompts import ONBOARDING_PROMPT
from src.agent.tools.base import AgentMessage

router = APIRouter(prefix="/api/company", tags=["company"])

VALID_STAGES = ["introduction", "company", "competitors", "goals", "confirm", "complete"]
STAGE_TRANSITIONS = {
    "introduction": "company",
    "company": "competitors",
    "competitors": "goals",
    "goals": "confirm",
    "confirm": "complete",
}

logger = logging.getLogger(__name__)


class OnboardRequest(BaseModel):
    """Incoming message during the conversational onboarding flow."""

    message: str
    session_id: str | None = None


class OnboardResponse(BaseModel):
    """LLM reply and accumulated context returned to the onboarding client."""

    reply: str
    session_id: str
    context_so_far: dict


class SaveCompanyRequest(BaseModel):
    """Request to persist a completed onboarding session as a company profile."""

    company_id: str

onboarding_sessions: dict[str, dict] = {}


def _get_stage_instructions(stage: str) -> str:
    """Return guidance text for the current onboarding stage."""
    instructions = {
        "introduction": "Greet the user warmly and ask them to describe their company and what they do. Extract the company name from their response.",
        "company": "Ask what makes their company different from others in the field. Acknowledge their unique positioning.",
        "competitors": "Ask who their main competitors are. They can list multiple names.",
        "goals": "Ask about their key business goals and priorities for the coming quarters.",
        "confirm": "Summarize what you've understood and ask them to confirm the details are correct.",
        "complete": "Let them know their intelligence environment is ready.",
    }
    return instructions.get(stage, "Continue the conversation naturally.")


@router.post("/onboard", response_model=OnboardResponse)
async def onboard(req: OnboardRequest):
    """Process a chat turn in the conversational onboarding flow."""
    session_id = req.session_id or str(uuid4())
    session = onboarding_sessions.get(session_id, {
        "company_name": None, "industry": None, "description": None,
        "competitors": [], "goals": [], "concerns": [], "market_focus": [],
        "stage": "introduction",
    })

    provider = ToolProvider(session)
    llm = provider.get_llm()

    if isinstance(llm, SimulatedLLMProvider):
        reply, updated, next_stage = llm.onboarding_turn(req.message, session)
        session.update(updated)
        session["stage"] = next_stage
    else:
        try:
            stage = session.get("stage", "introduction")
            stage_instructions = _get_stage_instructions(stage)
            prompt = ONBOARDING_PROMPT.format(
                stage=stage,
                company_name=session.get("company_name") or "unknown",
                industry=session.get("industry") or "unknown",
                competitors=", ".join(session.get("competitors", [])) or "none yet",
                goals=", ".join(session.get("goals", [])) or "none yet",
                user_message=req.message,
                stage_instructions=stage_instructions,
            )
            result = await llm.chat_structured(
                [AgentMessage(role="user", content=prompt)],
                schema_description='JSON object with "reply" (string), "context_updates" (object with optional company_name, industry, competitors, goals), "next_stage" (string)',
            )

            reply = filter_tone(result.get("reply", ""))
            context_updates = result.get("context_updates", {})
            proposed_stage = result.get("next_stage", stage)

            if context_updates.get("company_name"):
                session["company_name"] = context_updates["company_name"]
            elif not session.get("company_name") and stage == "introduction":
                session["company_name"] = _extract_company_name(req.message)

            if context_updates.get("industry"):
                session["industry"] = context_updates["industry"]
            elif not session.get("industry") and stage == "introduction":
                session["industry"] = _infer_industry(req.message)

            if context_updates.get("competitors"):
                existing = session.get("competitors", [])
                session["competitors"] = list(set(existing + context_updates["competitors"]))

            if context_updates.get("goals"):
                session["goals"] = context_updates["goals"]

            if stage == "introduction":
                session["description"] = req.message

            if proposed_stage in VALID_STAGES and proposed_stage == STAGE_TRANSITIONS.get(stage, stage):
                next_stage = proposed_stage
            else:
                next_stage = stage

            session["stage"] = next_stage

        except Exception as exc:
            logger.warning("AIMLAPI onboarding failed, falling back to simulated: %s", exc)
            fallback = SimulatedLLMProvider(session)
            reply, updated, next_stage = fallback.onboarding_turn(req.message, session)
            session.update(updated)
            session["stage"] = next_stage

    onboarding_sessions[session_id] = session

    return OnboardResponse(
        reply=reply, session_id=session_id,
        context_so_far={
            "company_name": session.get("company_name"),
            "industry": session.get("industry"),
            "description": session.get("description"),
            "competitors": session.get("competitors", []),
            "goals": session.get("goals", []),
            "concerns": session.get("concerns", []),
            "market_focus": session.get("market_focus", []),
        },
    )

@router.post("/save")
async def save_company(req: SaveCompanyRequest, db: AsyncSession = Depends(get_db)):
    """Persist the completed onboarding session to the database."""

    session = onboarding_sessions.get(req.company_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    company = CompanyProfile(
        name=session.get("company_name", "Unknown"),
        industry=session.get("industry"),
        description=session.get("description"),
        competitors=session.get("competitors", []),
        market_focus=session.get("market_focus", []),
        business_goals=session.get("goals", []),
        operational_concerns=session.get("concerns", []),
    )
    db.add(company)
    await db.flush()

    settings = UserSettings(company_id=company.id)
    db.add(settings)
    await db.commit()

    return {"status": "saved", "company_id": str(company.id)}

@router.get("/{company_id}")
async def get_company(company_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a saved company profile by its ID."""
    try:
        company_uuid = UUID(company_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid company ID format")
    company = await db.get(CompanyProfile, company_uuid)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "id": str(company.id), "name": company.name, "industry": company.industry,
        "description": company.description, "competitors": company.competitors or [],
        "market_focus": company.market_focus or [], "business_goals": company.business_goals or [],
        "operational_concerns": company.operational_concerns or [],
    }
