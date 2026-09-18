"""
Manual check that the graph now returns a step-by-step trace
alongside the usual result.
"""

from langgraph.types import Command
from app.agents.graph import graph

config = {"configurable": {"thread_id": "trace-test-1"}}

result = graph.invoke(
    {"customer_id": "cust_001", "message": "Someone's used my card without my permission."},
    config=config,
)
print("FIRST INVOKE TRACE:")
for entry in result.get("trace", []):
    print(" -", entry)

if "__interrupt__" in result:
    final = graph.invoke(Command(resume=True), config=config)
    print("\nAFTER APPROVAL, FULL TRACE:")
    for entry in final.get("trace", []):
        print(" -", entry)