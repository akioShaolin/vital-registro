"""Desktop and python-for-android entry point."""

import os

# Avoid measurement data in persistent GUI logs.
os.environ.setdefault("KIVY_NO_FILELOG", "1")

from vitalregistro.app import VitalRegistroApp


if __name__ == "__main__":
    VitalRegistroApp().run()
