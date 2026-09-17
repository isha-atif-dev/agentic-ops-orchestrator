"""
Defines the individual nodes (steps) used in the LangGraph graph.

classify_node determines the request type and risk tier (still
deterministic, taxonomy-driven, this controls approval gating and
must stay predictable for a financial services system).
approval_gate_node pauses for human approval on risky requests.
agent_loop_node is where real agentic behavior happens, Claude
decides which tool(s) to call, not a fixed lookup.
"""

from langgraph.types import interrupt
from app.agents.classifier import classify_request
from app.agents.agent_loop import run_agent_loop
from app.models.taxonomy import TAXONOMY, RiskTier
from app.agents.state import AgentState


def classify_node(state: AgentState) -> dict:
    """
    Classifies the incoming message and looks up its risk tier
    from the taxonomy. Always the first node in the graph.
    """
    request_type = classify_request(state["message"])
    risk_tier = TAXONOMY[request_type]["risk_tier"]

    return {
        "request_type": request_type.value,
        "risk_tier": risk_tier.value,
    }


def approval_gate_node(state: AgentState) -> dict:
    """
    Decides whether this request needs a human to approve it before
    the agent acts. AUTO-tier requests pass straight through.
    Anything else pauses the graph via interrupt() and waits for a
    human decision to be provided when the graph is resumed.
    """
    if state["risk_tier"] == RiskTier.AUTO.value:
        return {"approved": True}

    decision = interrupt({
        "customer_id": state["customer_id"],
        "message": state["message"],
        "request_type": state["request_type"],
        "risk_tier": state["risk_tier"],
    })

    return {"approved": decision}


def agent_loop_node(state: AgentState) -> dict:
    """
    Runs the real agentic tool-use loop, Claude decides which
    tool(s) to call for this specific request, rather than the
    taxonomy dictating a fixed list.
    """
    tool_result = run_agent_loop(state["customer_id"], state["message"])
    return {"tool_result": tool_result}