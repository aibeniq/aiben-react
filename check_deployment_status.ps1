#!/usr/bin/env powershell
# Quick status check script

Write-Host "=== Deployment Status Check ===" -ForegroundColor Yellow

try {
    Write-Host "`n1. Current project:"
    $project = oc project 2>&1
    Write-Host $project
    
    Write-Host "`n2. All resources:"
    oc get all 2>&1
    
    Write-Host "`n3. Pods status:"
    oc get pods 2>&1
    
    Write-Host "`n4. Events (last 10):"
    oc get events --sort-by=.metadata.creationTimestamp 2>&1 | Select-Object -Last 10
    
    Write-Host "`n5. ConfigMap ML settings:"
    $enablePytorch = oc get configmap backend-config -o jsonpath='{.data.ENABLE_PYTORCH}' 2>&1
    $runtimeInstall = oc get configmap backend-config -o jsonpath='{.data.RUNTIME_INSTALL_PYTORCH}' 2>&1
    Write-Host "ENABLE_PYTORCH: $enablePytorch"
    Write-Host "RUNTIME_INSTALL_PYTORCH: $runtimeInstall"
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Status Check Complete ===" -ForegroundColor Yellow
