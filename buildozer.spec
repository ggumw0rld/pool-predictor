[app]
title = PoolPredictor
package.name = poolpredictor
package.domain = org.poolpredictor
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.3.0,numpy,pillow
orientation = portrait
osx.kivy_version = 2.3.0

[buildozer]
log_level = 2
warn_on_root = 1

[app:android]
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,SYSTEM_ALERT_WINDOW
android.api = 33
android.minapi = 26
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
