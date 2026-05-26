"""Module: LangGraph agent graph definition for the intelligence pipeline.

This module builds and compiles the state graph that orchestrates the
intelligence workflow: deploy → extract → classify → verify → relate → synthesize.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.agent.state import AgentState
from src.agent.nodes.deploy import deploy_node
from src.agent.nodes.extract import extract_node
from src.agent.nodes.classify import classify_node
from src.agent.nodes.verify import verify_node
from src.agent.nodes.relate import relate_node
from src.agent.nodes.synthesize import synthesize_node


def build_graph():
    """Build and compile the intelligence pipeline graph with all nodes."""

    workflow = StateGraph(AgentState)
    workflow.add_node("deploy", deploy_node)
    workflow.add_node("extract", extract_node)
    workflow.add_node("classify", classify_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("relate", relate_node)
    workflow.add_node("synthesize", synthesize_node)

    workflow.set_entry_point("deploy")
    workflow.add_edge("deploy", "extract")
    workflow.add_edge("extract", "classify")
    workflow.add_edge("classify", "verify")
    workflow.add_edge("verify", "relate")
    workflow.add_edge("relate", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile(checkpointer=MemorySaver())
