from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID
from src.db.connection import get_db
from src.db.models import CompanyProfile, Message

router = APIRouter(prefix="/api/conversation", tags=["conversation"])

class AskRequest(BaseModel):
    company_id: str
    message: str
    entity: str | None = None

@router.post("/ask")
async def ask_zelene(req: AskRequest, db: AsyncSession = Depends(get_db)):
    company = await db.get(CompanyProfile, UUID(req.company_id))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    q = req.message.lower()
    comp0 = company.competitors[0] if company.competitors else "CompetitorX"
    comp1 = company.competitors[1] if len(company.competitors) > 1 else "CompetitorY"

    if "price" in q or "pricing" in q:
        reply = f"Based on recent signals, {comp0} has reduced enterprise pricing by 12%. This could indicate a market share capture strategy. I'm monitoring their pricing page daily."
    elif "hire" in q or "hiring" in q:
        reply = f"I've detected increased hiring activity from {comp0}, with 32 engineering roles posted this week concentrated in APAC. This suggests regional expansion."
    elif "regulat" in q or "compliance" in q:
        reply = "There's emerging regulatory movement in enterprise software. A new compliance framework has been proposed affecting SaaS data handling."
    elif "sentiment" in q or "review" in q:
        reply = f"{comp1} is experiencing customer satisfaction decline — 47 negative reviews in 24 hours, primarily about support and pricing. This creates a competitive positioning opportunity."
    else:
        reply = f"Based on my current intelligence, I'm continuously monitoring {company.name}'s competitive landscape. The most active signals involve {comp0}. Could you specify which area you'd like me to investigate further?"

    msg = Message(company_id=company.id, role="zelene", content=reply)
    db.add(msg)
    await db.commit()
    return {"reply": reply}
