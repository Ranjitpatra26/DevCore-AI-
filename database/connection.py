import os
import sqlite3
from typing import Generator, List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ai_software_company.db")

def get_connection() -> sqlite3.Connection:
    """Establish and return an SQLite connection."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a read query and return rows as list of dicts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def execute_update(query: str, params: tuple = ()) -> int:
    """Execute a write/update query and return the last row ID (if applicable) or affected rows."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid or cursor.rowcount

def get_current_theme() -> str:
    """Retrieve the active UI theme (light/dark) from database settings."""
    try:
        rows = execute_query("SELECT value FROM settings WHERE key = 'theme'")
        return rows[0]['value'] if rows and rows[0]['value'] in ['light', 'dark'] else 'light'
    except Exception:
        return 'light'

def toggle_theme_db(current_theme: Optional[str] = None) -> str:
    """Toggle the theme from light to dark or vice versa in settings database and return the new value."""
    if not current_theme:
        current_theme = get_current_theme()
    new_theme = 'light' if str(current_theme).lower() == 'dark' else 'dark'
    try:
        execute_update("UPDATE settings SET value = ? WHERE key = 'theme'", (new_theme,))
    except Exception:
        pass
    return new_theme

