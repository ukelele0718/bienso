@echo off
REM Full Stack Setup Script
REM Run this from G:\TTMT\datn directory

echo =========================================
echo   Vehicle LPR System - Full Stack Setup
echo =========================================

cd /d G:\TTMT\datn

echo.
echo [1/5] Starting Docker stack...
docker-compose up -d postgres mock_server
timeout /t 10 /nobreak > nul

echo.
echo [2/5] Checking Postgres is ready...
:wait_postgres
docker exec vehicle_lpr_postgres pg_isready -U postgres > nul 2>&1
if errorlevel 1 (
    echo     Waiting for Postgres...
    timeout /t 2 /nobreak > nul
    goto wait_postgres
)
echo     Postgres is ready!

echo.
echo [3/5] Starting backend (runs migrations)...
docker-compose up -d backend
timeout /t 15 /nobreak > nul

echo.
echo [4/5] Setting up sample camera...
docker exec -i vehicle_lpr_postgres psql -U postgres -d vehicle_lpr < scripts\setup_sample_camera.sql

echo.
echo [5/5] Running import script...
REM Install psycopg2 if needed
pip install psycopg2-binary --quiet 2>nul
python scripts\import_vehicle_events.py

echo.
echo =========================================
echo   Setup Complete!
echo =========================================
echo.
echo Services running:
echo   - Postgres:    localhost:5432
echo   - Backend:     http://localhost:8000
echo   - Mock Server: http://localhost:8088
echo.
echo Test commands:
echo   curl http://localhost:8000/docs          (API docs)
echo   curl http://localhost:8088/health        (Mock server health)
echo.
echo View logs:
echo   docker-compose logs -f backend
echo.
pause
