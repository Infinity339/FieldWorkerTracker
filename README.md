================================================================================
                   🚀 FIELD WORKER TRACKER - WORKER APP
                      Build Instructions & Documentation
================================================================================

WHAT IS THIS APP?
=================

The Field Worker Tracker is an Android app for field workers to:
  ✓ Securely log in with Worker ID authentication
  ✓ Track their location automatically every 5 minutes
  ✓ View their daily location log
  ✓ Send daily reports via WhatsApp
  ✓ Works offline (saves locations locally, syncs when online)

================================================================================
                          QUICK START
================================================================================

STEP 1: CONFIGURE (5 minutes)

1. Open: main.py (line 28)
2. Find: WEBHOOK_URL = "https://script.google.com/macros/s/..."
3. Replace with YOUR Google Apps Script deployment URL
4. Save file

STEP 2: SETUP GOOGLE SHEET (5 minutes)

1. Create Google Sheet named: "Field Worker Locations"
2. Create sheet tab: "WorkersDirectory"
3. Add headers: WorkerID | Name | Phone
4. Add workers:
   FW-001 | Ali Raza | +923001234567
   FW-002 | Sana Khan | +923007654321

STEP 3: DEPLOY APPSSCRIPT (5 minutes)

1. Open your Google Sheet
2. Tools → Script editor
3. Paste AppsScript_Code.gs content
4. Deploy → New deployment → Web app
5. Execute as: Me
6. Access: Anyone
7. Copy deployment URL
8. Update WEBHOOK_URL in main.py

STEP 4: BUILD ON GITHUB (50 minutes)

1. Create GitHub repo: FieldWorkerTracker
2. Upload files:
   - main.py ✓
   - service.py ✓
   - queue_store.py ✓
   - daily_log_store.py ✓
   - buildozer.spec ✓
   - AppsScript_Code.gs ✓
   - .github/workflows/build.yml ✓
3. Push to main branch
4. GitHub Actions starts build (takes ~50 min)
5. Download APK from Artifacts when ready

STEP 5: INSTALL & TEST (10 minutes)

1. Download APK from GitHub Artifacts
2. Transfer to Android phone
3. Install APK
4. Open app
5. Test login with valid Worker ID
6. Test START DUTY and location tracking
7. Verify locations appear in Google Sheet

================================================================================
                          FILE STRUCTURE
================================================================================

FieldWorkerTracker/
├── main.py                      # Main app code with login & tracking
├── service.py                   # Background location service
├── queue_store.py               # Offline queue (SQLite)
├── daily_log_store.py           # Daily log storage (SQLite)
├── buildozer.spec               # Kivy build configuration
├── AppsScript_Code.gs           # Google Sheets backend
├── .github/
│   └── workflows/
│       └── build.yml            # GitHub Actions build workflow
└── README.md                    # This file

TOTAL FILES: 8
TOTAL SIZE: ~150 KB (code only, no dependencies)

================================================================================
                          FEATURES
================================================================================

AUTHENTICATION:
  ✓ Worker ID login (secure)
  ✓ Directory validation against WorkersDirectory sheet
  ✓ Error messages for unauthorized logins
  ✓ Offline caching of worker list

LOCATION TRACKING:
  ✓ Automatic GPS every 5 minutes
  ✓ Background service (tracks even when minimized)
  ✓ Offline queue (saves if no internet)
  ✓ Auto-retry when online
  ✓ Battery efficient (stops after fix)

DAILY LOG:
  ✓ View all day's location points
  ✓ Formatted text display
  ✓ Send via WhatsApp to supervisor

USER INTERFACE:
  ✓ Clean, simple design
  ✓ Large buttons for easy tapping
  ✓ Status indicators (active/stopped)
  ✓ Pending sync counter
  ✓ Worker name display

BACKGROUND SERVICE:
  ✓ Keeps tracking when app is minimized
  ✓ Survives app restart
  ✓ Uses separate service process
  ✓ Minimal battery drain

