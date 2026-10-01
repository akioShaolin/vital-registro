[app]
title = VitalRegistro
package.name = vitalregistro
package.domain = org.vitalregistro
source.dir = .
source.include_exts = py,kv,png
source.exclude_dirs = tests,scripts,docs,.venv,.venv-build,venv,runtime,exports,bin,build,dist,.github
source.exclude_patterns = apresentacao.png,icone.png,**/__pycache__/*
version = 0.1.0
requirements = python3,kivy==2.3.1,sqlite3,pyjnius
icon.filename = %(source.dir)s/assets/icons/icone.png
orientation = portrait
fullscreen = 0
# No internet or storage permissions. Export uses ACTION_CREATE_DOCUMENT.
android.permissions =
android.api = 35
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a
android.allow_backup = False
android.accept_sdk_license = False
p4a.branch = master
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
