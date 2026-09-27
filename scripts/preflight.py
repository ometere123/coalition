"""Repository-level static preflight. It does not require a funded account."""

from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> None:
    package = json.loads((ROOT / "package.json").read_text())
    if package.get("devDependencies", {}).get("genlayer") != "0.39.1":
        fail("package.json must pin genlayer 0.39.1")

    config = (ROOT / "gltest.config.yaml").read_text()
    if "https://studio.genlayer.com/api" not in config:
        fail("stable Studionet RPC missing")
    if "studio-dev" in config or "61997" in config:
        fail("studio-dev/61997 leaked into stable config")

    contract = (ROOT / "contracts" / "coalition.py").read_text()
    for marker in ("class Coalition(gl.Contract)", "gl.vm.run_nondet_unsafe", "_choose_coalition", "_matrix_complete"):
        if marker not in contract:
            fail(f"missing contract marker: {marker}")

    subprocess.run([sys.executable, "-m", "py_compile", str(ROOT / "contracts" / "coalition.py")], check=True)
    subprocess.run([sys.executable, "-m", "py_compile", str(ROOT / "tests" / "direct" / "test_coalition.py")], check=True)

    readme = (ROOT / "README.md").read_text()
    if "61999" not in readme or "Studionet" not in readme:
        fail("README stable network declaration missing")

    print("OK: static preflight passed")
    print("NEXT: npm install && npx genlayer --version")
    print("NEXT: pytest tests/direct -q")
    print("NEXT: npx genlayer network set studionet && npx genlayer network info")


if __name__ == "__main__":
    main()
