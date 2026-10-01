"""Run the same checked Android build from Colab and Linux terminals."""

import os
import subprocess

from build_environment import ROOT, android_environment


def build():
    env = android_environment()
    subprocess.run([env["JAVA_HOME"] + "/bin/java", "-version"], check=True, env=env)
    subprocess.run([env["JAVA_HOME"] + "/bin/javac", "-version"], check=True, env=env)
    subprocess.run([str(ROOT / ".venv-build/bin/python"), "-m", "pip", "freeze"], check=True, env=env)
    # Colab is root: answer only Buildozer's explicit root warning.
    # SDK licenses remain governed by android.accept_sdk_license in the spec.
    options = {"input": "y\n", "text": True} if os.geteuid() == 0 else {}
    subprocess.run([str(ROOT / ".venv-build/bin/buildozer"), "-v", "android", "debug"],
                   cwd=ROOT, env=env, check=True, **options)
    subprocess.run(["git", "-C", str(ROOT / ".buildozer/android/platform/python-for-android"),
                    "rev-parse", "HEAD"], check=True)
    apks = sorted((ROOT / "bin").glob("*.apk"))
    if not apks:
        raise RuntimeError("Buildozer returned success but bin/ contains no APK.")
    for apk in apks:
        print(f"APK: {apk.name} ({apk.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    build()
