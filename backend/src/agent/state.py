"""Module: Agent state schema for the LangGraph intelligence pipeline.

This module defines the TypedDict used as shared state across all nodes
in the intelligence-gathering agent graph.
"""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Shared state dictionary passed between nodes in the agent pipeline."""

    messages: Annotated[list[BaseMessage], add_messages]
    company_id: str
    company_name: str
    industry: str
    competitors: list[str]
    deployment_id: str
    signals: list[dict]
    entities: list[dict]
    relationships: list[dict]
    insights: list[dict]
    current_stage: str
    signals_found: int
    relationships_mapped: int
