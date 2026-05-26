"""Module: Relate node — discovers and maps relationships between entities.

This node creates entities from the company, competitors, and market context,
then maps typed relationships (competes_with, supplies_to, affected_by)
between them.
"""

import asyncio
from src.agent.state import AgentState
from src.sse.manager import sse_manager


async def relate_node(state: AgentState) -> dict:
    """Discover entities and map relationships between them."""

    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "relate"})
    await asyncio.sleep(1 / sse_manager.speed)

    entities = [
        {"id": "e1", "name": state["company_name"], "type": "company", "activity_level": 0.8},
        {"id": "e2", "name": state["competitors"][0] if state["competitors"] else "CompetitorX", "type": "competitor", "activity_level": 0.7},
        {"id": "e3", "name": state["competitors"][1] if len(state["competitors"]) > 1 else "CompetitorY", "type": "competitor", "activity_level": 0.4},
        {"id": "e4", "name": f"{state['industry']} Market", "type": "market", "activity_level": 0.5},
        {"id": "e5", "name": "Regulatory", "type": "regulatory", "activity_level": 0.3},
    ]
    relationships = [
        {"id": "r1", "entity_a": "e1", "entity_b": "e2", "relationship_type": "competes_with", "strength": 0.8},
        {"id": "r2", "entity_a": "e1", "entity_b": "e3", "relationship_type": "competes_with", "strength": 0.6},
        {"id": "r3", "entity_a": "e2", "entity_b": "e4", "relationship_type": "supplies_to", "strength": 0.7},
        {"id": "r4", "entity_a": "e1", "entity_b": "e5", "relationship_type": "affected_by", "strength": 0.5},
    ]

    for rel in relationships:
        await asyncio.sleep(0.5 / sse_manager.speed)
        await sse_manager.broadcast(state["deployment_id"], "relationship", rel)

    # Broadcast entity data so the frontend can render the map
    for entity in entities:
        await sse_manager.broadcast(state["deployment_id"], "entity", entity)

    await sse_manager.broadcast(state["deployment_id"], "node_complete", {"node": "relate", "entities_mapped": len(entities), "relationships_mapped": len(relationships)})
    return {"entities": entities, "relationships": relationships, "relationships_mapped": len(relationships), "current_stage": "synthesize"}
