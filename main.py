"""
Field Worker Location Tracker - Worker App (WITH AUTHENTICATION)
==================================================================
For field workers to:
1. LOGIN with authentication (only workers in directory allowed)
2. START/STOP DUTY and track location
3. Save location log locally
4. Send daily log via WhatsApp

Authentication: Validates worker ID against WorkersDirectory sheet in Google Sheets
Only workers in the directory can log in.
"""

import re
import threading
import urllib.parse
import webbrowser
from datetime import datetime

import requests
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from plyer import gps, notification

# Import storage helpers
from queue_store import QueueStore
from daily_log_store import DailyLogStore

# CONFIG - Update with your Google Sheet Web App URL
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbx-Azk6A4XdhwgjtRtVLSvhF8vM96mypuV1K6eLqzF6aIBag2KcyXN-Kg23jBSFFAU_/exec"
API_KEY = "pakistan"
AUTO_SEND_INTERVAL = 300  # 5 minutes

try:
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    ANDROID = True
except ImportError:
    ANDROID = False


class LoginScreen(Screen):
    """Worker login screen with authentication."""
    login_status = StringProperty("Enter your Worker ID")
    error_message = StringProperty("")
    is_authenticating = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_workers = []  # Cache of authorized workers
        self.auth_checked = False
        self.fetch_worker_directory()

    def on_enter(self):
        self.ids.worker_id_input.focus = True

    def fetch_worker_directory(self):
        """Fetch authorized workers from WorkersDirectory sheet."""
        self.is_authenticating = "Fetching worker directory..."
        threading.Thread(target=self._fetch_workers, daemon=True).start()

    def _fetch_workers(self):
        try:
            # Fetch worker directory from Google Sheets
            resp = requests.get(
                WEBHOOK_URL,
                params={"action": "get_directory"},
                timeout=15
            )
            workers = resp.json()
            self.auth_workers = workers if isinstance(workers, list) else []
            self.auth_checked = True
            self._set_status("Ready to login")
        except Exception as e:
            self.auth_workers = []  # Allow offline login as fallback
            self.auth_checked = True
            self._set_status(f"Offline mode: {str(e)[:30]}")

    @mainthread
    def _set_status(self, text):
        self.login_status = text
        self.is_authenticating = ""

    def authenticate_worker(self):
        """Authenticate worker against directory."""
        worker_id = self.ids.worker_id_input.text.strip()

        if not worker_id:
            self.error_message = "❌ Error: Please enter your Worker ID"
            return

        if not self.auth_checked:
            self.error_message = "⏳ Loading worker directory..."
            return

        # Check if worker exists in directory
        is_authorized = self._validate_worker(worker_id)

        if is_authorized:
            # Successful login
            self.error_message = ""
            self.login_status = f"✅ Welcome, {worker_id}!"
            app = App.get_running_app()
            app.current_worker_id = worker_id
            # Get worker name if available
            worker_name = self._get_worker_name(worker_id)
            app.current_worker_name = worker_name if worker_name else worker_id
            Clock.schedule_once(lambda dt: self._switch_to_tracker(), 1)
        else:
            # Failed login
            self.error_message = "❌ Error: Worker ID not found in directory"
            self.login_status = "⛔ Unauthorized"
            self.ids.worker_id_input.text = ""

    def _validate_worker(self, worker_id):
        """Check if worker ID exists in directory."""
        # Normalize for comparison
        worker_id_lower = worker_id.lower().strip()
        for worker in self.auth_workers:
            auth_id = str(worker.get("WorkerID", "")).lower().strip()
            if auth_id == worker_id_lower:
                return True
        return False

    def _get_worker_name(self, worker_id):
        """Get worker name from directory."""
        worker_id_lower = worker_id.lower().strip()
        for worker in self.auth_workers:
            auth_id = str(worker.get("WorkerID", "")).lower().strip()
            if auth_id == worker_id_lower:
                return worker.get("Name", "")
        return None

    def _switch_to_tracker(self):
        """Switch to tracker screen."""
        self.manager.current = "tracker"

    def on_keyboard_enter(self, widget):
        """Handle Enter key press."""
        if self.ids.worker_id_input.focus:
            self.authenticate_worker()


class TrackerScreen(Screen):
    """Worker tracking screen - START/STOP DUTY, view status."""
    tracker_status = StringProperty("Ready to start duty")
    last_sent_text = StringProperty("")
    pending_sync_text = StringProperty("")
    duty_active = False
    current_worker_id = StringProperty("")

    def on_enter(self):
        """Update UI when entering tracker screen."""
        app = App.get_running_app()
        self.current_worker_id = app.current_worker_name
        self._update_status()

    def start_duty(self):
        """Start tracking duty."""
        if self.duty_active:
            return
        
        self.duty_active = True
        self.tracker_status = "🟢 DUTY ACTIVE - Sending location every 5 min"
        self.last_sent_text = ""
        
        if ANDROID:
            app = App.get_running_app()
            app._start_background_service()
        
        self._start_auto_tracking()

    def stop_duty(self):
        """Stop tracking duty."""
        if not self.duty_active:
            return
        
        self.duty_active = False
        self.tracker_status = "🔴 DUTY STOPPED"
        
        if ANDROID:
            app = App.get_running_app()
            app._stop_background_service()

    def _start_auto_tracking(self):
        """Start auto-tracking loop."""
        threading.Thread(target=self._tracking_loop, daemon=True).start()

    def _tracking_loop(self):
        """Main tracking loop."""
        while self.duty_active:
            self._send_location_and_log()
            Clock.sleep(AUTO_SEND_INTERVAL)

    def _send_location_and_log(self):
        """Capture location and send/queue it."""
        try:
            # Get location
            if ANDROID:
                self._request_single_location()
            else:
                # Test location
                self._log_location(30.1234, 69.5678)
        except Exception as e:
            pass

    def _request_single_location(self):
        """Request single GPS location."""
        try:
            gps.start(on_location=self.on_gps_location, timeout=30000)
        except Exception as e:
            pass

    def on_gps_location(self, **kwargs):
        """Handle GPS location update."""
        latitude = kwargs['lat']
        longitude = kwargs['lon']
        accuracy = kwargs.get('accuracy', 0)
        
        self._log_location(latitude, longitude, accuracy)
        gps.stop()

    def _log_location(self, latitude, longitude, accuracy=0):
        """Log location and send/queue."""
        app = App.get_running_app()
        worker_id = app.current_worker_id
        timestamp = datetime.now().isoformat()
        
        # Add to daily log
        DailyLogStore.add_entry(worker_id, latitude, longitude, timestamp)
        
        # Try to send
        self._send_to_sheets(worker_id, latitude, longitude, accuracy, timestamp)
        
        # Update UI
        self._update_status()

    def _send_to_sheets(self, worker_id, latitude, longitude, accuracy, timestamp):
        """Send location to Google Sheets."""
        try:
            data = {
                "action": "log_location",
                "worker_id": worker_id,
                "latitude": str(latitude),
                "longitude": str(longitude),
                "accuracy": str(accuracy),
                "timestamp": timestamp,
                "api_key": API_KEY
            }
            resp = requests.post(WEBHOOK_URL, data=data, timeout=10)
            
            if resp.status_code == 200:
                self._set_last_sent(timestamp)
            else:
                # Queue for retry
                QueueStore.save_location(worker_id, latitude, longitude, timestamp)
        except Exception as e:
            # Queue for retry
            QueueStore.save_location(worker_id, latitude, longitude, timestamp)

    @mainthread
    def _set_last_sent(self, timestamp):
        """Update last sent timestamp."""
        self.last_sent_text = f"✓ Sent at {timestamp[-8:]}"

    @mainthread
    def _update_status(self):
        """Update pending sync count."""
        pending = QueueStore.pending_count()
        if pending > 0:
            self.pending_sync_text = f"⚠️ Offline: {pending} location(s) pending"
        else:
            self.pending_sync_text = "✓ All synced"

    def view_daily_log(self):
        """Show daily log."""
        self.manager.current = "daily_log"

    def logout(self):
        """Logout worker."""
        if self.duty_active:
            self.stop_duty()
        
        # Reset
        app = App.get_running_app()
        app.current_worker_id = None
        app.current_worker_name = None
        
        self.manager.current = "login"
        self.ids.worker_id_input.text = ""


class DailyLogScreen(Screen):
    """View and send daily location log."""
    log_status = StringProperty("")
    log_count = StringProperty("")

    def on_enter(self):
        """Load log when entering screen."""
        self._load_log()

    def _load_log(self):
        """Load today's log."""
        count = DailyLogStore.today_count()
        self.log_count = f"Today: {count} location(s) captured"
        self.log_status = "Tap 'Send to WhatsApp' to share log with supervisor"

    def preview_log(self):
        """Show log preview."""
        log_text = DailyLogStore.format_log_as_text()
        
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        content.add_widget(Label(text=log_text, size_hint_y=0.8))
        
        btn = Button(text="Close", size_hint_y=0.2)
        popup = Popup(title="Daily Log Preview", content=content, size_hint=(0.9, 0.8))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        
        popup.open()

    def send_to_whatsapp(self):
        """Send log via WhatsApp."""
        phone_input = TextInput(
            multiline=False,
            hint_text="Supervisor phone (e.g., +923001234567)",
            size_hint_y=None,
            height=40
        )
        
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text="Enter supervisor phone number:", size_hint_y=None, height=40))
        content.add_widget(phone_input)
        
        btn_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        def send_whatsapp(instance):
            phone = phone_input.text.strip()
            if phone:
                self._send_whatsapp_message(phone)
                popup.dismiss()
        
        send_btn = Button(text="Send", background_color=(0.2, 0.7, 0.4, 1))
        cancel_btn = Button(text="Cancel", background_color=(0.5, 0.5, 0.5, 1))
        
        send_btn.bind(on_release=send_whatsapp)
        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        
        btn_row.add_widget(send_btn)
        btn_row.add_widget(cancel_btn)
        
        content.add_widget(btn_row)
        
        popup = Popup(title="Send Log via WhatsApp", content=content, size_hint=(0.8, 0.4))
        popup.open()

    def _send_whatsapp_message(self, phone_number):
        """Send location log via WhatsApp."""
        log_text = DailyLogStore.format_log_as_text()
        message = f"Daily Location Log:\n\n{log_text}"
        
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"whatsapp://send?phone={phone_number}&text={encoded_message}"
        
        if ANDROID:
            try:
                webbrowser.open(whatsapp_url)
                self.log_status = "✓ Sent to WhatsApp"
            except:
                self.log_status = "❌ WhatsApp not installed"
        else:
            self.log_status = "Test: Would open WhatsApp"

    def back_to_tracker(self):
        """Return to tracker."""
        self.manager.current = "tracker"


