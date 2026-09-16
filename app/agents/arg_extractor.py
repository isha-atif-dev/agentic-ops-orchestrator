"""
Extracts tool-specific arguments from a customer's raw message.

Some tools need more than just the customer_id (e.g. which month
for a statement, or which field to update). This uses the same
structured-output pattern as the classifier to pull those values
out of the customer's message, guided by each tool's schema.
"""

import json
from anthropic import Anthropic
from app.config import settings
from app.agents.tool_schemas import TOOL_ARG_SCHEMAS

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

EXTRACTION_MODEL = "claude-haiku-4-5-20251001"


def extract_tool_args(message: str, tool_name: str) -> dict:
    """
    Given a customer message and a tool name, returns the arguments
    that tool needs, extracted from the message according to its
    JSON schema.
    """
    schema = TOOL_ARG_SCHEMAS[tool_name]

    response = client.messages.create(
        model=EXTRACTION_MODEL,
        max_tokens=200,
        system=(
            "Extract the requested information from the customer's "
            "message. If something isn't clearly mentioned, make a "
            "reasonable guess based on context."
        ),
        messages=[{"role": "user", "content": message}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )

    return json.loads(response.content[0].text)