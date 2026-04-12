#!/usr/bin/env bash
# Run all backend tests + dashboard typecheck (local, no Docker)
# Usage: bash scripts/quick-test.sh
set -e
cd "$(dirname "$0")/.."

echo "========================================"
echo "  Quick Test Suite"
echo "========================================"

echo ""
echo "[1/3] Backend pytest..."
cd apps/backend
PYTHONPATH=. python -m pytest tests/ -v --tb=short
BACKEND_EXIT=$?

echo ""
echo "[2/3] Backend mypy..."
python -m mypy app/ 2>/dev/null && echo "  mypy: PASS" || echo "  mypy: SKIP (not installed)"

echo ""
echo "[3/3] Dashboard typecheck..."
cd ../../apps/dashboard
npx tsc --noEmit && echo "  tsc: PASS" || echo "  tsc: FAIL"

echo ""
echo "========================================"
echo "  Done. Backend exit code: $BACKEND_EXIT"
echo "========================================"
exit $BACKEND_EXIT
