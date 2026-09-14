"""
Defines the request taxonomy for the Agentic Ops Orchestrator.

This is the single source of truth for what kinds of requests the
system can handle, what risk tier each one falls into, and which
action(s) it maps to. Everything downstream (intent classification,
routing, human-in-the-loop approval) reads from this file, so the
taxonomy only needs to be defined once.
"""

from enum import Enum


class RiskTier(str, Enum):
    """
    How much oversight a request's action needs before it executes.

    AUTO: the system can act immediately, no human involved.
    NEEDS_APPROVAL: the action must pause and wait for a human to
    approve it before it actually runs.
    URGENT_APPROVAL: same as NEEDS_APPROVAL, but flagged as high
    priority (e.g. fraud), so it should be surfaced to a human faster.
    """
    AUTO = "auto"
    NEEDS_APPROVAL = "needs_approval"
    URGENT_APPROVAL = "urgent_approval"


class RequestType(str, Enum):
    """
    The categories of request this system knows how to classify.
    Each one corresponds to a real thing a Meridian customer might ask for.
    """
    ACCOUNT_STATUS_QUERY = "account_status_query"
    STATEMENT_REQUEST = "statement_request"
    UPDATE_CONTACT_INFO = "update_contact_info"
    GENERAL_COMPLAINT = "general_complaint"
    SUBSCRIPTION_CANCELLATION = "subscription_cancellation"
    TRANSACTION_DISPUTE = "transaction_dispute"
    FRAUD_REPORT = "fraud_report"
    IDENTITY_THEFT_REPORT = "identity_theft_report"


# Maps each request type to its risk tier and the tool(s) it will call.
# Tool names here are just strings for now, the actual functions get
# built in Phase 3. Keeping this as data (not code) makes it easy to
# add new request types later without touching the routing logic.
TAXONOMY = {
    RequestType.ACCOUNT_STATUS_QUERY: {
        "risk_tier": RiskTier.AUTO,
        "tools": ["check_account"],
    },
    RequestType.STATEMENT_REQUEST: {
        "risk_tier": RiskTier.AUTO,
        "tools": ["generate_statement"],
    },
    RequestType.UPDATE_CONTACT_INFO: {
        "risk_tier": RiskTier.AUTO,
        "tools": ["update_contact_info"],
    },
    RequestType.GENERAL_COMPLAINT: {
        "risk_tier": RiskTier.AUTO,
        "tools": ["create_ticket"],
    },
    RequestType.SUBSCRIPTION_CANCELLATION: {
        "risk_tier": RiskTier.NEEDS_APPROVAL,
        "tools": ["cancel_subscription"],
    },
    RequestType.TRANSACTION_DISPUTE: {
        "risk_tier": RiskTier.NEEDS_APPROVAL,
        "tools": ["create_ticket", "flag_transaction"],
    },
    RequestType.FRAUD_REPORT: {
        "risk_tier": RiskTier.URGENT_APPROVAL,
        "tools": ["escalate_to_fraud_team"],
    },
    RequestType.IDENTITY_THEFT_REPORT: {
        "risk_tier": RiskTier.URGENT_APPROVAL,
        "tools": ["freeze_account", "escalate_to_fraud_team"],
    },
}