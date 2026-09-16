"""
Builds the LangGraph graph connecting classification, human
approval, and tool execution into one runnable flow.

AUTO-tier requests flow straight through. NEEDS_APPROVAL and
URGENT_APPROVAL requests pause at approval_gate until a human
decision is provided, then either proceed to execute_tool or end
without taking any action.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import AgentState
from app.agents.nodes import classify_node, approval_gate_node, execute_tool_node


def route_after_approval(state: AgentState) -> str:
    """Sends approved requests to execute_tool, rejected ones straight to END."""
    return "execute_tool" if state["approved"] else END


graph_builder = StateGraph(AgentState)

graph_builder.add_node("classify", classify_node)
graph_builder.add_node("approval_gate", approval_gate_node)
graph_builder.add_node("execute_tool", execute_tool_node)

graph_builder.add_edge(START, "classify")
graph_builder.add_edge("classify", "approval_gate")
graph_builder.add_conditional_edges("approval_gate", route_after_approval, {"execute_tool": "execute_tool", END: END})
graph_builder.add_edge("execute_tool", END)

# A checkpointer is required for interrupt() to work, it's what
# "remembers" the paused state while waiting for a human decision.
# MemorySaver keeps it in memory, fine for development, we'll
# revisit this for production later if needed.
graph = graph_builder.compile(checkpointer=MemorySaver())