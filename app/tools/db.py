"""
Sets up the mocked backend database for the Agentic Ops Orchestrator.

Provides a SQLite database with customer records, support tickets,
and an action log, used by the tool functions to simulate real
backend operations (checking accounts, freezing accounts, logging
actions, etc).
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "mock_data.db"


def get_connection():
    """Opens a connection to the SQLite database file."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """
    Creates the required tables if they don't already exist, and
    seeds a few fake customers so there's data to query. Safe to
    run multiple times, CREATE TABLE IF NOT EXISTS won't wipe
    existing data.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT,
            kyc_status TEXT,
            subscription_active INTEGER,
            phone TEXT,
            email TEXT,
            frozen INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            description TEXT,
            status TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            action TEXT,
            details TEXT,
            timestamp TEXT
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO customers (customer_id, name, kyc_status, subscription_active, phone, email) VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("cust_001", "Amara Chen", "under_review", 1, "07700900001", "amara@example.com"),
                ("cust_002", "James Okafor", "approved", 1, "07700900002", "james@example.com"),
                ("cust_003", "Priya Nair", "approved", 0, "07700900003", "priya@example.com"),
            ],
        )

    conn.commit()
    conn.close()