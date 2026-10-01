"""Prepare the build interpreter without replacing the notebook kernel.

The runtime Python only bootstraps uv. p4a gets a pinned CPython 3.14
environment and builds its own matching host/target Python recipes.
"""

import json
import os
from pathlib import Path
import platform
import subprocess
import sys

BUILD_PYTHON = "3.14.7"
UV_VERSION = "0.12.21"
ROOT = Path(__file__).resolve().parents[1]


def interpreter_info(executable):
    result = subprocess.run(
        [str(executable), "-c",
         "import json,sys,sysconfig; print(json.dumps({'version': list(sys.version_info[:3]), "
         "'implementation': sys.implementation.name, 'free_threaded': bool(sysconfig.get_config_var('Py_GIL_DISABLED'))}))"],
        check=True, text=True, stdout=subprocess.PIPE,
    )
    return json.loads(result.stdout)


def compatible_interpreter(info):
    return (tuple(info["version"]) == tuple(map(int, BUILD_PYTHON.split(".")))
            and info["implementation"] == "cpython" and not info["free_threaded"])


def require_linux():
    if sys.platform != "linux" or platform.machine() != "x86_64":
        raise RuntimeError("The Android build requires Linux x86_64; use Colab CPU or WSL2.")


def build_python(root=ROOT):
    executable = root / ".venv-build/bin/python"
    if not executable.exists() or not compatible_interpreter(interpreter_info(executable)):
        raise RuntimeError(f"Run scripts/setup_linux.sh to prepare CPython {BUILD_PYTHON}.")
    return executable


def android_environment(root=ROOT):
    require_linux()
    build_python(root)
    env = os.environ.copy()
    # Never inherit notebook package paths into the compiler environment.
    for key in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV"):
        env.pop(key, None)
    env["VIRTUAL_ENV"] = str(root / ".venv-build")
    env["JAVA_HOME"] = "/usr/lib/jvm/java-17-openjdk-amd64"
    env["CARGO_HOME"] = str(root / ".build-tools/cargo")
    env["RUSTUP_HOME"] = str(root / ".build-tools/rustup")
    env["PATH"] = os.pathsep.join((str(root / ".venv-build/bin"), env["JAVA_HOME"] + "/bin",
                                   env["CARGO_HOME"] + "/bin", env.get("PATH", "")))
    env["PYTHONUNBUFFERED"] = "1"
    return env


def prepare(root=ROOT):
    require_linux()
    print("Runtime Python:", sys.version, flush=True)
    if sys.version_info < (3, 10):
        raise RuntimeError("Bootstrap requires Python >=3.10.")
    target = root / ".venv-build"
    if target.exists():
        # Do not erase or mix an old master/3.12 environment with the new one.
        existing = target / "bin/python"
        if not existing.exists() or not compatible_interpreter(interpreter_info(existing)):
            raise RuntimeError("Existing .venv-build is incompatible. Rename it or start a fresh Colab session.")
    else:
        source_python = sys.executable
        if not compatible_interpreter(interpreter_info(source_python)):
            bootstrap = root / ".build-tools/bootstrap"
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(bootstrap),
                            f"uv=={UV_VERSION}"], check=True)
            uv_env = os.environ.copy()
            uv_env["PYTHONPATH"] = str(bootstrap)
            uv_env["UV_PYTHON_INSTALL_DIR"] = str(root / ".build-tools/python")
            uv = [sys.executable, "-m", "uv", "--no-config"]
            subprocess.run(uv + ["python", "install", "--no-bin", BUILD_PYTHON], check=True, env=uv_env)
            found = subprocess.run(uv + ["python", "find", "--managed-python", BUILD_PYTHON],
                                   check=True, env=uv_env, text=True, stdout=subprocess.PIPE)
            source_python = found.stdout.strip()
        if not compatible_interpreter(interpreter_info(source_python)):
            raise RuntimeError(f"Expected CPython {BUILD_PYTHON} with GIL; refusing an incompatible build.")
        # Use the selected interpreter, not whichever python3 happens to be on PATH.
        subprocess.run([str(source_python), "-m", "venv", str(target)], check=True)
    executable = build_python(root)
    subprocess.run([str(executable), "-m", "pip", "install", "-r", str(root / "requirements-build.txt")], check=True)
    subprocess.run([str(executable), "-m", "pip", "check"], check=True)
    print("Build Python:", interpreter_info(executable), flush=True)
    subprocess.run([str(target / "bin/buildozer"), "--version"], check=True)


if __name__ == "__main__":
    prepare()
