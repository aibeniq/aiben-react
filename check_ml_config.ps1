#!/usr/bin/env powershell
# Quick script to check ML configuration in ConfigMap

Write-Host "Checking ML environment configuration..." -ForegroundColor Yellow

try {
    Write-Host "`nCurrent project:"
    oc project
    
    Write-Host "`nConfigMap status:"
    oc get configmap backend-config -o name 2>&1
    
    Write-Host "`nPyTorch-related environment variables:"
    $enablePytorch = oc get configmap backend-config -o jsonpath='{.data.ENABLE_PYTORCH}' 2>&1
    $runtimeInstall = oc get configmap backend-config -o jsonpath='{.data.RUNTIME_INSTALL_PYTORCH}' 2>&1
    
    Write-Host "ENABLE_PYTORCH: $enablePytorch" -ForegroundColor Cyan
    Write-Host "RUNTIME_INSTALL_PYTORCH: $runtimeInstall" -ForegroundColor Cyan
    
    Write-Host "`nFull ConfigMap data (filtered for ML):"
    oc get configmap backend-config -o yaml | Select-String "PYTORCH|ENABLE_" -Context 1
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nDone!" -ForegroundColor Green
