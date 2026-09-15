"""
Defines the individual nodes (steps) used in the LangGraph graph.

Each function here takes the current AgentState, does one job, and
returns the fields it updated. LangGraph merges these updates back
into the shared state as the request moves through the graph.
"""

from app.agents.classifier import classify_request
from app.models.taxonomy import TAXONOMY
from app.agents.state import AgentState
from app.tools import actions


def classify_node(state: AgentState) -> dict:
    """
    Classifies the incoming message and looks up its risk tier
    from the taxonomy. This is always the first node in the graph.
    """
    request_type = classify_request(state["message"])
    risk_tier = TAXONOMY[request_type]["risk_tier"]

    return {
        "request_type": request_type,
        "risk_tier": risk_tier,
    }



# Maps tool names (as strings, from the taxonomy) to the actual
# functions in app/tools/actions.py. This indirection is what lets
# the graph call the right function without hardcoding a big
# if/elif chain for every request type.
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
    Runs the tool(s) mapped to this request's type in the taxonomy.
    For this phase, calls each tool with just the customer_id,
    real argument handling per-tool comes later if needed.
    """
    tool_names = TAXONOMY[state["request_type"]]["tools"]
    results = {}

    for tool_name in tool_names:
        tool_function = TOOL_REGISTRY[tool_name]
        results[tool_name] = tool_function(state["customer_id"])

    return {"tool_result": results}