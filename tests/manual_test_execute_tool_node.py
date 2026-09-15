"""
Manual check for execute_tool_node. Confirms the right tool(s) get
called based on request_type, and results come back correctly.
"""

from app.agents.nodes import execute_tool_node
from app.models.taxonomy import RequestType

state = {
    "customer_id": "cust_001",
    "request_type": RequestType.ACCOUNT_STATUS_QUERY,
}

result = execute_tool_node(state)
print(result)