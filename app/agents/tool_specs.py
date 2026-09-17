"""
Tool schemas exposed to Claude for the agentic tool-use loop.

Each entry matches a function in app/tools/actions.py by name.
customer_id is NOT included here, it's injected automatically when
a tool is actually called, since the agent already operates in the
context of one specific customer and doesn't need to specify it.
"""

TOOL_SPECS = [
    {
        "name": "check_account",
        "description": "Look up a customer's account and KYC status.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "generate_statement",
        "description": "Generate an account statement for a given month.",
        "input_schema": {
            "type": "object",
            "properties": {"month": {"type": "string", "description": "e.g. '2026-08'"}},
            "required": ["month"],
        },
    },
    {
        "name": "update_contact_info",
        "description": "Update the customer's phone number or email.",
        "input_schema": {
            "type": "object",
            "properties": {
                "field": {"type": "string", "enum": ["phone", "email"]},
                "new_value": {"type": "string"},
            },
            "required": ["field", "new_value"],
        },
    },
    {
        "name": "create_ticket",
        "description": "Open a general support ticket for a complaint.",
        "input_schema": {
            "type": "object",
            "properties": {"description": {"type": "string"}},
            "required": ["description"],
        },
    },
    {
        "name": "cancel_subscription",
        "description": "Cancel the customer's subscription.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "flag_transaction",
        "description": "Flag a disputed transaction for review.",
        "input_schema": {
            "type": "object",
            "properties": {
                "transaction_id": {"type": "string", "description": "Use 'unknown' if not mentioned"},
                "reason": {"type": "string"},
            },
            "required": ["transaction_id", "reason"],
        },
    },
    {
        "name": "escalate_to_fraud_team",
        "description": "Escalate a fraud concern to the fraud team.",
        "input_schema": {
            "type": "object",
            "properties": {"details": {"type": "string"}},
            "required": ["details"],
        },
    },
    {
        "name": "freeze_account",
        "description": "Freeze the customer's account entirely, used for suspected identity theft.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]