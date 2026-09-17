"""
Runs a real agentic tool-use loop.

Unlike the earlier fixed-routing approach (taxonomy decides which
tools run), this lets Claude itself decide which tool(s) to call
based on the customer's message, see each tool's result, and decide
whether another tool call is needed or whether it's done. The first
turn forces a tool call (tool_choice="any"), so the agent can never
simply respond with text and take no action at all, after that it's
free to decide naturally when it's done. MAX_ITERATIONS exists purely
as a safety cap against runaway loops, not as a normal stopping point.
"""

import json
from anthropic import Anthropic
from app.config import settings
from app.tools import actions
from app.agents.tool_specs import TOOL_SPECS

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
AGENT_MODEL = "claude-haiku-4-5-20251001"
MAX_ITERATIONS = 5

AGENT_SYSTEM_PROMPT = (
    "You are an operations agent for a financial services company. "
    "A customer has sent a request through an automated system, you "
    "cannot ask them follow-up questions or have a back-and-forth "
    "conversation. Use the information given to take the most "
    "reasonable action available, using placeholder values like "
    "'unknown' for any details not mentioned. You must call at "
    "least one tool before finishing, taking no action at all is "
    "not an acceptable outcome. "
    "If the customer reports their card being stolen, used without "
    "their permission, or any sign their account has been "
    "compromised, you must escalate to the fraud team, this takes "
    "priority over simply flagging a transaction. "
    "For a specific transaction the customer merely doesn't "
    "recognize or disputes, without suggesting their card was "
    "stolen or compromised, flag the transaction AND open a "
    "support ticket so the case is tracked. "
    "Once you've handled the request, stop calling tools."
)

TOOL_REGISTRY = {
    "check_account": actions.check_account,
    "generate_statement": actions.generate_statement,
    "update_contact_info": actions.update_contact_info,
    "create_ticket": actions.create_ticket,
    "cancel_subscription": actions.cancel_subscription,
    "flag_transaction": actions.flag_transaction,
    "escalate_to_fraud_team": actions.escalate_to_fraud_team,
    "freeze_account": actions.freeze_account,
}


def run_agent_loop(customer_id: str, message: str) -> dict:
    """
    Lets Claude decide which tool(s) to call to handle a customer's
    request, executes them, feeds results back, and repeats until
    Claude decides it's done or MAX_ITERATIONS is hit.

    Returns every tool call made and its result.
    """
    messages = [{"role": "user", "content": message}]
    tool_calls_made = {}

    for i in range(MAX_ITERATIONS):
        # Force a tool call on the first turn only, so the agent can
        # never simply respond with text and take no action at all.
        # After that, let it decide naturally when it's actually done.
        tool_choice = {"type": "any"} if i == 0 else {"type": "auto"}

        response = client.messages.create(
            model=AGENT_MODEL,
            max_tokens=500,
            system=AGENT_SYSTEM_PROMPT,
            messages=messages,
            tools=TOOL_SPECS,
            tool_choice=tool_choice,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        tool_result_blocks = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_function = TOOL_REGISTRY[block.name]
            result = tool_function(customer_id, **block.input)
            tool_calls_made[block.name] = result

            tool_result_blocks.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result),
            })

        messages.append({"role": "user", "content": tool_result_blocks})

    return tool_calls_made