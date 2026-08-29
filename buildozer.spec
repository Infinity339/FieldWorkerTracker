[app]
title = Field Worker Tracker
package.name = fieldworkerlocationtracker
package.domain = org.fieldworker.tracker
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3==3.11,kivy==2.2.1,plyer,requests,pyjnius,certifi
orientation = portrait
fullscreen = 0
android.presplash_color = #FFFFFF
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_BACKGROUND_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk = 27c
android.copy_libs = 1
android.archs = arm64-v8a,armeabi-v7a
android.enable_androidx = True
android.skip_update = False
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = .buildozer
bin_dir = ./bin