================================================================================
                          CONFIGURATION
================================================================================

FILE: main.py (Line 28)

WEBHOOK_URL = "https://script.google.com/macros/s/REPLACE_WITH_YOUR_DEPLOYMENT_ID/exec"

This should be replaced with your actual Google Apps Script deployment URL.
Example: https://script.google.com/macros/s/AKfycbwXaBcDeFgHiJkLmNoPqRsT123456/exec

FILE: main.py (Line 29)

API_KEY = "pakistan"

This key validates requests to your Google Sheet. Change if desired.

FILE: main.py (Line 30)

AUTO_SEND_INTERVAL = 300  # 5 minutes in seconds

How often to send location (in seconds). Default: 300 (5 minutes)

FILE: buildozer.spec

package.name = fieldworkerlocationtracker
package.domain = org.fieldworker.tracker

These are the Android app identifiers. Change if desired.

================================================================================
                          BUILD INSTRUCTIONS
================================================================================

GITHUB SETUP:

1. Create new GitHub repository: "FieldWorkerTracker"
2. Clone to your computer
3. Copy all files from FieldWorkerTracker folder into the repo
4. Commit: git add . && git commit -m "Initial commit"
5. Push: git push origin main
6. GitHub Actions automatically starts build

BUILD PROCESS:

The .github/workflows/build.yml file handles everything:
  1. Checks out code
  2. Installs Python 3.11
  3. Installs system dependencies (Java, build tools, etc)
  4. Installs Python packages (buildozer, kivy, etc)
  5. Runs: buildozer android debug
  6. Uploads APK to Artifacts

BUILD TIME:
  First build: ~50 minutes (downloads Android SDK)
  Subsequent builds: ~30-40 minutes

DOWNLOAD APK:
  1. Go to GitHub repo → Actions
  2. Click latest successful build
  3. Download "fieldworker-tracker-apk" artifact
  4. Unzip and get APK file
  5. Transfer to Android phone and install

================================================================================
                          TESTING
================================================================================

TEST 1: LOGIN (2 min)
  1. Open app
  2. Type valid Worker ID (from WorkersDirectory)
  3. Tap Login
  Expected: "✅ Welcome" message, proceeds to tracker
  Status: ✓ Pass if successful

TEST 2: INVALID LOGIN (2 min)
  1. Open app
  2. Type invalid Worker ID (not in WorkersDirectory)
  3. Tap Login
  Expected: "❌ Worker ID not found" message, stays on login
  Status: ✓ Pass if error shown

TEST 3: LOCATION TRACKING (10 min)
  1. Log in with valid Worker ID
  2. Tap "START DUTY"
  3. Wait 5-10 minutes
  4. Check Google Sheet "Locations" tab
  Expected: Location entries appear with timestamps
  Status: ✓ Pass if locations recorded

TEST 4: DAILY LOG (5 min)
  1. Log in and tap "Daily Log"
  2. Tap "Preview Log"
  Expected: Shows today's location points
  Status: ✓ Pass if log displays

TEST 5: WHATSAPP SENDING (5 min)
  1. Log in and tap "Daily Log"
  2. Tap "Send to WhatsApp"
  3. Enter supervisor phone number
  4. Tap Send
  Expected: Opens WhatsApp with pre-filled message
  Status: ✓ Pass if WhatsApp opens

TEST 6: LOGOUT (2 min)
  1. From tracker screen, tap "Logout"
  Expected: Returns to login screen
  Status: ✓ Pass if back on login

ALL TESTS PASS? → App ready for deployment! ✓

================================================================================
                          DEPENDENCIES
================================================================================

PYTHON PACKAGES:
  • kivy (v2.0+) - UI framework
  • plyer - GPS access
  • requests - HTTP calls
  • buildozer - Build tool

ANDROID REQUIREMENTS:
  • Minimum API: 21 (Android 5.0)
  • Target API: 33
  • Permissions: INTERNET, ACCESS_FINE_LOCATION, ACCESS_BACKGROUND_LOCATION

