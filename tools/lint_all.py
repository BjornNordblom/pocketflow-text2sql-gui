#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def run(cmd, cwd=None):
    print(f"+ {' '.join(cmd)}", flush=True)
    try:
        return subprocess.run(cmd, cwd=cwd, check=False).returncode
    except FileNotFoundError:
        return 127

def main():
    parser = argparse.ArgumentParser(description="Lint backend (ruff) and frontend (eslint) cross-platform.")
    parser.add_argument("--fix", action="store_true", help="Attempt to auto-fix issues where supported.")
    args = parser.parse_args()

    print("==> Lint: backend (Python) with ruff")
    if shutil.which("ruff") is None:
        print("ERROR: ruff not found. Install with: pip install ruff", file=sys.stderr)
        return 1
    rc = run(["ruff", "--version"], cwd=REPO_ROOT)
    if rc != 0:
        return rc
    ruff_cmd = ["ruff", "check", "backend"]
    if args.fix:
        ruff_cmd.append("--fix")
    rc = run(ruff_cmd, cwd=REPO_ROOT)
    if rc != 0:
        return rc

    print("==> Lint: frontend (JavaScript) with ESLint")
    if shutil.which("node") is None:
        print("ERROR: Node.js not found. Install Node to run ESLint.", file=sys.stderr)
        return 1
    eslint_cmd = ["npx", "eslint", "frontend/**/*.js"]
    if args.fix:
        eslint_cmd.append("--fix")
    rc = run(eslint_cmd, cwd=REPO_ROOT)
    if rc != 0:
        return rc

    print("All lint checks passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
