"""
Classifies an incoming customer request into one of the request
types defined in the taxonomy.

Uses the Claude API's structured output feature: instead of asking
for free text and hoping it matches a valid category, we pass a
JSON schema that constrains the response to exactly one of our
valid category names. This removes the need to validate free-text
output ourselves, the API guarantees the shape.
"""

import json
from anthropic import Anthropic
from app.config import settings
from app.models.taxonomy import RequestType

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# Small, fast model, classification doesn't need heavy reasoning power.
CLASSIFIER_MODEL = "claude-haiku-4-5-20251001"

VALID_TYPES = [t.value for t in RequestType]

# Constrains the model's response to a JSON object with a single
# "category" field, which must be one of our valid request types.
CLASSIFICATION_SCHEMA = {
    "format": {
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": VALID_TYPES,
                }
            },
            "required": ["category"],
            "additionalProperties": False,
        },
    }
}


def classify_request(message: str) -> RequestType:
    """
    Takes a raw customer message and returns the matching RequestType.
    """
    system_prompt = (
        "You are a classifier for a financial services company's "
        "customer requests. Read the customer's message and classify "
        "it into the correct category."
    )

    response = client.messages.create(
        model=CLASSIFIER_MODEL,
        max_tokens=50,
        system=system_prompt,
        messages=[{"role": "user", "content": message}],
        output_config=CLASSIFICATION_SCHEMA,
    )

    parsed = json.loads(response.content[0].text)
    return RequestType(parsed["category"])