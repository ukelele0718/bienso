#!/usr/bin/env bash
# Quick-start dashboard without Docker (local dev)
# Usage: bash scripts/quick-dashboard.sh
set -e
cd "$(dirname "$0")/../apps/dashboard"

echo "[dashboard] Installing deps..."
npm install --silent 2>/dev/null

echo "[dashboard] Starting dev server on :5173..."
echo "[dashboard] API proxy -> http://127.0.0.1:8000 (via vite.config.ts)"
npm run dev
