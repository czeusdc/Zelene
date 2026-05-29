"""LangGraph agent pipeline and tool framework.

The agent is a linear 6-node graph (deploy → extract → classify → verify →
relate → synthesize) orchestrated by LangGraph. Tools resolve to real or
simulated providers based on environment configuration.
"""

