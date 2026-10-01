"""No SDK downloads: exercise interpreter selection and build failure handling."""

import configparser
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import build_environment as buildenv


def info(version, implementation="cpython", free_threaded=False):
    return {"version": version, "implementation": implementation, "free_threaded": free_threaded}


class BuildEnvironmentTests(unittest.TestCase):
    def test_exact_supported_interpreter_and_gil_are_required(self):
        self.assertTrue(buildenv.compatible_interpreter(info([3, 14, 7])))
        for value in (info([3, 13, 7]), info([3, 15, 0]), info([3, 14, 7], "pypy"),
                      info([3, 14, 7], free_threaded=True)):
            with self.subTest(info=value):
                self.assertFalse(buildenv.compatible_interpreter(value))

    def test_colab_313_installs_314_without_replacing_kernel(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            executable = root / ".venv-build/bin/python"
            with (patch.object(buildenv, "require_linux"),
                  patch.object(buildenv, "interpreter_info", side_effect=[info([3, 13, 7]), info([3, 14, 7]), info([3, 14, 7])]),
                  patch.object(buildenv, "build_python", return_value=executable),
                  patch.object(buildenv.subprocess, "run", return_value=SimpleNamespace(stdout="/managed/python3.14\n")) as run):
                buildenv.prepare(root)
            commands = [call.args[0] for call in run.call_args_list]
            self.assertIn([sys.executable, "-m", "uv", "--no-config", "python", "install", "--no-bin", "3.14.7"], commands)
            self.assertIn(["/managed/python3.14", "-m", "venv", str(root / ".venv-build")], commands)
            self.assertTrue(all(call.kwargs["check"] for call in run.call_args_list))
            self.assertFalse(any("3.12" in str(command) for command in commands))

    def test_compatible_kernel_does_not_download_another_python(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with (patch.object(buildenv, "require_linux"),
                  patch.object(buildenv, "interpreter_info", return_value=info([3, 14, 7])),
                  patch.object(buildenv, "build_python", return_value=root / ".venv-build/bin/python"),
                  patch.object(buildenv.subprocess, "run") as run):
                buildenv.prepare(root)
            commands = [call.args[0] for call in run.call_args_list]
            self.assertIn([sys.executable, "-m", "venv", str(root / ".venv-build")], commands)
            self.assertFalse(any("uv" in command for command in commands))

    def test_old_environment_is_not_deleted_or_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            executable = root / ".venv-build/bin/python"
            executable.parent.mkdir(parents=True)
            executable.write_text("old environment", encoding="utf-8")
            with (patch.object(buildenv, "require_linux"),
                  patch.object(buildenv, "interpreter_info", return_value=info([3, 12, 0])),
                  patch.object(buildenv.subprocess, "run") as run,
                  self.assertRaisesRegex(RuntimeError, "incompatible")):
                buildenv.prepare(root)
            run.assert_not_called()
            self.assertEqual(executable.read_text(encoding="utf-8"), "old environment")

    def test_failed_bootstrap_aborts_before_build_installation(self):
        with tempfile.TemporaryDirectory() as folder:
            with (patch.object(buildenv, "require_linux"),
                  patch.object(buildenv, "interpreter_info", return_value=info([3, 13, 7])),
                  patch.object(buildenv.subprocess, "run", side_effect=subprocess.CalledProcessError(1, ["pip"])) as run,
                  self.assertRaises(subprocess.CalledProcessError)):
                buildenv.prepare(Path(folder))
            self.assertEqual(run.call_count, 1)

    def test_build_uses_java17_and_does_not_inherit_kernel_packages(self):
        with (patch.object(buildenv, "require_linux"), patch.object(buildenv, "build_python"),
              patch.dict("os.environ", {"PYTHONPATH": "/kernel/packages", "PYTHONHOME": "/kernel", "PATH": "/usr/bin"})):
            env = buildenv.android_environment(Path("/project"))
        self.assertNotIn("PYTHONPATH", env)
        self.assertNotIn("PYTHONHOME", env)
        self.assertIn("java-17", env["JAVA_HOME"])
        self.assertTrue(env["PATH"].startswith(str(Path("/project/.venv-build/bin"))))


class ColabFlowTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.notebook = json.loads((self.root / "docs/build_colab.ipynb").read_text(encoding="utf-8"))

    def test_failed_build_invalidates_download_even_after_previous_success(self):
        cell = next("".join(cell["source"]) for cell in self.notebook["cells"]
                    if cell["cell_type"] == "code" and "'scripts/build_android.py'" in "".join(cell["source"]))
        scope = {"build_succeeded": True, "build_python": Path("/build/python"), "subprocess": subprocess}
        with (patch.object(subprocess, "run", side_effect=subprocess.CalledProcessError(1, "buildozer")),
              self.assertRaises(subprocess.CalledProcessError)):
            exec(compile(cell, "build-cell", "exec"), scope)
        self.assertFalse(scope["build_succeeded"])

    def test_notebook_cells_parse_and_point_to_real_repository(self):
        for index, cell in enumerate(self.notebook["cells"]):
            if cell["cell_type"] == "code":
                compile("".join(cell["source"]), f"cell-{index}", "exec")
        self.assertIn("https://github.com/akioShaolin/vital-registro.git", json.dumps(self.notebook))

    def test_modern_config_preserves_offline_permissions(self):
        spec = configparser.ConfigParser(interpolation=None)
        spec.read(self.root / "buildozer.spec", encoding="utf-8")
        app = spec["app"]
        self.assertEqual(app["android.api"], "36")
        self.assertEqual(app["android.ndk"], "29")
        self.assertEqual(app["p4a.branch"], "develop")
        self.assertRegex(app["p4a.commit"], r"^[a-f0-9]{40}$")
        self.assertEqual(app["android.permissions"], "")
        self.assertFalse(app.getboolean("android.allow_backup"))
        self.assertFalse(app.getboolean("android.accept_sdk_license"))


if __name__ == "__main__":
    unittest.main()
