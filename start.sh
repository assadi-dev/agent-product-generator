#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$SCRIPT_DIR/.venv/bin/python"

echo "Starting backend  -> http://localhost:8000"
"$PYTHON" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting frontend -> http://localhost:8501"
"$PYTHON" -m streamlit run frontend/app.py --server.port=8501 &
FRONTEND_PID=$!

echo "Press Ctrl+C to stop both services"

cleanup() {
    echo "Stopping..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
    echo "Stopped."
}

trap cleanup SIGINT SIGTERM

wait "$BACKEND_PID" "$FRONTEND_PID"