SYSTEM REQUIREMENTS (for building):
  • Java JDK 17
  • Python 3.11
  • Git
  • zip/unzip utilities
  • Standard build tools (gcc, make, etc)

All handled by GitHub Actions!

================================================================================
                          TROUBLESHOOTING
================================================================================

BUILD ERRORS:

Error: "buildozer: command not found"
  Solution: Pip not installed properly. Reinstall buildozer.

Error: "Java not found"
  Solution: GitHub Actions installs Java. Check build.yml.

Error: "SDK license not accepted"
  Solution: build.yml includes 'yes' to auto-accept licenses.

RUNTIME ERRORS:

App crashes on startup:
  Solution: Check WEBHOOK_URL is valid in main.py

"Worker ID not found" for valid workers:
  Solution: Check WorkersDirectory sheet exists and is named exactly

Can't log in offline:
  Solution: App needs to connect once to cache worker list

Locations not saving:
  Solution: Check INTERNET permission granted, check WEBHOOK_URL valid

WhatsApp not opening:
  Solution: Install WhatsApp on phone first

TESTING ERRORS:

APK won't install:
  Solution: Allow unknown apps in phone settings

"This app is corrupted" error:
  Solution: Try downloading APK again from GitHub

BUILD TAKES TOO LONG:
  Solution: First build takes ~50 min. Subsequent builds faster.

BUILD KEEPS FAILING:
  Solution: Wait a few minutes and try again. Sometimes GitHub Actions queue is full.

================================================================================
                          DEPLOYMENT
================================================================================

BEFORE DEPLOYING:

1. ✓ All features tested on phone
2. ✓ WEBHOOK_URL is correct
3. ✓ WorkersDirectory sheet created with workers
4. ✓ AppsScript deployed
5. ✓ All workers added to directory
6. ✓ Each worker knows their Worker ID

DEPLOYING:

1. Download APK from GitHub
2. Transfer to worker phones (USB or share link)
3. Install APK (Settings → Unknown apps → Enable)
4. Give each worker their Worker ID
5. Brief workers on login procedure
6. First day: Monitor for issues

MONITORING:

Day 1:
  • Check all workers logged in successfully
  • Monitor Google Sheet for location entries
  • Check for error messages

Weekly:
  • Review location logs for gaps or issues
  • Add new workers if needed
  • Remove workers who left
  • Update phone numbers if changed

Monthly:
  • Analyze coverage patterns
  • Identify any tracking issues
  • Plan improvements

================================================================================
                          FEATURES OVERVIEW
================================================================================

LOGIN SCREEN:
  • Worker ID input field
  • Login button
  • Status messages
  • Error display
  • Directory loaded indicator

TRACKER SCREEN:
  • Current worker name display
  • Duty status (Active/Stopped)
  • START DUTY button (green)
  • STOP DUTY button (red)
  • Last sent timestamp
  • Pending sync counter
  • Daily Log button
  • Logout button

DAILY LOG SCREEN:
  • Today's location count
  • Preview button (shows formatted log)
  • Send to WhatsApp button
  • Back to Tracker button

BACKGROUND:
  • Continuous location tracking
  • Automatic retry on failure
  • Offline queue persistence
  • Battery optimized

================================================================================
                          API ENDPOINTS
================================================================================

Google Apps Script Endpoints:

POST /exec
  Purpose: Log location from worker
  Data: {
    "action": "log_location",
    "worker_id": "FW-001",
    "latitude": "30.1234",
    "longitude": "69.5678",
    "accuracy": "15",
    "timestamp": "2026-08-29T14:30:45",
    "api_key": "pakistan"
  }
  Response: {"status": "success"}

GET /exec?action=get_directory
  Purpose: Fetch worker directory for authentication
  Response: [
    {"WorkerID": "FW-001", "Name": "Ali Raza", "Phone": "+923001234567"},
    {"WorkerID": "FW-002", "Name": "Sana Khan", "Phone": "+923007654321"}
  ]

