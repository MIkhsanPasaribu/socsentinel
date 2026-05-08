"""
SOCsentinel — SQLite database for investigation persistence.

Provides async SQLite access for storing investigation state
across server restarts. Uses write-through cache pattern:
- In-memory dict for fast reads during SSE streaming
- SQLite for persistence across restarts
"""

import json
import os
import sqlite3
from typing import Any

from app.core.logger import get_logger

logger = get_logger(__name__)

# Database file path
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "socsentinel.db")

# Schema
_SCHEMA = """
CREATE TABLE IF NOT EXISTS investigations (
    investigation_id TEXT PRIMARY KEY,
    state_json TEXT NOT NULL,
    status TEXT NOT NULL,
    severity TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    total_processing_time_ms REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def init_database() -> None:
    """Initialize the SQLite database and create tables if needed.

    Called once at application startup.
    """
    os.makedirs(DB_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(_SCHEMA)
        conn.commit()
        logger.info("SQLite database initialized", path=DB_PATH)
    finally:
        conn.close()


def save_investigation(investigation_id: str, state_dict: dict[str, Any]) -> None:
    """Save or update an investigation in the database.

    Args:
        investigation_id: Unique investigation ID.
        state_dict: Full PipelineState as a dictionary (from model_dump()).
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO investigations
                (investigation_id, state_json, status, severity, started_at,
                 completed_at, total_processing_time_ms, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                investigation_id,
                json.dumps(state_dict, default=str),
                state_dict.get("status", "pending"),
                state_dict.get("alert", {}).get("severity", "medium"),
                state_dict.get("started_at", ""),
                state_dict.get("completed_at"),
                state_dict.get("total_processing_time_ms", 0),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def load_investigation(investigation_id: str) -> dict[str, Any] | None:
    """Load a single investigation from the database.

    Args:
        investigation_id: The investigation ID to load.

    Returns:
        The state dictionary or None if not found.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT state_json FROM investigations WHERE investigation_id = ?",
            (investigation_id,),
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row["state_json"])
        return None
    finally:
        conn.close()


def load_all_investigations() -> dict[str, dict[str, Any]]:
    """Load all investigations from the database.

    Returns:
        Dictionary mapping investigation_id to state_dict.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT investigation_id, state_json FROM investigations ORDER BY created_at DESC"
        )
        results = {}
        for row in cursor.fetchall():
            results[row["investigation_id"]] = json.loads(row["state_json"])
        return results
    finally:
        conn.close()


def delete_investigation(investigation_id: str) -> bool:
    """Delete an investigation from the database.

    Args:
        investigation_id: The investigation ID to delete.

    Returns:
        True if deleted, False if not found.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.execute(
            "DELETE FROM investigations WHERE investigation_id = ?",
            (investigation_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_investigation_count() -> int:
    """Get total number of investigations in the database."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM investigations")
        return cursor.fetchone()[0]
    finally:
        conn.close()
