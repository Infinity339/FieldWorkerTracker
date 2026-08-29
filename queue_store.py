"""
queue_store.py
---------------
A tiny local SQLite queue used to hold location pings that failed to send
(no internet, server down, etc.) so they can be retried later without
losing data. Used by both main.py (foreground) and service.py (background).
"""

import json
import sqlite3
import threading
import time
from pathlib import Path

import requests

DB_PATH = str(Path(__file__).parent / "pending_locations.db")
_lock = threading.Lock()


def _get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            accuracy REAL,
            captured_at TEXT NOT NULL
        )
        """
    )
    return conn


def add_pending(worker_id, lat, lon, accuracy, captured_at):
    """Save a location locally because sending it right now failed."""
    with _lock:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO queue (worker_id, latitude, longitude, accuracy, captured_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (worker_id, lat, lon, accuracy, captured_at),
        )
        conn.commit()
        conn.close()


def pending_count():
    with _lock:
        conn = _get_conn()
        n = conn.execute("SELECT COUNT(*) FROM queue").fetchone()[0]
        conn.close()
        return n


def try_send_one(webhook_url, api_key, worker_id, lat, lon, accuracy, captured_at, timeout=15):
    """
    Attempt to send one location straight to the sheet.
    Returns True on success, False on any failure (caller should then queue it).
    """
    payload = {
        "api_key": api_key,
        "worker_id": worker_id,
        "latitude": lat,
        "longitude": lon,
        "accuracy": accuracy,
        "captured_at": captured_at,
    }
    try:
        resp = requests.post(webhook_url, data=json.dumps(payload), timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


def flush_queue(webhook_url, api_key, max_items=25):
    """
    Try to send everything sitting in the local queue.
    Sends oldest-first; stops early if a send fails (assume still offline).
    Returns the number of items successfully flushed.
    """
    with _lock:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT id, worker_id, latitude, longitude, accuracy, captured_at "
            "FROM queue ORDER BY id ASC LIMIT ?",
            (max_items,),
        ).fetchall()
        conn.close()

    flushed = 0
    for row_id, worker_id, lat, lon, accuracy, captured_at in rows:
        ok = try_send_one(webhook_url, api_key, worker_id, lat, lon, accuracy, captured_at)
        if not ok:
            break  # still offline / server down, stop trying for now
        with _lock:
            conn = _get_conn()
            conn.execute("DELETE FROM queue WHERE id = ?", (row_id,))
            conn.commit()
            conn.close()
        flushed += 1
    return flushed


def send_or_queue(webhook_url, api_key, worker_id, lat, lon, accuracy, captured_at):
    """
    Main entry point: try to send now; if that fails, save locally instead.
    Also opportunistically flushes any older queued items when a send succeeds.
    Returns (sent_now: bool, queue_size_after: int)
    """
    ok = try_send_one(webhook_url, api_key, worker_id, lat, lon, accuracy, captured_at)
    if ok:
        # We're online - clear out any backlog too.
        flush_queue(webhook_url, api_key)
        return True, pending_count()
    else:
        add_pending(worker_id, lat, lon, accuracy, captured_at)
        return False, pending_count()
