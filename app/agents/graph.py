"""
Builds the LangGraph graph connecting classification, human
approval, and the agentic tool-use loop into one runnable flow.

AUTO-tier requests flow straight through. NEEDS_APPROVAL and
URGENT_APPROVAL requests pause at approval_gate until a human
decision is provided, then either proceed to the agent loop or end
without taking any action.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import AgentState
from app.agents.nodes import classify_node, approval_gate_node, agent_loop_node


def route_after_approval(state: AgentState) -> str:
    """Sends approved requests to the agent loop, rejected ones straight to END."""
    return "agent_loop" if state["approved"] else END


graph_builder = StateGraph(AgentState)

graph_builder.add_node("classify", classify_node)
graph_builder.add_node("approval_gate", approval_gate_node)
graph_builder.add_node("agent_loop", agent_loop_node)

graph_builder.add_edge(START, "classify")
graph_builder.add_edge("classify", "approval_gate")
graph_builder.add_conditional_edges("approval_gate", route_after_approval, {"agent_loop": "agent_loop", END: END})
graph_builder.add_edge("agent_loop", END)

graph = graph_builder.compile(checkpointer=MemorySaver())