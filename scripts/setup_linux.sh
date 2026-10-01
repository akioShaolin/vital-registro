#!/usr/bin/env bash
# Ubuntu/Colab: system tools + an isolated modern Android build interpreter.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_dir"
bootstrap_python="${VITALREGISTRO_BOOTSTRAP_PYTHON:-python3}"

if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
  printf '%s\n' 'Use Linux x86_64 (Colab CPU or WSL2). Android NDK Linux prebuilt requires this host.' >&2
  exit 1
fi
"$bootstrap_python" -c 'import sys; print("Bootstrap Python:", sys.version); assert sys.version_info >= (3, 10), "Bootstrap requires Python >=3.10; build Python is installed separately"'

admin=()
if [[ "$EUID" -ne 0 ]]; then
  admin=(sudo)
fi
"${admin[@]}" apt-get update
"${admin[@]}" apt-get install -y git zip unzip openjdk-17-jdk python3-pip \
  autoconf automake libtool libltdl-dev pkg-config zlib1g-dev libncurses-dev \
  cmake libffi-dev libssl-dev build-essential ccache gettext autopoint curl ca-certificates

# Rust is part of the current upstream build-tool prerequisites. Keep it local.
export CARGO_HOME="$project_dir/.build-tools/cargo"
export RUSTUP_HOME="$project_dir/.build-tools/rustup"
mkdir -p "$project_dir/.build-tools"
if [[ ! -x "$CARGO_HOME/bin/rustup" ]]; then
  curl --fail --location --proto '=https' --tlsv1.2 https://sh.rustup.rs \
    --output "$project_dir/.build-tools/rustup-init.sh"
  sh "$project_dir/.build-tools/rustup-init.sh" -y --profile minimal --no-modify-path
fi
"$CARGO_HOME/bin/rustup" toolchain install stable --profile minimal
"$CARGO_HOME/bin/rustup" default stable
"$CARGO_HOME/bin/rustc" --version

"$bootstrap_python" scripts/build_environment.py
printf '%s\n' 'Tools ready. Run: .venv-build/bin/python scripts/build_android.py'
