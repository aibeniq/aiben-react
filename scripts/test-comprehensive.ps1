# Comprehensive Functionality Test Runner (PowerShell)
# This script runs both backend and frontend comprehensive tests

# Stop script on any error
$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Comprehensive Functionality Tests" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Function to check if service is running
function Test-Service {
    param(
        [string]$ServiceName,
        [int]$Port
    )
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port" -TimeoutSec 5 -UseBasicParsing
        Write-Host "✅ $ServiceName is running on port $Port" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ $ServiceName is not running on port $Port" -ForegroundColor Red
        return $false
    }
}

# Ensure we're in the project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir "..")

$backendFailed = $false
$frontendFailed = $false
$frontendProcess = $null

try {
    # Start services if not running
    Write-Host "`n📦 Checking and starting services..." -ForegroundColor Yellow
    
    if (-not (Test-Service "Backend" 8000)) {
        Write-Host "Starting backend services..." -ForegroundColor Yellow
        & docker compose up -d --wait backend
        Start-Sleep 10
        
        # Check again
        if (-not (Test-Service "Backend" 8000)) {
            Write-Host "❌ Failed to start backend service" -ForegroundColor Red
            exit 1
        }
    }

    if (-not (Test-Service "Frontend" 5173)) {
        Write-Host "Starting frontend development server..." -ForegroundColor Yellow
        Set-Location frontend
        $frontendProcess = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -PassThru -NoNewWindow
        Set-Location ..
        Start-Sleep 15
        
        # Check if frontend started
        if (-not (Test-Service "Frontend" 5173)) {
            Write-Host "❌ Failed to start frontend service" -ForegroundColor Red
            if ($frontendProcess -and -not $frontendProcess.HasExited) {
                $frontendProcess.Kill()
            }
            exit 1
        }
    }

    Write-Host "`n🔧 Running Backend Comprehensive Tests..." -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan

    # Run backend tests
    try {
        & docker compose exec -T backend bash -c "python -m pytest app/tests/test_comprehensive_functionality.py -v --tb=short -x"
        if ($LASTEXITCODE -ne 0) {
            throw "Backend tests failed with exit code $LASTEXITCODE"
        }
    }
    catch {
        Write-Host "❌ Backend tests failed" -ForegroundColor Red
        $backendFailed = $true
    }

    Write-Host "`n🌐 Running Frontend Comprehensive Tests..." -ForegroundColor Cyan
    Write-Host "===========================================" -ForegroundColor Cyan

    # Run frontend tests
    Set-Location frontend

    # Check if playwright is installed
    try {
        & npx playwright --version | Out-Null
    }
    catch {
        Write-Host "Installing Playwright..." -ForegroundColor Yellow
        & npx playwright install chromium
    }

    # Run the comprehensive functionality tests
    try {
        & npx playwright test comprehensive-functionality.spec.ts --reporter=line --timeout=30000
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend tests failed with exit code $LASTEXITCODE"
        }
    }
    catch {
        Write-Host "❌ Frontend tests failed" -ForegroundColor Red
        $frontendFailed = $true
    }

    Set-Location ..

    Write-Host "`n📊 Test Summary" -ForegroundColor Cyan
    Write-Host "===============" -ForegroundColor Cyan

    if ($backendFailed) {
        Write-Host "❌ Backend comprehensive tests: FAILED" -ForegroundColor Red
    } else {
        Write-Host "✅ Backend comprehensive tests: PASSED" -ForegroundColor Green
    }

    if ($frontendFailed) {
        Write-Host "❌ Frontend comprehensive tests: FAILED" -ForegroundColor Red
    } else {
        Write-Host "✅ Frontend comprehensive tests: PASSED" -ForegroundColor Green
    }

    Write-Host ""
    if ($backendFailed -or $frontendFailed) {
        Write-Host "❌ Some tests failed. Check the output above for details." -ForegroundColor Red
        Write-Host ""
        Write-Host "To debug:" -ForegroundColor Yellow
        Write-Host "  Backend: docker compose exec backend bash -c 'python -m pytest app/tests/test_comprehensive_functionality.py -v -s'" -ForegroundColor Yellow
        Write-Host "  Frontend: cd frontend; npx playwright test comprehensive-functionality.spec.ts --ui" -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host "🎉 All comprehensive functionality tests passed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your application successfully handles:" -ForegroundColor Green
        Write-Host "  ✅ Ask functionality (vector `& full scan)" -ForegroundColor Green
        Write-Host "  ✅ Review functionality (upload `& knowledge base)" -ForegroundColor Green
        Write-Host "  ✅ Generate functionality (sections `& outlines)" -ForegroundColor Green
        Write-Host "  ✅ Compare functionality (document comparison)" -ForegroundColor Green
        Write-Host "  ✅ Match functionality (form field extraction)" -ForegroundColor Green
        Write-Host "  ✅ UI navigation and modal workflows" -ForegroundColor Green
        Write-Host "  ✅ Copy button functionality" -ForegroundColor Green
    }
}
finally {
    # Cleanup frontend process if we started it
    if ($frontendProcess -and -not $frontendProcess.HasExited) {
        Write-Host "Stopping frontend development server..." -ForegroundColor Yellow
        $frontendProcess.Kill()
    }

    Write-Host "`n✨ Comprehensive testing completed!" -ForegroundColor Cyan
}
