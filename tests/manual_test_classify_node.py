"""
Manual check for classify_node. Run this file directly to confirm
the node correctly classifies a message and attaches its risk tier.
"""

from app.agents.nodes import classify_node

state = {
    "customer_id": "cust_001",
    "message": "Someone's used my card without my permission.",
}

result = classify_node(state)
print(result)