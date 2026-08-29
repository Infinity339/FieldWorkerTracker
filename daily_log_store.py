"""
daily_log_store.py
--------------------
Keeps a running local record of every GPS point captured "today" (worker_id,
latitude, longitude, timestamp) - independent of whether it successfully
reached Google Sheets or not. This is what gets turned into the message
text sent to the supervisor over WhatsApp.

Kept as its own small SQLite file so it's simple to reason about, and
separate from queue_store.py (which only tracks points still WAITING to
sync to the sheet).
"""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path

DB_PATH = str(Path(__file__).parent / "daily_log.db")
_lock = threading.Lock()


def _get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            timestamp TEXT NOT NULL,
            log_date TEXT NOT NULL
        )
        """
    )
    return conn


def add_entry(worker_id, lat, lon, timestamp_iso):
    """Record one GPS point. timestamp_iso should look like 2026-08-26T14:05:00."""
    log_date = timestamp_iso[:10]  # the 'YYYY-MM-DD' part
    with _lock:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO daily_log (worker_id, latitude, longitude, timestamp, log_date) "
            "VALUES (?, ?, ?, ?, ?)",
            (worker_id, lat, lon, timestamp_iso, log_date),
        )
        conn.commit()
        conn.close()


def get_today_entries(worker_id):
    today = datetime.now().strftime("%Y-%m-%d")
    with _lock:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT worker_id, latitude, longitude, timestamp FROM daily_log "
            "WHERE log_date = ? AND worker_id = ? ORDER BY id ASC",
            (today, worker_id),
        ).fetchall()
        conn.close()
    return rows


def today_count(worker_id):
    return len(get_today_entries(worker_id))


def format_log_as_text(worker_id):
    """Builds the plain-text message that gets sent via WhatsApp."""
    rows = get_today_entries(worker_id)
    if not rows:
        return None

    today_str = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"Daily Navigation Log",
        f"Worker ID: {worker_id}",
        f"Date: {today_str}",
        "-" * 30,
    ]
    for i, (wid, lat, lon, ts) in enumerate(rows, start=1):
        try:
            time_part = datetime.fromisoformat(ts).strftime("%H:%M:%S")
        except Exception:
            time_part = ts
        lines.append(f"{i}. {time_part} | ID: {wid} | Lat: {lat:.5f} | Lon: {lon:.5f}")
    lines.append("-" * 30)
    lines.append(f"Total points logged today: {len(rows)}")
    return "\n".join(lines)


def clear_entries_older_than(days=7):
    """Optional housekeeping - call occasionally to stop the file growing forever."""
    with _lock:
        conn = _get_conn()
        conn.execute(
            "DELETE FROM daily_log WHERE log_date < date('now', ?)",
            (f"-{days} days",),
        )
        conn.commit()
        conn.close()
