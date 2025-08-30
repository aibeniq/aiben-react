#!/usr/bin/env pwsh
# Test Script - Verify Database Authentication Fix

Write-Host "=== Testing Database Authentication Fix ===" -ForegroundColor Green

# 1. Check that passwords match between secret and DATABASE_URL
Write-Host "`n1. Checking password consistency..." -ForegroundColor Yellow
$dbPassword = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret backend-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}')))
$databaseUrl = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret backend-secrets -o jsonpath='{.data.DATABASE_URL}')))

Write-Host "POSTGRES_PASSWORD: $dbPassword"
Write-Host "DATABASE_URL: $databaseUrl"

if ($databaseUrl -match "postgresql://app:(.+)@postgres:5432/aibeniq") {
    $urlPassword = $matches[1]
    if ($urlPassword -eq $dbPassword) {
        Write-Host "✅ Passwords MATCH!" -ForegroundColor Green
    } else {
        Write-Host "❌ Passwords DON'T MATCH!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Invalid DATABASE_URL format!" -ForegroundColor Red
    exit 1
}

# 2. Test direct database connection
Write-Host "`n2. Testing direct database connection..." -ForegroundColor Yellow
$testCmd = "PGPASSWORD='$dbPassword' psql -U app -d aibeniq -c 'SELECT current_user, current_database();'"
$result = oc exec deployment/postgres -- bash -c $testCmd 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Direct database connection works!" -ForegroundColor Green
    Write-Host "Result: $result" -ForegroundColor Gray
} else {
    Write-Host "❌ Direct database connection failed!" -ForegroundColor Red
    Write-Host "Error: $result" -ForegroundColor Red
    exit 1
}

# 3. Check backend pod status
Write-Host "`n3. Checking backend pod status..." -ForegroundColor Yellow
$backendPods = oc get pods -l component=backend -o jsonpath='{.items[*].metadata.name}'
if ($backendPods) {
    Write-Host "Backend pods: $backendPods" -ForegroundColor Gray
    $podStatus = oc get pods -l component=backend -o jsonpath='{.items[0].status.phase}'
    Write-Host "Backend status: $podStatus" -ForegroundColor Gray
    
    if ($podStatus -eq "Running") {
        Write-Host "✅ Backend pod is running!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Backend pod status: $podStatus" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ No backend pods found!" -ForegroundColor Red
    exit 1
}

# 4. Check for recent database errors in backend logs
Write-Host "`n4. Checking for recent database errors..." -ForegroundColor Yellow
$recentErrors = oc logs deployment/backend --since=5m 2>/dev/null | Select-String "password authentication failed"

if ($recentErrors.Count -eq 0) {
    Write-Host "✅ No recent database authentication errors!" -ForegroundColor Green
} else {
    Write-Host "❌ Found $($recentErrors.Count) recent database errors!" -ForegroundColor Red
    $recentErrors | Select-Object -First 3 | ForEach-Object { Write-Host "  $($_)" -ForegroundColor Red }
    Write-Host "Consider running: .\scripts\setup-secrets.ps1 -Environment dev -ForcePasswordRotate" -ForegroundColor Cyan
}

# 5. Test backend API health check
Write-Host "`n5. Testing backend API health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://redhat-api.aiben.io/api/v1/utils/health-check/" -Method GET -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend API health check passed!" -ForegroundColor Green
        Write-Host "Response: $($response.Content)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️ Backend API returned status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Backend API health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
Write-Host "If all checks passed, your database authentication issue is resolved!" -ForegroundColor Cyan
Write-Host "You can now test your application at: http://redhat.aiben.io" -ForegroundColor Cyan