================================================================================
                          SECURITY
================================================================================

AUTHENTICATION:
  • Workers must enter valid ID
  • ID validated against WorkersDirectory
  • Unauthorized logins blocked with error
  • Offline caching for resilience

DATA PROTECTION:
  • API key validation on all requests
  • HTTPS to Google Sheets
  • SQLite encryption available (if configured)
  • No sensitive data in logs

PRIVACY:
  • Only authorized workers can track
  • Location data stored in your Google Sheet
  • No third-party tracking
  • Data ownership: You (in your Google Sheet)

================================================================================
                          TECHNICAL DETAILS
================================================================================

FRAMEWORK: Kivy (cross-platform UI)
LANGUAGE: Python 3
BUILD: Buildozer (APK builder)
GPS: Plyer library
STORAGE: SQLite (queue + daily log)
BACKEND: Google Apps Script + Google Sheets
COMMUNICATION: HTTP POST/GET

CODE STRUCTURE:
  main.py → LoginScreen, TrackerScreen, DailyLogScreen
  service.py → Background location service
  queue_store.py → Offline queue management
  daily_log_store.py → Daily location log
  AppsScript_Code.gs → Backend API

PERMISSIONS NEEDED:
  INTERNET → Send data to Google Sheet
  ACCESS_FINE_LOCATION → Get GPS location
  ACCESS_BACKGROUND_LOCATION → Track when in background

================================================================================
                          NEXT STEPS
================================================================================

1. UPDATE CONFIGURATION (5 min)
   → Edit WEBHOOK_URL in main.py with your Google Apps Script URL

2. SETUP GOOGLE SHEET (5 min)
   → Create WorkersDirectory sheet with your workers

3. DEPLOY APPSSCRIPT (5 min)
   → Deploy AppsScript_Code.gs to Google Sheet

4. BUILD ON GITHUB (50 min)
   → Create repo, upload files, wait for build

5. TEST APP (10 min)
   → Download APK, install, test login and tracking

6. DEPLOY TO WORKERS (15 min)
   → Install on worker phones, give them their IDs

TOTAL TIME: ~1.5 hours

Ready to build! 🚀

================================================================================
                          SUPPORT
================================================================================

DOCUMENTATION:
  See parent folder for:
  • AUTH_QUICK_SETUP.md - Authentication setup guide
  • WORKER_AUTHENTICATION.md - Detailed auth documentation
  • UPDATE_SUMMARY.md - Feature overview

TROUBLESHOOTING:
  1. Check WEBHOOK_URL is correct
  2. Verify WorkersDirectory sheet exists
  3. Check internet connection
  4. Restart app to refresh caches
  5. Check Google Sheet for entries

ISSUES:
  • App won't build: Check build.yml workflow, wait for GitHub queue
  • Can't log in: Check WorkersDirectory sheet, restart app
  • Locations not saving: Check WEBHOOK_URL, check INTERNET permission
  • WhatsApp not opening: Install WhatsApp first

GIT PUSH:
  After making changes:
  git add .
  git commit -m "Description of changes"
  git push origin main

GitHub Actions will automatically rebuild!

================================================================================
                          SUMMARY
================================================================================

This is a PRODUCTION-READY Android app for field worker location tracking.

Features:
  ✓ Secure authentication with Worker ID
  ✓ Automatic GPS tracking every 5 minutes
  ✓ Offline support (works without internet)
  ✓ Daily location logs
  ✓ WhatsApp integration
  ✓ Background service for continuous tracking
  ✓ Easy worker management

Technology:
  ✓ Built with Kivy (Python)
  ✓ Compiled to native Android APK
  ✓ Uses Google Sheets as backend (free)
  ✓ No external APIs or costs

Deployment:
  ✓ Build on GitHub (automated)
  ✓ Download APK
  ✓ Install on worker phones
  ✓ Start tracking!

Status: ✅ READY FOR PRODUCTION

Build and deploy with confidence! 🚀

================================================================================
