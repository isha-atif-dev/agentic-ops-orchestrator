"""
Tool functions that the agent can call to take real actions.

Each function here mocks a real backend operation (querying or
updating the SQLite database) rather than hardcoding a hypothetical
result, so the agent is working with data that actually changes.
Every action that touches customer data gets recorded in the
action_log table for auditability.
"""

from datetime import datetime, timezone
from app.tools.db import get_connection


def log_action(customer_id: str, action: str, details: str = ""):
    """Records an action in the action_log table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO action_log (customer_id, action, details, timestamp) VALUES (?, ?, ?, ?)",
        (customer_id, action, details, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def check_account(customer_id: str) -> dict:
    """
    Looks up a customer's account and returns their KYC status.
    Used for account status queries, the lowest-risk tool, read-only.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT customer_id, name, kyc_status FROM customers WHERE customer_id = ?",
        (customer_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return {"found": False}

    return {"found": True, "customer_id": row[0], "name": row[1], "kyc_status": row[2]}

def generate_statement(customer_id: str, month: str) -> dict:
    """
    Simulates generating a statement for a given month.
    No real PDF generation, just returns a mocked confirmation,
    good enough to prove the routing and tool-calling logic.
    """
    log_action(customer_id, "generate_statement", f"month={month}")
    return {"customer_id": customer_id, "month": month, "statement_url": f"https://meridian.example/statements/{customer_id}/{month}.pdf"}


def update_contact_info(customer_id: str, field: str, new_value: str) -> dict:
    """
    Updates a customer's phone or email in the database.
    Restricted to a fixed set of fields, so it can't be used to
    overwrite arbitrary columns.
    """
    if field not in ("phone", "email"):
        return {"success": False, "error": f"Cannot update field: {field}"}

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE customers SET {field} = ? WHERE customer_id = ?", (new_value, customer_id))
    conn.commit()
    conn.close()

    log_action(customer_id, "update_contact_info", f"{field} -> {new_value}")
    return {"success": True, "customer_id": customer_id, "field": field, "new_value": new_value}


def create_ticket(customer_id: str, description: str) -> dict:
    """
    Opens a support ticket for a general complaint.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tickets (customer_id, description, status) VALUES (?, ?, ?)",
        (customer_id, description, "open"),
    )
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_action(customer_id, "create_ticket", description)
    return {"success": True, "ticket_id": ticket_id, "status": "open"}

def cancel_subscription(customer_id: str) -> dict:
    """
    Cancels a customer's subscription. Reverses recurring revenue,
    so this is a needs_approval action, not auto.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET subscription_active = 0 WHERE customer_id = ?", (customer_id,))
    conn.commit()
    conn.close()

    log_action(customer_id, "cancel_subscription")
    return {"success": True, "customer_id": customer_id, "subscription_active": False}


def flag_transaction(customer_id: str, transaction_id: str, reason: str) -> dict:
    """
    Flags a disputed transaction for review. Doesn't reverse the
    charge itself, just marks it as disputed and logs the reason.
    """
    log_action(customer_id, "flag_transaction", f"transaction={transaction_id}, reason={reason}")
    return {"success": True, "transaction_id": transaction_id, "status": "flagged_for_review"}


def escalate_to_fraud_team(customer_id: str, details: str) -> dict:
    """
    Simulates escalating a case to the fraud team. In a real system
    this might create a ticket in a dedicated fraud queue, here it's
    logged as a distinct action type so it's easy to find later.
    """
    log_action(customer_id, "escalate_to_fraud_team", details)
    return {"success": True, "customer_id": customer_id, "status": "escalated", "priority": "urgent"}


def freeze_account(customer_id: str) -> dict:
    """
    Freezes a customer's account. The most severe action available,
    used for suspected identity theft, blocks all activity until a
    human reviews it.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET frozen = 1 WHERE customer_id = ?", (customer_id,))
    conn.commit()
    conn.close()

    log_action(customer_id, "freeze_account")
    return {"success": True, "customer_id": customer_id, "frozen": True}