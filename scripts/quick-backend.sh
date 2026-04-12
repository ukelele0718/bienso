#!/usr/bin/env bash
# Quick-start backend without Docker (local dev)
# Usage: bash scripts/quick-backend.sh
set -e
cd "$(dirname "$0")/.."

echo "[backend] Checking venv..."
if [ ! -d ".venv" ]; then
  echo "[backend] Creating venv..."
  python -m venv .venv
fi

echo "[backend] Installing deps..."
.venv/Scripts/pip install -q -r apps/backend/requirements.txt 2>/dev/null || \
  .venv/bin/pip install -q -r apps/backend/requirements.txt

echo "[backend] Running migrations..."
cd apps/backend
PYTHONPATH=. python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine)" 2>/dev/null || true

echo "[backend] Starting uvicorn on :8000..."
PYTHONPATH=. python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
