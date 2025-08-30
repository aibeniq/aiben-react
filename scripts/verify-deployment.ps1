#!/usr/bin/env pwsh
# Quick deployment verification script

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod")]
    [string]$Environment
)

$namespace = if ($Environment -eq "dev") { "aibeniq-dev" } else { "aibeniq-prod" }

Write-Host "=== AIBeniq Deployment Verification ($Environment) ===" -ForegroundColor Green

# Switch to the correct project
Write-Host "Switching to project: $namespace" -ForegroundColor Yellow
oc project $namespace

Write-Host "`n=== Pod Status ===" -ForegroundColor Yellow
oc get pods

Write-Host "`n=== Deployment Status ===" -ForegroundColor Yellow
oc get deployments

Write-Host "`n=== Service Status ===" -ForegroundColor Yellow
oc get services

Write-Host "`n=== Route Status ===" -ForegroundColor Yellow
oc get routes

Write-Host "`n=== Secret Status ===" -ForegroundColor Yellow
oc get secrets | Select-String -Pattern "backend-secrets|postgres-secret"

Write-Host "`n=== Application URLs ===" -ForegroundColor Green
$routes = oc get routes -o json | ConvertFrom-Json
foreach ($route in $routes.items) {
    $url = "https://$($route.spec.host)"
    Write-Host "$($route.metadata.name): $url" -ForegroundColor Cyan
}

Write-Host "`n=== Final Verification ===" -ForegroundColor Green
Write-Host "✅ Deployment verification completed" -ForegroundColor Green
