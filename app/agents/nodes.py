"""
Defines the individual nodes (steps) used in the LangGraph graph.

Each function here takes the current AgentState, does one job, and
returns the fields it updated. Enums (RequestType, RiskTier) are
stored in state as plain string values, not enum instances, since
LangGraph checkpoints this state and plain strings serialize safely.
Enum behaviour is used locally inside each node where needed.
"""

from langgraph.types import interrupt
from app.agents.classifier import classify_request
from app.agents.arg_extractor import extract_tool_args
from app.agents.tool_schemas import TOOL_ARG_SCHEMAS
from app.models.taxonomy import TAXONOMY, RequestType, RiskTier
from app.agents.state import AgentState
from app.tools import actions


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


def extract_args_node(state: AgentState) -> dict:
    """
    Extracts any extra arguments each mapped tool needs, beyond
    customer_id. Tools with no schema in TOOL_ARG_SCHEMAS need no
    extra arguments, so they're skipped here.
    """
    request_type = RequestType(state["request_type"])
    tool_names = TAXONOMY[request_type]["tools"]

    tool_args = {}
    for tool_name in tool_names:
        if tool_name in TOOL_ARG_SCHEMAS:
            tool_args[tool_name] = extract_tool_args(state["message"], tool_name)

    return {"tool_args": tool_args}


def approval_gate_node(state: AgentState) -> dict:
    """
    Decides whether this request needs a human to approve it before
    the tool runs. AUTO-tier requests pass straight through. Anything
    else pauses the graph via interrupt(), and waits for a human
    decision to be provided when the graph is resumed.
    """
    if state["risk_tier"] == RiskTier.AUTO.value:
        return {"approved": True}

    decision = interrupt({
        "customer_id": state["customer_id"],
        "message": state["message"],
        "request_type": state["request_type"],
        "risk_tier": state["risk_tier"],
        "tool_args": state.get("tool_args", {}),
    })

    return {"approved": decision}


TOOL_REGISTRY = {
    "check_account": actions.check_account,
    "generate_statement": actions.generate_statement,
    "update_contact_info": actions.update_contact_info,
    "create_ticket": actions.create_ticket,
    "cancel_subscription": actions.cancel_subscription,
    "flag_transaction": actions.flag_transaction,
    "escalate_to_fraud_team": actions.escalate_to_fraud_team,
    "freeze_account": actions.freeze_account,
}


def execute_tool_node(state: AgentState) -> dict:
    """
    Runs the tool(s) mapped to this request's type, passing any
    extracted arguments alongside customer_id.
    """
    request_type = RequestType(state["request_type"])
    tool_names = TAXONOMY[request_type]["tools"]
    tool_args = state.get("tool_args", {})
    results = {}

    for tool_name in tool_names:
        tool_function = TOOL_REGISTRY[tool_name]
        extra_args = tool_args.get(tool_name, {})
        results[tool_name] = tool_function(state["customer_id"], **extra_args)

    return {"tool_result": results}