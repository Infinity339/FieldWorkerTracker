"""
service.py
-----------
Runs as an Android background Service (declared in buildozer.spec via
`services = tracker:service.py`), so it keeps running on its own 5-minute
timer even after the worker minimizes or switches away from the app.

It reads the last-known GPS fix directly through Android's LocationManager
(via pyjnius) rather than plyer, because that is the more reliable way to
get a location from inside a background service.

Every cycle it:
  1. Gets the last known location.
  2. Tries to send it straight to the Google Sheet.
  3. If that fails (no internet), saves it to the local offline queue.
  4. Also retries anything already sitting in the queue from earlier.

IMPORTANT - battery optimization:
Many Android phones (Xiaomi, Huawei, Samsung, OnePlus, etc.) aggressively
kill background services to save battery. For reliable all-day tracking,
field workers should open the phone's Battery settings and disable
"battery optimization" / enable "auto-start" for this app. This is a
phone-OS limitation, not something the app itself can fully override.
"""

import json
import time
from datetime import datetime
from pathlib import Path

import requests

import queue_store
import daily_log_store

# Must match the values in main.py
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbx-Azk6A4XdhwgjtRtVLSvhF8vM96mypuV1K6eLqzF6aIBag2KcyXN-Kg23jBSFFAU_/exec"
API_KEY = "pakistan"
AUTO_SEND_INTERVAL = 300  # 5 minutes, in seconds

SESSION_FILE = str(Path(__file__).parent / "worker_session.json")


def get_worker_id():
    """Read the logged-in worker ID that main.py saved via JsonStore."""
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
        return data.get("session", {}).get("worker_id", "")
    except Exception:
        return ""


def get_last_known_location():
    """
    Pull the last known fix from Android's LocationManager.
    Returns (lat, lon, accuracy) or (None, None, None) if unavailable.
    """
    try:
        from jnius import autoclass, cast
        from android.permissions import check_permission, Permission

        if not check_permission(Permission.ACCESS_FINE_LOCATION):
            return None, None, None

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context = autoclass("android.content.Context")
        activity = PythonActivity.mActivity
        location_manager = cast(
            "android.location.LocationManager",
            activity.getSystemService(Context.LOCATION_SERVICE),
        )

        providers = ["gps", "network", "passive"]
        best_location = None
        for provider in providers:
            try:
                loc = location_manager.getLastKnownLocation(provider)
            except Exception:
                loc = None
            if loc is not None:
                if best_location is None or loc.getTime() > best_location.getTime():
                    best_location = loc

        if best_location is None:
            return None, None, None

        return best_location.getLatitude(), best_location.getLongitude(), best_location.getAccuracy()

    except Exception:
        # Not running on Android (e.g. desktop test) or jnius unavailable.
        return None, None, None


def run_cycle():
    worker_id = get_worker_id()
    if not worker_id:
        return  # nobody logged in yet - nothing to send

    lat, lon, accuracy = get_last_known_location()
    captured_at = datetime.now().isoformat()

    if lat is not None:
        daily_log_store.add_entry(worker_id, lat, lon, captured_at)
        queue_store.send_or_queue(WEBHOOK_URL, API_KEY, worker_id, lat, lon, accuracy, captured_at)
    else:
        # Still try flushing anything queued from earlier, even without a
        # fresh fix this cycle.
        queue_store.flush_queue(WEBHOOK_URL, API_KEY)


def main_loop():
    while True:
        try:
            run_cycle()
        except Exception:
            pass  # never let the service crash - just wait and try again
        time.sleep(AUTO_SEND_INTERVAL)


if __name__ == "__main__":
    main_loop()
