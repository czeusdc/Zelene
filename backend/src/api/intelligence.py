"""Module: Intelligence deployment and SSE streaming API.

This module handles deploying intelligence-gathering runs and streaming live
updates back to the frontend via Server-Sent Events.
"""

import asyncio
import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from src.db.connection import get_db
from src.db.models import CompanyProfile, Deployment
from src.agent.graph import build_graph
from src.agent.state import AgentState
from src.sse.manager import sse_manager
from src.config import get_settings

router = APIRouter(tags=["intelligence"])


class DeployRequest(BaseModel):
    """Request to start an intelligence-gathering deployment for a company."""

    company_id: str


@router.post("/api/intelligence/deploy")
async def deploy(req: DeployRequest, db: AsyncSession = Depends(get_db)):
    """Launch an intelligence deployment and return the SSE stream URL."""
    company = await db.get(CompanyProfile, UUID(req.company_id))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    deployment_id = sse_manager.create_deployment()
    settings = get_settings()
    sse_manager._speed = settings.simulation_speed

    deployment = Deployment(id=UUID(deployment_id), company_id=company.id, mode=settings.mode, status="deploying")
    db.add(deployment)
    await db.commit()

    initial_state: AgentState = {
        "messages": [], "company_id": str(company.id), "company_name": company.name,
        "industry": company.industry or "Technology", "competitors": company.competitors or [],
        "deployment_id": deployment_id, "signals": [], "entities": [], "relationships": [],
        "insights": [], "current_stage": "deploy", "signals_found": 0, "relationships_mapped": 0,
    }

    graph = build_graph()
    asyncio.create_task(graph.ainvoke(initial_state, config={"configurable": {"thread_id": deployment_id}}))

    return {"stream_url": f"{settings.backend_url}/api/intelligence/stream?deployment_id={deployment_id}", "deployment_id": deployment_id}

@router.get("/api/intelligence/stream")
async def intelligence_stream(request: Request, deployment_id: str):
    """SSE endpoint that streams intelligence events for a deployment."""

    conn = sse_manager.subscribe(deployment_id)

    async def event_generator():
        """Yield SSE events from the deployment connection queue."""
        try:
            while conn.active:
                if await request.is_disconnected():
                    break
                try:
                    item = await asyncio.wait_for(conn.queue.get(), timeout=30)
                except asyncio.TimeoutError:
                    continue
                if item is None:
                    break
                event_type, data = item
                yield {"event": event_type, "data": json.dumps(data)}
        finally:
            sse_manager.unsubscribe(deployment_id, conn)

    return EventSourceResponse(event_generator())
