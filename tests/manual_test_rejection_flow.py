"""
Manual check that a rejected request does NOT execute its tool.
"""

from langgraph.types import Command
from app.agents.graph import graph

config = {"configurable": {"thread_id": "demo-2"}}

result = graph.invoke(
    {"customer_id": "cust_001", "message": "Someone's used my card without my permission."},
    config=config,
)
print("PAUSED:", result.get("__interrupt__"))

final_result = graph.invoke(Command(resume=False), config=config)
print("AFTER REJECTION (tool_result should be missing):")
print(final_result)