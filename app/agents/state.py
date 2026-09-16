"""
Defines the shared state that flows through the LangGraph graph.

Every node in the graph receives this state, reads what it needs,
and returns updates to it. LangGraph merges those updates back in
as the request moves from node to node.
"""

from typing import TypedDict, Optional
from app.models.taxonomy import RequestType, RiskTier


class AgentState(TypedDict):
    customer_id: str
    message: str

    # Filled in by the classification node
    request_type: Optional[RequestType]
    risk_tier: Optional[RiskTier]

    # Filled in by the approval node (built properly in Phase 5,
    # for now it will just default to "approved")
    approved: Optional[bool]

    # Filled in by the tool-execution node
    tool_result: Optional[dict]
    tool_args: Optional[dict]