#!/usr/bin/env bash
set -euo pipefail
exec python3 tools/lint_all.py "$@"
