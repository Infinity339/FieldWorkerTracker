# Field Worker Location Tracker - Worker App

**This app is FOR FIELD WORKERS only**

---

## What This App Does

When a worker opens this app, they can:

1. **Log in** with their unique Worker ID (e.g., "FW-001", "Ali Raza")
2. **Tap START DUTY** to begin tracking their location
3. **Location auto-sends** to Google Sheets every 5 minutes
4. **Works in background** — keeps tracking even if you minimize the app
5. **Saves offline** — if no internet, locations are saved locally and sent automatically when back online
6. **View daily log** — see all locations captured that day
7. **Send to WhatsApp** — one tap to send the full day's navigation to supervisor
8. **Tap STOP DUTY** to end tracking

---

## Files in This Folder

```
FieldWorkerTracker/
├── main.py                ← Worker app interface (login, duty tracker, daily log)
├── service.py             ← Background service (keeps sending location in background)
├── queue_store.py         ← Offline queue (saves locations if no internet)
├── daily_log_store.py     ← Today's log tracker (all locations captured)
├── buildozer.spec         ← Build configuration for Android
└── AppsScript_Code.gs     ← Backend (communicates with Google Sheets)
```

**Total: 6 files — this is everything the worker app needs**

---

## Before You Build

### 1. Get your Google Sheets Web App URL

This is a one-time setup shared with the Supervisor app.

1. Go to [sheets.google.com](https://sheets.google.com)
2. Create a new spreadsheet called `"Field Worker Locations"`
3. Go to **Extensions → Apps Script**
4. Delete placeholder code
5. Paste the entire `AppsScript_Code.gs` file (from this folder)
6. Change line 7 if you want a different API key:
   ```javascript
   var API_KEY = "pakistan";  // or your own secret
   ```
7. Click **Deploy → New deployment → Web app → Execute as Me → Access: Anyone → Deploy**
8. Copy the Web App URL (looks like `https://script.google.com/macros/s/AKfycb.../exec`)

### 2. Update this app with your URL

**Open `main.py`** and find line 22:
```python
WEBHOOK_URL = "https://script.google.com/macros/s/REPLACE_WITH_YOUR_DEPLOYMENT_ID/exec"
```
Replace with your actual URL.

**Open `service.py`** and find line 22:
```python
WEBHOOK_URL = "https://script.google.com/macros/s/REPLACE_WITH_YOUR_DEPLOYMENT_ID/exec"
```
Replace with the same URL.

Also check the API_KEY matches (should be `"pakistan"` if you didn't change it):
```python
API_KEY = "pakistan"
```

---

## Build This App

### Using GitHub Actions (Easiest — Recommended)

1. Create a GitHub repo called `FieldWorkerTracker`
2. Upload all 6 files from this folder
3. Create `.github/workflows/build.yml` with this content:

```yaml
name: Build Worker APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - run: |
          sudo apt-get update
          sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config libncurses-dev cmake libffi-dev libssl-dev build-essential cython3
          pip install buildozer cython kivy plyer requests
      
      - run: yes | buildozer android debug
      
      - uses: actions/upload-artifact@v4
        with:
          name: worker-apk
          path: bin/*.apk
```

4. Push to GitHub
5. Wait 50 minutes for build to complete
6. Download the APK from the "Actions" tab

---

## Install and Test

1. Copy the APK to your phone: `fieldworkerlocationtracker-1.0-debug.apk`
2. Tap to install (allow unknown sources if prompted)
3. Open the app and:
   - Grant Location and Internet permissions
   - Log in with a Worker ID (e.g., "FW-001")
   - Tap **START DUTY**
   - Check your Google Sheet — a new row should appear in ~5 seconds with your coordinates
   - Tap **Daily Log** to see the captured location
   - Tap **Send to Supervisor** and enter a WhatsApp number to send the log

---

## How It Works Behind the Scenes

### Foreground (App Open)
```
START DUTY → Every 5 minutes
  ↓
Get GPS location
  ↓
Try to send to Google Sheets immediately
  ├─ Success? → Show "✓ Synced {time}"
  └─ No internet? → Save locally, show "✗ Saved locally {time}"
```

### Background (App Minimized)
```
Background service runs continuously every 5 minutes
  ↓
Get last known GPS location
  ↓
Try to send to Google Sheets
  ├─ Success? → Location logged
  └─ No internet? → Save to local queue
  
When internet returns, automatically flush queue
```

### Daily Log
```
Every location (foreground or background) added to today's log
  ↓
Worker can preview anytime
  ↓
Send to WhatsApp with one tap
```

---

## Important Notes

### Battery Optimization
On some phones (Xiaomi, Huawei, Samsung, OnePlus), Android aggressively kills background services. After installing:

1. Open **Settings → Apps → Field Worker Location Tracker**
2. Tap **Battery**
3. Set to **"Unrestricted"** or **"Don't optimize"** (wording varies by brand)

Without this, the background tracking may stop after the phone idles.

### Offline Queue
If a worker has no internet:
1. Location is saved on the phone
2. App shows "✗ Saved locally"
3. No action needed — when internet returns, the app automatically sends it
4. Workers can keep using the app normally

### Daily Log
The log includes every location captured that day:
```
Timestamp | Worker ID | Latitude | Longitude
10:05:30  | FW-001    | 30.12345 | 69.67890
10:10:45  | FW-001    | 30.12400 | 69.67920
```

When sending to WhatsApp, the full log is pre-typed in the message.

---

## Troubleshooting

### Locations not sending
- Check GPS is ON on the phone
- Make sure WEBHOOK_URL is correct in main.py and service.py
- Check internet connection works

### App crashes on login
- Verify API_KEY in main.py, service.py, and AppsScript_Code.gs all match

### Background service not working
- Enable location permission for "all the time" (not just "while using app")
- Disable battery optimization for this app (see "Important Notes" above)

### WhatsApp not opening
- Make sure WhatsApp is installed
- Check the phone number is entered in the correct format (digits only)

---

## What Data Is Stored?

### On Google Sheet (Shared)
- Timestamp (when received)
- Worker ID
- Latitude
- Longitude
- GPS Accuracy (in meters)
- Captured at time (device timestamp)

### On Phone (Private, Local)
- Daily log of today's locations (SQLite database: `daily_log.db`)
- Offline queue (SQLite database: `pending_locations.db`)
- Session info (which worker is logged in)

All local data is on the phone only — nothing is sent unless the worker explicitly sends to WhatsApp.

---

## Next Steps

1. **Set up the Google Sheet** (see "Before You Build" section)
2. **Update WEBHOOK_URL** in main.py and service.py
3. **Build on GitHub Actions** (see "Build This App" section)
4. **Install on worker phones**
5. **Test with one worker** before rolling out to the team

---

## Support

If something doesn't work:
- Check FILE_STRUCTURE.md for overview
- Check SETUP_GUIDE.md for detailed step-by-step
- Make sure all file updates are done (WEBHOOK_URL, API_KEY)
- Verify Google Sheet is accessible

Good luck! 🚀
