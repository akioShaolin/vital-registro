"""Read-only audit of candidate files, config and notebook Python cells."""

import ast
import configparser
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check():
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=ROOT, capture_output=True, check=True)
    names = sorted(set(result.stdout.decode("utf-8").split("\0")) - {""})
    problems = []
    for name in names:
        path = Path(name)
        if path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".apk", ".aab", ".pem", ".key", ".jks"}:
            problems.append(f"Private/generated file: {name}")
        if path.suffix.lower() == ".csv" and not name.startswith("tests/fixtures/"):
            problems.append(f"Review CSV data: {name}")
        if path.name.startswith(".env"):
            problems.append(f"Environment file: {name}")
        if path.suffix in {".py", ".md", ".kv", ".yml", ".txt", ".spec", ".ipynb"}:
            text = (ROOT / name).read_text(encoding="utf-8")
            # Match token-like values, not references to environment variables.
            secret_pattern = r"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|" + "-----" + r"BEGIN .*PRIVATE KEY-----"
            if re.search(secret_pattern, text):
                problems.append(f"Possible credential: {name}")
            if re.search(r"[A-Za-z]:[\\/]+Users[\\/]+[^\s]+", text):
                problems.append(f"Local user path: {name}")
    spec = configparser.ConfigParser(interpolation=None)
    spec.read(ROOT / "buildozer.spec", encoding="utf-8")
    assert spec["app"]["android.permissions"].strip() == ""
    assert spec["app"].getboolean("android.allow_backup") is False
    icon = spec["app"]["icon.filename"].replace("%(source.dir)s/", "")
    assert (ROOT / icon).is_file()
    notebook = json.loads((ROOT / "docs/build_colab.ipynb").read_text(encoding="utf-8"))
    for index, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] == "code":
            ast.parse("".join(cell["source"]), filename=f"colab-cell-{index}")
    assert (ROOT / "LICENSE").is_file()
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"Repository audit: PASS ({len(names)} candidate files; notebook syntax, icon and permissions checked)")
    print("Automated checks do not replace manual review of data and images.")


if __name__ == "__main__":
    check()
