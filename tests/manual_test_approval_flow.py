"""
Manual check for the full human-in-the-loop flow. Sends a
needs_approval request through the graph, confirms it pauses,
then resumes it with an approval decision and confirms the tool
only runs after approval.
"""

from langgraph.types import Command
from app.agents.graph import graph

config = {"configurable": {"thread_id": "demo-1"}}

# Step 1: send a request that should require approval
result = graph.invoke(
    {"customer_id": "cust_002", "message": "I want to cancel my premium plan."},
    config=config,
)
print("AFTER FIRST INVOKE (should be paused):")
print(result)
print()

# Step 2: simulate a human approving it
final_result = graph.invoke(Command(resume=True), config=config)
print("AFTER APPROVAL (tool should have run now):")
print(final_result)