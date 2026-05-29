"""Tool abstractions, resolution, and providers for the agent.

Defines the base interfaces (LLMProvider, SearchTool, ScraperTool) and the
ToolProvider registry that resolves real vs. simulated implementations
per-tool based on available API keys.
"""

