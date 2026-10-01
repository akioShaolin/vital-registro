#!/usr/bin/env bash
# Ubuntu 22.04/24.04 or compatible Colab. Run from the repository root.
set -euo pipefail

python3 -c 'import sys; assert (3, 10) <= sys.version_info[:2] <= (3, 12), "Use Python 3.10–3.12 for this p4a master build; see docs/ANDROID.md"'
sudo apt-get update
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip python3-venv \
  autoconf automake libtool pkg-config zlib1g-dev libncurses-dev cmake \
  libffi-dev libssl-dev build-essential ccache gettext autopoint

python3 -m venv .venv-build
.venv-build/bin/python -m pip install -r requirements-build.txt
printf '%s\n' 'Tools installed. Activate .venv-build and run: buildozer -v android debug'
