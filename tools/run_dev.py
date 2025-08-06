#!/usr/bin/env python3
import shutil
import subprocess
import sys

def main():
    if shutil.which("uvicorn") is None:
        print("ERROR: uvicorn not found. Install with: pip install uvicorn[standard]", file=sys.stderr)
        return 1
    cmd = ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(main())
