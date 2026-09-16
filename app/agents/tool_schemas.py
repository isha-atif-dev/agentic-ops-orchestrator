"""
Defines the extra arguments (beyond customer_id) each tool needs,
as JSON schemas. Used by the argument-extraction node to ask Claude
to pull the right values out of the customer's raw message.

Tools not listed here need no extra arguments, customer_id alone
is enough.
"""

TOOL_ARG_SCHEMAS = {
    "generate_statement": {
        "type": "object",
        "properties": {
            "month": {"type": "string", "description": "The month requested, e.g. '2026-08' or 'last month' if unclear"}
        },
        "required": ["month"],
        "additionalProperties": False,
    },
    "update_contact_info": {
        "type": "object",
        "properties": {
            "field": {"type": "string", "enum": ["phone", "email"]},
            "new_value": {"type": "string", "description": "The new value the customer provided"}
        },
        "required": ["field", "new_value"],
        "additionalProperties": False,
    },
    "create_ticket": {
        "type": "object",
        "properties": {
            "description": {"type": "string", "description": "A short summary of the complaint"}
        },
        "required": ["description"],
        "additionalProperties": False,
    },
    "flag_transaction": {
        "type": "object",
        "properties": {
            "transaction_id": {"type": "string", "description": "The transaction ID if mentioned, otherwise 'unknown'"},
            "reason": {"type": "string", "description": "Why the customer is disputing it"}
        },
        "required": ["transaction_id", "reason"],
        "additionalProperties": False,
    },
    "escalate_to_fraud_team": {
        "type": "object",
        "properties": {
            "details": {"type": "string", "description": "A short summary of the fraud concern"}
        },
        "required": ["details"],
        "additionalProperties": False,
    },
}