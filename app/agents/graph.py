"""
Builds the LangGraph graph that connects classification and tool
execution into one runnable flow.

Currently a simple two-step path: classify, then execute. The
human-in-the-loop approval step (Phase 5) will sit between these
two nodes, pausing execution for risk_tiers that need it.
"""

from langgraph.graph import StateGraph, START, END
from app.agents.state import AgentState
from app.agents.nodes import classify_node, execute_tool_node

graph_builder = StateGraph(AgentState)

graph_builder.add_node("classify", classify_node)
graph_builder.add_node("execute_tool", execute_tool_node)

graph_builder.add_edge(START, "classify")
graph_builder.add_edge("classify", "execute_tool")
graph_builder.add_edge("execute_tool", END)

graph = graph_builder.compile()