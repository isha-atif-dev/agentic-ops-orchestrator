"""
Debug version: prints the raw response so we can see exactly what
Claude decided to do, rather than just the final result.
"""

from anthropic import Anthropic
from app.config import settings
from app.agents.tool_specs import TOOL_SPECS
from app.agents.agent_loop import AGENT_SYSTEM_PROMPT

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=500,
    system=AGENT_SYSTEM_PROMPT,
    messages=[{"role": "user", "content": "Someone's used my card without my permission."}],
    tools=TOOL_SPECS,
)

print("STOP REASON:", response.stop_reason)
print("CONTENT:")
for block in response.content:
    print(" -", block)