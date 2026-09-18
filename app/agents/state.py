"""
Defines the shared state that flows through the LangGraph graph.

Every node reads what it needs and returns updates. `trace` is
additive (Annotated with operator.add), each node appends its own
entry rather than overwriting the list, so by the end it holds the
exact real sequence of what happened, used to power the node-graph
replay visualization on the frontend.
"""

from typing import TypedDict, Optional, List, Annotated
import operator
from app.models.taxonomy import RequestType, RiskTier


class AgentState(TypedDict):
    customer_id: str
    message: str
    request_type: Optional[RequestType]
    risk_tier: Optional[RiskTier]
    approved: Optional[bool]
    tool_result: Optional[dict]
    trace: Annotated[List[dict], operator.add]