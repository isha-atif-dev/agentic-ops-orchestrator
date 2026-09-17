"""
Manual check for the agentic tool-use loop, confirms Claude picks
the right tool(s) on its own for a given message.
"""

from app.agents.agent_loop import run_agent_loop

result = run_agent_loop("cust_001", "Someone's used my card without my permission.")
print(result)