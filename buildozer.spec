[app]
title = VitalRegistro
package.name = vitalregistro
package.domain = org.vitalregistro
source.dir = .
source.include_exts = py,kv,png
source.exclude_dirs = tests,scripts,docs,.venv,.venv-build,.build-tools,venv,runtime,exports,bin,build,dist,.github
source.exclude_patterns = apresentacao.png,icone.png,**/__pycache__/*
version = 0.2.0
# Match the Python/hostpython recipes at the pinned p4a revision.
requirements = python3==3.14.2,hostpython3==3.14.2,kivy==2.3.1,sqlite3,pyjnius==1.7.0
icon.filename = %(source.dir)s/assets/icons/icone.png
orientation = portrait
fullscreen = 0
# No internet or storage permissions. Export uses ACTION_CREATE_DOCUMENT.
android.permissions =
android.api = 36
android.minapi = 24
android.ndk = 29
android.ndk_api = 24
android.archs = arm64-v8a
android.allow_backup = False
android.accept_sdk_license = False
p4a.branch = develop
p4a.commit = e772ad93f20a61c0bbe1cf8955e073cfb41062e1
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
