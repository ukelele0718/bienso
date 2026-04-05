Param(
    [string]$ProjectRoot = "G:/TTMT/datn",
    [string]$DatabaseUrl = "postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr",
    [string]$BaseUrl = "http://localhost:8000",
    [switch]$UseDockerBackend,
    [switch]$SkipBuild,
    [switch]$SkipReset,
    [switch]$SkipMigrations
)

$ErrorActionPreference = "Stop"

function Step($message) {
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host $message -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Ok($message) {
    Write-Host "[OK] $message" -ForegroundColor Green
}

function Warn($message) {
    Write-Host "[WARN] $message" -ForegroundColor Yellow
}

function Fail($message) {
    Write-Host "[FAIL] $message" -ForegroundColor Red
}

try {
    Step "Seeded regression one-command runner"
    Write-Host "ProjectRoot: $ProjectRoot"
    Write-Host "DatabaseUrl: $DatabaseUrl"
    Write-Host "BaseUrl: $BaseUrl"

    if (-not (Test-Path $ProjectRoot)) {
        throw "Project root not found: $ProjectRoot"
    }

    Push-Location $ProjectRoot

    Step "1) Ensure postgres service is up"
    docker compose up -d postgres | Out-Host
    Ok "postgres is up"

    Step "2) Set environment for backend scripts"
    $env:PYTHONPATH = "$ProjectRoot/apps/backend"
    $env:APP_DATABASE_URL = $DatabaseUrl
    $env:DATABASE_URL = $DatabaseUrl
    Ok "environment exported (PYTHONPATH/APP_DATABASE_URL/DATABASE_URL)"

    if (-not $SkipMigrations) {
        Step "3) Run migrations"
        python "$ProjectRoot/apps/backend/scripts/run_migrations.py" | Out-Host
        Ok "migrations completed"
    }
    else {
        Warn "Skip migrations (--SkipMigrations)"
    }

    if (-not $SkipReset) {
        Step "4) Reset deterministic seeded fixture"
        python "$ProjectRoot/scripts/reset_seeded_test_state.py" | Out-Host
        Ok "deterministic fixture prepared"
    }
    else {
        Warn "Skip reset fixture (--SkipReset)"
    }

    if ($UseDockerBackend) {
        Step "5) Start backend via docker compose"
        if ($SkipBuild) {
            docker compose up -d backend | Out-Host
        }
        else {
            docker compose up -d --build backend | Out-Host
        }
        Ok "backend container started"
    }
    else {
        Warn "Backend start is skipped (default). Ensure backend is already running at $BaseUrl"
        Warn "Use -UseDockerBackend to auto start backend container"
    }

    Step "6) Wait backend health"
    $maxAttempts = 30
    $attempt = 0
    $healthy = $false

    while ($attempt -lt $maxAttempts) {
        $attempt++
        try {
            $res = Invoke-WebRequest -Uri "$BaseUrl/health" -UseBasicParsing -TimeoutSec 3
            if ($res.StatusCode -eq 200) {
                $healthy = $true
                break
            }
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }

    if (-not $healthy) {
        throw "backend health check failed after $maxAttempts attempts: $BaseUrl/health"
    }
    Ok "backend is healthy"

    Step "7) Run seeded flow regression"
    python "$ProjectRoot/scripts/test_seeded_flow.py" --base-url $BaseUrl | Out-Host
    Ok "seeded regression completed"

    Step "DONE"
    Ok "All steps finished successfully"
    exit 0
}
catch {
    Step "FAILED"
    Fail $_.Exception.Message
    exit 1
}
finally {
    Pop-Location
}
