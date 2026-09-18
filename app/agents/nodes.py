"""
Defines the individual nodes (steps) used in the LangGraph graph.

classify_node determines the request type and risk tier (still
deterministic, taxonomy-driven). approval_gate_node pauses for
human approval on risky requests. agent_loop_node is where real
agentic behavior happens, Claude decides which tool(s) to call.
Each node also appends a trace entry describing what it did, used
to power the node-graph replay visualization.
"""

from langgraph.types import interrupt
from app.agents.classifier import classify_request
from app.agents.agent_loop import run_agent_loop
from app.models.taxonomy import TAXONOMY, RiskTier
from app.agents.state import AgentState


def classify_node(state: AgentState) -> dict:
    """Classifies the incoming message and looks up its risk tier."""
    request_type = classify_request(state["message"])
    risk_tier = TAXONOMY[request_type]["risk_tier"]

    return {
        "request_type": request_type.value,
        "risk_tier": risk_tier.value,
        "trace": [{
            "node": "classify",
            "request_type": request_type.value,
            "risk_tier": risk_tier.value,
        }],
    }


def approval_gate_node(state: AgentState) -> dict:
    """
    AUTO-tier requests pass straight through. Anything else pauses
    via interrupt() until a human decision is provided.
    """
    if state["risk_tier"] == RiskTier.AUTO.value:
        return {
            "approved": True,
            "trace": [{"node": "approval_gate", "action": "auto_approved"}],
        }

    decision = interrupt({
        "customer_id": state["customer_id"],
        "message": state["message"],
        "request_type": state["request_type"],
        "risk_tier": state["risk_tier"],
    })

    return {
        "approved": decision,
        "trace": [{"node": "approval_gate", "action": "human_decision", "approved": decision}],
    }


def agent_loop_node(state: AgentState) -> dict:
    """Runs the real agentic tool-use loop and records each step it took."""
    loop_output = run_agent_loop(state["customer_id"], state["message"])
    return {
        "tool_result": loop_output["tool_result"],
        "trace": loop_output["trace"],
    }