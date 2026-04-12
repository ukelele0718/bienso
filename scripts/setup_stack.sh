#!/usr/bin/env bash
# Full Stack Setup Script
# Run this from project root: ./scripts/setup_stack.sh

set -e

echo "========================================="
echo "  Vehicle LPR System - Full Stack Setup"
echo "========================================="

cd "$(dirname "$0")/.."

echo ""
echo "[1/5] Starting Docker stack..."
docker-compose up -d postgres mock_server
sleep 5

echo ""
echo "[2/5] Checking Postgres is ready..."
until docker exec vehicle_lpr_postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo "    Waiting for Postgres..."
    sleep 2
done
echo "    Postgres is ready!"

echo ""
echo "[3/5] Starting backend (runs migrations)..."
docker-compose up -d backend
sleep 10

echo ""
echo "[4/5] Setting up sample camera..."
docker exec -i vehicle_lpr_postgres psql -U postgres -d vehicle_lpr < scripts/setup_sample_camera.sql

echo ""
echo "[5/5] Running import script..."
pip install psycopg2-binary --quiet 2>/dev/null || true
python scripts/import_vehicle_events.py

echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Services running:"
echo "  - Postgres:    localhost:5432"
echo "  - Backend:     http://localhost:8000"
echo "  - Mock Server: http://localhost:8088"
echo ""
echo "Test commands:"
echo "  curl http://localhost:8000/docs          (API docs)"
echo "  curl http://localhost:8088/health        (Mock server health)"
echo ""
echo "View logs:"
echo "  docker-compose logs -f backend"
