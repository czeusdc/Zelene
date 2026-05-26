"""Module: Relate node — discovers and maps relationships between entities.

This node creates entities from the company, competitors, and market context,
then maps typed relationships (competes_with, operates_in, affected_by)
between them. Adapts to any number of competitors.
"""

import asyncio
from src.agent.state import AgentState
from src.sse.manager import sse_manager


async def relate_node(state: AgentState) -> dict:
    """Discover entities and map relationships between them."""

    await sse_manager.broadcast(state["deployment_id"], "node_start", {"node": "relate"})
    await asyncio.sleep(1 / sse_manager.speed)

    company = state.get("company_name", "Your Company")
    industry = state.get("industry", "the market")
    competitors = state.get("competitors", [])

    entities = [{"id": "e1", "name": company, "type": "company", "activity_level": 0.8}]
    relationships = []

    # Market entity
    market = {"id": "e_market", "name": f"{industry} Market", "type": "market", "activity_level": 0.5}

    # Add each competitor
    for idx, comp_name in enumerate(competitors[:5]):  # max 5 for visual clarity
        eid = f"e_comp{idx}"
        entities.append({"id": eid, "name": comp_name, "type": "competitor", "activity_level": 0.7 - idx * 0.1})
        # Company competes with each competitor
        relationships.append({"id": f"r_compete_{idx}", "entity_a": "e1", "entity_b": eid,
                              "relationship_type": "competes_with", "strength": 0.8 - idx * 0.1})
        # Competitor operates in the market
        relationships.append({"id": f"r_comp_market_{idx}", "entity_a": eid, "entity_b": "e_market",
                              "relationship_type": "operates_in", "strength": 0.6})

    # Fallback if no competitors
    if not competitors:
        entities.append({"id": "e_comp0", "name": "Key Competitor", "type": "competitor", "activity_level": 0.5})
        relationships.append({"id": "r_compete_0", "entity_a": "e1", "entity_b": "e_comp0",
                              "relationship_type": "competes_with", "strength": 0.7})

    # Regulatory entity
    reg = {"id": "e_reg", "name": "Regulatory", "type": "regulatory", "activity_level": 0.3}
    entities.append(reg)
    relationships.append({"id": "r_reg", "entity_a": "e1", "entity_b": "e_reg",
                          "relationship_type": "affected_by", "strength": 0.5})

    # Company operates in market
    relationships.append({"id": "r_co_market", "entity_a": "e1", "entity_b": "e_market",
                          "relationship_type": "operates_in", "strength": 0.9})
    entities.append(market)

    for rel in relationships:
        await asyncio.sleep(0.5 / sse_manager.speed)
        await sse_manager.broadcast(state["deployment_id"], "relationship", rel)

    for entity in entities:
        await sse_manager.broadcast(state["deployment_id"], "entity", entity)

    await sse_manager.broadcast(state["deployment_id"], "node_complete",
                                {"node": "relate", "entities_mapped": len(entities),
                                 "relationships_mapped": len(relationships)})
    return {"entities": entities, "relationships": relationships,
            "relationships_mapped": len(relationships), "current_stage": "synthesize"}
