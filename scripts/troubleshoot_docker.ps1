# Troubleshooting script for Docker/Postgres setup
# Run this script in PowerShell if you encounter issues

Write-Host "=== Docker Troubleshooting Script ===" -ForegroundColor Cyan

# Check Docker status
Write-Host "`n[1] Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "    Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "    ERROR: Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check docker-compose
Write-Host "`n[2] Checking docker-compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version 2>&1
    Write-Host "    docker-compose: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "    WARNING: docker-compose not found. Using 'docker compose' instead." -ForegroundColor Yellow
}

# Check port 5432
Write-Host "`n[3] Checking port 5432..." -ForegroundColor Yellow
$port5432 = netstat -ano | Select-String ":5432 "
if ($port5432) {
    Write-Host "    WARNING: Port 5432 is in use:" -ForegroundColor Yellow
    $port5432 | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
    
    # Get process info
    $pids = $port5432 | ForEach-Object { ($_ -split '\s+')[-1] } | Sort-Object -Unique
    foreach ($pid in $pids) {
        $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "    Process: $($process.ProcessName) (PID: $pid)" -ForegroundColor Yellow
        }
    }
    
    Write-Host "`n    To fix: Either stop the process using port 5432, or change the port in docker-compose.yml" -ForegroundColor Cyan
    Write-Host "    Example: Change '5432:5432' to '5433:5432' in docker-compose.yml" -ForegroundColor Cyan
} else {
    Write-Host "    Port 5432 is free." -ForegroundColor Green
}

# Check port 8088
Write-Host "`n[4] Checking port 8088 (mock server)..." -ForegroundColor Yellow
$port8088 = netstat -ano | Select-String ":8088 "
if ($port8088) {
    Write-Host "    WARNING: Port 8088 is in use:" -ForegroundColor Yellow
    $port8088 | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
} else {
    Write-Host "    Port 8088 is free." -ForegroundColor Green
}

# Check port 8000
Write-Host "`n[5] Checking port 8000 (backend)..." -ForegroundColor Yellow
$port8000 = netstat -ano | Select-String ":8000 "
if ($port8000) {
    Write-Host "    WARNING: Port 8000 is in use:" -ForegroundColor Yellow
    $port8000 | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
} else {
    Write-Host "    Port 8000 is free." -ForegroundColor Green
}

Write-Host "`n=== Quick Start Commands ===" -ForegroundColor Cyan
Write-Host "cd G:\TTMT\datn" -ForegroundColor White
Write-Host "docker-compose up -d postgres          # Start only Postgres" -ForegroundColor White
Write-Host "docker-compose up -d mock_server       # Start only Mock Server" -ForegroundColor White
Write-Host "docker-compose up -d                   # Start all services" -ForegroundColor White
Write-Host "docker-compose logs -f postgres        # View Postgres logs" -ForegroundColor White
Write-Host "docker-compose logs -f backend         # View Backend logs" -ForegroundColor White

Write-Host "`n=== After Stack is Running ===" -ForegroundColor Cyan
Write-Host "# Test Postgres connection" -ForegroundColor White
Write-Host 'docker exec vehicle_lpr_postgres psql -U postgres -d vehicle_lpr -c "SELECT 1"' -ForegroundColor White
Write-Host "`n# Setup sample camera" -ForegroundColor White
Write-Host 'docker exec -i vehicle_lpr_postgres psql -U postgres -d vehicle_lpr < scripts/setup_sample_camera.sql' -ForegroundColor White
Write-Host "`n# Run import script" -ForegroundColor White
Write-Host 'python scripts/import_vehicle_events.py' -ForegroundColor White
Write-Host "`n# Test mock server" -ForegroundColor White
Write-Host 'curl http://localhost:8088/health' -ForegroundColor White

Write-Host "`n=== Done ===" -ForegroundColor Cyan
