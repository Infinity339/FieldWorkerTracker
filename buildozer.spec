[app]

# (str) Title of your application
title = Field Worker Location Tracker

# (str) Package name
package.name = fieldworkerlocationtracker

# (str) Package domain (needed for android/ios packaging)
package.domain = org.fieldworker.tracker

# (source.dir) Source code where the main.py is
source.dir = .

# (source.include_exts) Source include extensions (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (version) Application version
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
# Simplified and tested requirements
requirements = python3==3.11,kivy==2.2.1,plyer,requests,pyjnius,certifi

# (str) Supported orientation (landscape, sensorLandscape, portrait or sensorPortrait)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = False

# (string) Presplash background color (for new android toolchain)
android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_BACKGROUND_LOCATION,ACCESS_COARSE_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 24

# (int) Android NDK version to use
android.ndk = 27c

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a,armeabi-v7a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Indicate if the generated buildozer.spec should be committed to Version Control System
# add_src = False

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning + info for result of buildozer.spec coercion
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file directory (./build by default)
build_dir = .buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin

