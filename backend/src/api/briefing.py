"""Module: Strategic briefing API endpoint.

Provides an endpoint to generate executive briefings from stored
intelligence data. Compiles signals, entities, relationships, and
insights into a structured strategic summary using the LLM.
"""

import asyncio
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from src.db.connection import get_db
from src.db.models import CompanyProfile, Signal, Entity, Relationship, Insight, Deployment
from src.agent.tools.real.briefing import generate_briefing, _build_template_briefing
from src.agent.tools.registry import ToolProvider

logger = logging.getLogger(__name__)

router = APIRouter(tags=["briefing"])


class BriefingRequest(BaseModel):
    """Request to generate a strategic briefing for a company."""

    company_id: str


@router.post("/api/briefing/generate")
async def generate_briefing_endpoint(req: BriefingRequest, db: AsyncSession = Depends(get_db)):
    """Generate a strategic briefing from all stored intelligence.

    Compiles signals, entities, relationships, and insights into a
    structured executive summary with sections for strategic assessment,
    key findings, competitive landscape, and recommended actions.
    """
    company = await db.get(CompanyProfile, UUID(req.company_id))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Fetch intelligence data for this company
    signals_result = await db.execute(
        select(Signal).where(Signal.company_id == company.id).order_by(Signal.extracted_at.desc()).limit(20)
    )
    signals = signals_result.scalars().all()

    entities_result = await db.execute(
        select(Entity).where(Entity.company_id == company.id).limit(10)
    )
    entities = entities_result.scalars().all()

    # Relationships are linked via deployment, not company directly
    dep_result = await db.execute(
        select(Deployment).where(Deployment.company_id == company.id).order_by(Deployment.started_at.desc()).limit(1)
    )
    latest_dep = dep_result.scalars().first()

    relationships = []
    if latest_dep:
        rel_result = await db.execute(
            select(Relationship).where(Relationship.deployment_id == latest_dep.id).limit(10)
        )
        relationships = rel_result.scalars().all()

    insights_result = await db.execute(
        select(Insight).where(Insight.company_id == company.id).order_by(Insight.created_at.desc()).limit(5)
    )
    insights = insights_result.scalars().all()

    # Build entity name lookup for relationship display
    entity_names = {str(e.id): e.name for e in entities}

    # Convert to dicts
    signal_dicts = [
        {
            "title": s.title, "content": s.content, "type": s.signal_type,
            "severity": s.severity, "confidence": s.confidence,
        }
        for s in signals
    ]
    entity_dicts = [
        {"name": e.name, "type": e.entity_type, "description": e.description}
        for e in entities
    ]
    relationship_dicts = [
        {
            "entity_a": entity_names.get(str(r.entity_a), str(r.entity_a)),
            "entity_b": entity_names.get(str(r.entity_b), str(r.entity_b)),
            "relationship_type": r.relationship_type, "strength": r.strength,
        }
        for r in relationships
    ]
    insight_dicts = [
        {
            "title": i.title, "body": i.body, "type": i.insight_type,
            "confidence": i.confidence,
        }
        for i in insights
    ]

    # If no signal data, return template briefing immediately (skip LLM)
    if not signal_dicts:
        return _build_template_briefing(
            company.name, signal_dicts, entity_dicts, relationship_dicts, insight_dicts
        )

    # Get LLM provider and generate briefing with timeout
    company_context = {
        "company_name": company.name,
        "industry": company.industry or "",
        "competitors": company.competitors or [],
    }
    provider = ToolProvider(company_context)
    llm = provider.get_llm(reasoning_effort="high")

    try:
        briefing = await asyncio.wait_for(
            generate_briefing(
                company_name=company.name,
                signals=signal_dicts,
                entities=entity_dicts,
                relationships=relationship_dicts,
                insights=insight_dicts,
                llm=llm,
            ),
            timeout=30.0,
        )
    except (asyncio.TimeoutError, Exception) as exc:
        logger.warning("Briefing LLM generation failed, using template: %s", exc)
        briefing = _build_template_briefing(
            company.name, signal_dicts, entity_dicts, relationship_dicts, insight_dicts
        )

    return briefing
