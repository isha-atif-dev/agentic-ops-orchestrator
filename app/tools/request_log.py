"""
Logs every submitted request and provides the queries the ops
dashboard needs: the pending queue, and today's stats.
"""

import json
from datetime import datetime, timezone
from app.tools.db import get_connection


def log_new_request(thread_id, customer_id, message, request_type, risk_tier, tool_args, ai_recommendation, status):
    """Records a newly submitted request, whatever its outcome."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO requests_log
        (thread_id, customer_id, message, request_type, risk_tier, tool_args, ai_recommendation, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (thread_id, customer_id, message, request_type, risk_tier, json.dumps(tool_args), ai_recommendation, status, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def resolve_request(thread_id, status):
    """Marks a pending request as approved or rejected."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE requests_log SET status = ?, resolved_at = ? WHERE thread_id = ?",
        (status, datetime.now(timezone.utc).isoformat(), thread_id),
    )
    conn.commit()
    conn.close()


def get_pending_requests():
    """Returns every request currently waiting for human review."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT thread_id, customer_id, message, request_type, risk_tier, tool_args, ai_recommendation, created_at "
        "FROM requests_log WHERE status = 'pending' ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "thread_id": r[0],
            "customer_id": r[1],
            "message": r[2],
            "request_type": r[3],
            "risk_tier": r[4],
            "tool_args": json.loads(r[5]) if r[5] else {},
            "ai_recommendation": r[6],
            "created_at": r[7],
        }
        for r in rows
    ]


def get_stats():
    """Returns the counts shown in the dashboard's stat cards."""
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now(timezone.utc).date().isoformat()

    cursor.execute("SELECT COUNT(*) FROM requests_log WHERE status = 'pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM requests_log WHERE status = 'approved' AND resolved_at LIKE ?", (f"{today}%",))
    approved_today = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM requests_log WHERE status = 'rejected' AND resolved_at LIKE ?", (f"{today}%",))
    rejected_today = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM requests_log")
    total = cursor.fetchone()[0]

    conn.close()
    return {
        "pending_review": pending,
        "approved_today": approved_today,
        "rejected_today": rejected_today,
        "total_requests": total,
    }


def get_request_history():
    """Returns every resolved (approved or rejected) request, most recent first."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT thread_id, customer_id, message, request_type, risk_tier, status, created_at, resolved_at "
        "FROM requests_log WHERE status != 'pending' ORDER BY resolved_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "thread_id": r[0],
            "customer_id": r[1],
            "message": r[2],
            "request_type": r[3],
            "risk_tier": r[4],
            "status": r[5],
            "created_at": r[6],
            "resolved_at": r[7],
        }
        for r in rows
    ]