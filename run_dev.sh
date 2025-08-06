#!/usr/bin/env bash
set -euo pipefail

# Configurable ports via env
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-8080}"

# Ensure backend deps are installed (optional; comment out if you manage env separately)
# pip install -r backend/requirements.txt >/dev/null

echo "[dev] Starting backend on :${BACKEND_PORT}"
uvicorn backend.app:app --host 0.0.0.0 --port "${BACKEND_PORT}" --reload &
BACK_PID=$!

echo "[dev] Starting frontend on :${FRONTEND_PORT}"
python -m http.server "${FRONTEND_PORT}" --directory frontend &
FRONT_PID=$!

cleanup() {
  echo
  echo "[dev] Stopping services..."
  kill "${BACK_PID}" "${FRONT_PID}" 2>/dev/null || true
}
trap cleanup EXIT

echo "[dev] Backend:  http://localhost:${BACKEND_PORT}"
echo "[dev] Frontend: http://localhost:${FRONTEND_PORT}/index.html"
echo "[dev] Press Ctrl+C to stop."
wait