KV = """
ScreenManager:
    LoginScreen:
    TrackerScreen:
    DailyLogScreen:

<LoginScreen>:
    name: "login"
    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 20
        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.95, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "Field Worker Location Tracker"
            font_size: "24sp"
            bold: True
            size_hint_y: 0.2

        BoxLayout:
            orientation: "vertical"
            size_hint_y: 0.4
            padding: 10
            spacing: 10
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            Label:
                text: "Worker ID Login"
                font_size: "16sp"
                bold: True
                size_hint_y: 0.2
            
            TextInput:
                id: worker_id_input
                hint_text: "Enter your Worker ID (e.g., FW-001)"
                multiline: False
                size_hint_y: 0.4
                on_text_validate: root.authenticate_worker()
            
            Button:
                text: "Login"
                size_hint_y: 0.4
                background_color: (0.2, 0.6, 0.9, 1)
                font_size: "16sp"
                on_release: root.authenticate_worker()

        Label:
            text: root.login_status
            font_size: "13sp"
            color: (0.2, 0.7, 0.2, 1)
            size_hint_y: 0.2

        Label:
            text: root.error_message
            font_size: "14sp"
            color: (1, 0.2, 0.2, 1)
            bold: True
            size_hint_y: 0.2

        Label:
            text: root.is_authenticating
            font_size: "12sp"
            color: (0.6, 0.6, 0.6, 1)
            size_hint_y: 0.2

<TrackerScreen>:
    name: "tracker"
    current_worker_id: root.current_worker_id
    BoxLayout:
        orientation: "vertical"
        padding: 15
        spacing: 15
        canvas.before:
            Color:
                rgba: 0.95, 0.95, 0.95, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: f"Worker: {root.current_worker_id}"
            font_size: "18sp"
            bold: True
            size_hint_y: 0.1

        Label:
            text: root.tracker_status
            font_size: "14sp"
            bold: True
            color: (0.2, 0.7, 0.2, 1)
            size_hint_y: 0.1

        BoxLayout:
            size_hint_y: 0.3
            spacing: 10
            Button:
                text: "START DUTY"
                background_color: (0.2, 0.8, 0.2, 1)
                font_size: "18sp"
                bold: True
                on_release: root.start_duty()
            
            Button:
                text: "STOP DUTY"
                background_color: (1, 0.2, 0.2, 1)
                font_size: "18sp"
                bold: True
                on_release: root.stop_duty()

        Label:
            text: root.last_sent_text
            font_size: "12sp"
            size_hint_y: 0.1

        Label:
            text: root.pending_sync_text
            font_size: "12sp"
            color: (1, 0.7, 0.2, 1)
            size_hint_y: 0.1

        BoxLayout:
            size_hint_y: 0.2
            spacing: 10
            Button:
                text: "Daily Log"
                background_color: (0.2, 0.6, 0.9, 1)
                on_release: root.view_daily_log()
            
            Button:
                text: "Logout"
                background_color: (0.7, 0.2, 0.2, 1)
                on_release: root.logout()

<DailyLogScreen>:
    name: "daily_log"
    BoxLayout:
        orientation: "vertical"
        padding: 15
        spacing: 15

        Label:
            text: "Daily Location Log"
            font_size: "18sp"
            bold: True
            size_hint_y: 0.1

        Label:
            text: root.log_count
            font_size: "14sp"
            size_hint_y: 0.1

        Label:
            text: root.log_status
            font_size: "12sp"
            size_hint_y: 0.2

        BoxLayout:
            size_hint_y: 0.3
            spacing: 10
            Button:
                text: "Preview Log"
                background_color: (0.2, 0.6, 0.9, 1)
                on_release: root.preview_log()
            
            Button:
                text: "Send to WhatsApp"
                background_color: (0.2, 0.8, 0.2, 1)
                on_release: root.send_to_whatsapp()

        Button:
            text: "Back to Tracker"
            size_hint_y: 0.2
            background_color: (0.5, 0.5, 0.5, 1)
            on_release: root.back_to_tracker()
"""


class FieldWorkerApp(App):
    current_worker_id = None
    current_worker_name = None

    def build(self):
        if ANDROID:
            request_permissions([
                Permission.INTERNET,
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_BACKGROUND_LOCATION,
            ])
        
        root = Builder.load_string(KV)
        return root

    def _start_background_service(self):
        """Start background location service."""
        if ANDROID:
            try:
                from android.runnable import run_on_ui_thread
                from org.kivy.android import service
                run_on_ui_thread(lambda: service.start('fieldworker_service'))
            except:
                pass

    def _stop_background_service(self):
        """Stop background location service."""
        if ANDROID:
            try:
                from android.runnable import run_on_ui_thread
                from org.kivy.android import service
                run_on_ui_thread(lambda: service.stop('fieldworker_service'))
            except:
                pass


if __name__ == "__main__":
    FieldWorkerApp().run()
