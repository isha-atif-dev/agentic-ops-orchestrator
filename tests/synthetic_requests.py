"""
Synthetic customer requests used to test the intent classifier.

These are hand-written example messages, a handful per request type,
covering different phrasings a real customer might use. This becomes
the dataset for checking whether classification actually works
(Phase 2) and later for the agent evaluation (Phase 6).
"""

from app.models.taxonomy import RequestType

SYNTHETIC_REQUESTS = [
    # Account status query
    {"text": "Is my account still under review?", "expected_type": RequestType.ACCOUNT_STATUS_QUERY},
    {"text": "Can you check the status of my KYC verification?", "expected_type": RequestType.ACCOUNT_STATUS_QUERY},
    {"text": "Why hasn't my account been approved yet?", "expected_type": RequestType.ACCOUNT_STATUS_QUERY},

    # Statement request
    {"text": "Can you send me last month's statement?", "expected_type": RequestType.STATEMENT_REQUEST},
    {"text": "I need a copy of my transaction history for March.", "expected_type": RequestType.STATEMENT_REQUEST},

    # Update contact info
    {"text": "I need to change my phone number on file.", "expected_type": RequestType.UPDATE_CONTACT_INFO},
    {"text": "Please update my email address.", "expected_type": RequestType.UPDATE_CONTACT_INFO},

    # General complaint
    {"text": "Your app keeps logging me out every five minutes.", "expected_type": RequestType.GENERAL_COMPLAINT},
    {"text": "The transfer feature has been broken all week.", "expected_type": RequestType.GENERAL_COMPLAINT},

    # Subscription cancellation
    {"text": "I want to cancel my premium plan.", "expected_type": RequestType.SUBSCRIPTION_CANCELLATION},
    {"text": "Please cancel my subscription, I no longer need it.", "expected_type": RequestType.SUBSCRIPTION_CANCELLATION},

    # Transaction dispute
    {"text": "I didn't make this £200 charge, please look into it.", "expected_type": RequestType.TRANSACTION_DISPUTE},
    {"text": "There's a payment on my account I don't recognise.", "expected_type": RequestType.TRANSACTION_DISPUTE},

    # Fraud report
    {"text": "Someone's used my card without my permission.", "expected_type": RequestType.FRAUD_REPORT},
    {"text": "My card details were stolen, I need to report fraud.", "expected_type": RequestType.FRAUD_REPORT},

    # Identity theft report
    {"text": "I think someone opened an account in my name.", "expected_type": RequestType.IDENTITY_THEFT_REPORT},
    {"text": "Someone is impersonating me to open new accounts.", "expected_type": RequestType.IDENTITY_THEFT_REPORT},
]