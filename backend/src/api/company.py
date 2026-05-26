from uuid import uuid4, UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from src.db.connection import get_db
from src.db.models import CompanyProfile, UserSettings
from src.agent.tools.simulated.llm import SimulatedLLMProvider

router = APIRouter(prefix="/api/company", tags=["company"])

class OnboardRequest(BaseModel):
    message: str
    session_id: str | None = None

class OnboardResponse(BaseModel):
    reply: str
    session_id: str
    context_so_far: dict

class SaveCompanyRequest(BaseModel):
    company_id: str

onboarding_sessions: dict[str, dict] = {}

@router.post("/onboard", response_model=OnboardResponse)
async def onboard(req: OnboardRequest):
    session_id = req.session_id or str(uuid4())
    session = onboarding_sessions.get(session_id, {
        "company_name": None, "industry": None, "description": None,
        "competitors": [], "goals": [], "concerns": [], "market_focus": [],
        "stage": "introduction",
    })

    llm = SimulatedLLMProvider(session)
    reply, updated, next_stage = llm.onboarding_turn(req.message, session)
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
    company = await db.get(CompanyProfile, UUID(company_id))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "id": str(company.id), "name": company.name, "industry": company.industry,
        "description": company.description, "competitors": company.competitors or [],
        "market_focus": company.market_focus or [], "business_goals": company.business_goals or [],
        "operational_concerns": company.operational_concerns or [],
    }
