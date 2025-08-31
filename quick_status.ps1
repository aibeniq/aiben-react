#!/usr/bin/env powershell
# Quick deployment status check

cd "C:\miniconda\aibeniq-react"

Write-Host "=== AIBeniq Deployment Status ===" -ForegroundColor Yellow

# Load OpenShift token
$env:OPENSHIFT_TOKEN = (Get-Content .env | Where-Object { $_ -match "OPENSHIFT_TOKEN=" } | ForEach-Object { $_.Split('=')[1] })

# Login
Write-Host "Logging in to OpenShift..." -ForegroundColor Blue
oc login --token=$env:OPENSHIFT_TOKEN --server=https://api.aibeniq-prod.gimc.p1.openshiftapps.com:6443

# Switch to dev namespace
Write-Host "Switching to aibeniq-dev namespace..." -ForegroundColor Blue
oc project aibeniq-dev

Write-Host "`nDeployment status:" -ForegroundColor Green
oc get deployments

Write-Host "`nPod status:" -ForegroundColor Green
oc get pods

Write-Host "`nML Configuration:" -ForegroundColor Green
$enablePytorch = oc get configmap backend-config -o jsonpath='{.data.ENABLE_PYTORCH}' 2>$null
$runtimeInstall = oc get configmap backend-config -o jsonpath='{.data.RUNTIME_INSTALL_PYTORCH}' 2>$null
Write-Host "ENABLE_PYTORCH: $enablePytorch"
Write-Host "RUNTIME_INSTALL_PYTORCH: $runtimeInstall"

Write-Host "`nRecent events:" -ForegroundColor Green
oc get events --sort-by=.metadata.creationTimestamp | Select-Object -Last 5

Write-Host "`n=== Status Check Complete ===" -ForegroundColor Yellow
