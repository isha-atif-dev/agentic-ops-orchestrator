"""
Manual check that calling the same tool twice in one agent run
doesn't execute the real action twice, confirms the called_tools
guard in run_agent_loop is working.
"""

from app.agents.agent_loop import run_agent_loop

result = run_agent_loop(
    "cust_001",
    "Someone stole my card and I think they've opened a new account in my name too.",
)
print(result)