#!/usr/bin/env bash
set -euo pipefail

echo "==> Lint: backend (Python)"
if command -v ruff >/dev/null 2>&1; then
  ruff --version
  ruff check backend
else
  echo "ruff not found. Install with: pip install ruff"
  exit 1
fi

echo "==> Lint: frontend (JavaScript)"
if command -v node >/dev/null 2>&1; then
  npx --yes eslint@latest "frontend/**/*.js"
else
  echo "Node.js not found. Install Node to run ESLint, or run: npx eslint frontend/**/*.js"
  exit 1
fi

echo "All lint checks passed."
