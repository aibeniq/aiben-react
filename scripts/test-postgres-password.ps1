#!/usr/bin/env pwsh
# PostgreSQL Password Mismatch Detection and Resolution

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod")]
    [string]$Environment,
    [switch]$DestructiveReset
)

Write-Host "=== PostgreSQL Password Test ($Environment) ===" -ForegroundColor Green

# Set namespace
$namespace = if ($Environment -eq "dev") { "aibeniq-dev" } else { "aibeniq-prod" }

# Check login
oc whoami | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Not logged into OpenShift" -ForegroundColor Red
    exit 1
}

oc project $namespace

# Check if PostgreSQL is running
$pgRunning = oc get pod -l app=aibeniq,component=postgres --field-selector=status.phase=Running --no-headers 2>$null
if (-not $pgRunning -or $pgRunning.Length -eq 0) {
    Write-Host "PostgreSQL pod not running" -ForegroundColor Yellow
    exit 1
}

Write-Host "PostgreSQL pod is running" -ForegroundColor Green

# Get password from secret
$currentPassword = oc get secret backend-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}' | ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }

if (-not $currentPassword) {
    Write-Host "[ERROR] Could not get password from secret" -ForegroundColor Red
    exit 1
}

Write-Host "Retrieved password: $($currentPassword.Substring(0,8))..." -ForegroundColor Green

# Test password
Write-Host "Testing database connection..." -ForegroundColor Yellow
$cmd = "PGPASSWORD='$currentPassword' psql -U app -d aibeniq -h postgres -c '\dt' >/dev/null 2>&1"
oc exec deploy/postgres -- bash -c "$cmd" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Database password works!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Password mismatch detected!" -ForegroundColor Red
    
    if ($DestructiveReset) {
        Write-Host "Performing destructive reset..." -ForegroundColor Red
        oc delete deployment postgres --ignore-not-found=true
        oc delete pvc -l app=aibeniq,component=postgres --ignore-not-found=true
        Write-Host "Reset complete. Redeploy to fix." -ForegroundColor Green
    } else {
        Write-Host "Use -DestructiveReset to fix the mismatch" -ForegroundColor Yellow
    }
}

Write-Host "Password test complete" -ForegroundColor Green
