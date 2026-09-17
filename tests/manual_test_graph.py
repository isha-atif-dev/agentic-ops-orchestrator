"""
Manual check for the full graph, runs a message through classify,
approval gate, and the agent loop end to end.
"""

from app.agents.graph import graph

config = {"configurable": {"thread_id": "manual-test-1"}}

result = graph.invoke({
    "customer_id": "cust_002",
    "message": "I want to cancel my premium plan.",
}, config=config)

print(result)