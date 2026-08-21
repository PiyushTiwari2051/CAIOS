import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..config import settings
from ..models.mode import ModeEnum

def get_db_connection() -> sqlite3.Connection:
    settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(settings.DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize SQLite database tables for mode history and actions."""
    conn = get_db_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mode_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                mode TEXT NOT NULL,
                confidence REAL NOT NULL,
                process_name TEXT,
                window_title TEXT,
                reasoning TEXT,
                is_manual_override INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS action_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                params TEXT,
                status TEXT NOT NULL,
                details TEXT
            )
        """)
    conn.close()

# Auto-initialize on import for safety across all test & runtime environments
init_db()


def record_mode_transition(
    mode: str,
    confidence: float,
    process_name: str,
    window_title: str,
    reasoning: str,
    is_manual_override: bool = False
) -> int:
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat() + "Z"
    with conn:
        cursor = conn.execute("""
            INSERT INTO mode_history (timestamp, mode, confidence, process_name, window_title, reasoning, is_manual_override)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, mode, confidence, process_name, window_title, reasoning, 1 if is_manual_override else 0))
        row_id = cursor.lastrowid
    conn.close()
    return row_id

def record_action_execution(
    action_type: str,
    title: str,
    description: str,
    params: Dict[str, Any],
    status: str,
    details: str = ""
) -> int:
    conn = get_db_connection()
    timestamp = datetime.utcnow().isoformat() + "Z"
    params_json = json.dumps(params)
    with conn:
        cursor = conn.execute("""
            INSERT INTO action_history (timestamp, action_type, title, description, params, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, action_type, title, description, params_json, status, details))
        row_id = cursor.lastrowid
    conn.close()
    return row_id

def get_recent_modes(limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM mode_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_recent_actions(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM action_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = []
    for row in cursor.fetchall():
        item = dict(row)
        try:
            item["params"] = json.loads(item["params"])
        except Exception:
            pass
        rows.append(item)
    conn.close()
    return rows
