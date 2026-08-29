[app]
title = Field Worker Location Tracker
package.name = fieldworkerlocationtracker
package.domain = org.fieldworker
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3==3.11,kivy==2.3.0,plyer,requests,pyjnius,certifi,urllib3,idna,charset-normalizer,chardet
orientation = portrait
fullscreen = 0
# Background service for continuous location tracking
services = tracker:service.py
[android]
# Runtime permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_BACKGROUND_LOCATION,FOREGROUND_SERVICE,WAKE_LOCK
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
# Keep CPU awake while app is in foreground
android.wakelock = True
[buildozer]
log_level = 2
warn_on_root = 0
