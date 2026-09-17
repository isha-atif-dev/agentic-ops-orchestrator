"""
Manual check for the full human-in-the-loop flow with the new
agentic execution step. Sends a needs_approval request through the
graph, confirms it pauses, then resumes it with an approval
decision and confirms Claude's agent loop runs afterward.
"""

from langgraph.types import Command
from app.agents.graph import graph

config = {"configurable": {"thread_id": "demo-agentic-1"}}

result = graph.invoke(
    {"customer_id": "cust_002", "message": "I want to cancel my premium plan."},
    config=config,
)
print("AFTER FIRST INVOKE (should be paused):")
print(result)
print()

final_result = graph.invoke(Command(resume=True), config=config)
print("AFTER APPROVAL (agent loop should have run):")
print(final_result)