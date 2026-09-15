"""
Manual check for the full graph, runs a message through classify
then execute_tool end to end.
"""

from app.agents.graph import graph

result = graph.invoke({
    "customer_id": "cust_002",
    "message": "I want to cancel my premium plan.",
})

print(result)