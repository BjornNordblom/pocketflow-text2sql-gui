#!/usr/bin/env bash
# Unix convenience wrapper for the cross-platform linter.
# Prefer on Windows or in CI:
#   python tools/lint_all.py [--fix]
set -euo pipefail
exec python3 tools/lint_all.py "$@"
