"""
SQLite database layer for sensor readings.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "sensor_data.db"


def get_connection() -> sqlite3.Connection:
    """Return a connection with row_factory set for dict-like access."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # better concurrent read perf
    return conn


def init_db() -> None:
    """Create the sensor_readings table if it doesn't exist."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id     TEXT    NOT NULL,
            moisture    REAL    NOT NULL,
            temperature REAL    NOT NULL,
            humidity    REAL    NOT NULL,
            light       REAL    NOT NULL,
            battery     REAL    NOT NULL,
            timestamp   TEXT    NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_node_timestamp
        ON sensor_readings (node_id, timestamp DESC)
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS node_photos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id     TEXT    NOT NULL,
            filename    TEXT    NOT NULL,
            captured_at TEXT    NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS advisories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id     TEXT    NOT NULL,
            advisory    TEXT    NOT NULL,
            timestamp   TEXT    NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
