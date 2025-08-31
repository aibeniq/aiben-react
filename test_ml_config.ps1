#!/usr/bin/env powershell
# Test ML Configuration Script

Write-Host "=== ML Configuration Test ===" -ForegroundColor Yellow

Write-Host "`n1. ConfigMap Values:" -ForegroundColor Cyan
try {
    $enablePytorch = oc get configmap backend-config -o jsonpath='{.data.ENABLE_PYTORCH}' 2>$null
    $runtimeInstall = oc get configmap backend-config -o jsonpath='{.data.RUNTIME_INSTALL_PYTORCH}' 2>$null
    
    Write-Host "   ENABLE_PYTORCH: $enablePytorch" -ForegroundColor Green
    Write-Host "   RUNTIME_INSTALL_PYTORCH: $runtimeInstall" -ForegroundColor Green
    
    if ($enablePytorch -eq "false" -and $runtimeInstall -eq "true") {
        Write-Host "   ✅ Correct configuration for lean build with runtime ML!" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Unexpected configuration" -ForegroundColor Red
    }
} catch {
    Write-Host "   Error checking ConfigMap: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n2. Pod Status:" -ForegroundColor Cyan
try {
    $pods = oc get pods -l component=backend --no-headers 2>$null
    if ($pods) {
        Write-Host "   $pods" -ForegroundColor Green
    } else {
        Write-Host "   No backend pods found" -ForegroundColor Red
    }
} catch {
    Write-Host "   Error checking pods: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n3. Deployment Configuration Verification:" -ForegroundColor Cyan
try {
    # Test that our kustomize build generates the right values
    Push-Location "openshift\overlays\development"
    $manifest = kustomize build . 2>$null | Out-String
    if ($manifest -match 'ENABLE_PYTORCH: "false"' -and $manifest -match 'RUNTIME_INSTALL_PYTORCH: "true"') {
        Write-Host "   ✅ Kustomize generates correct ML configuration" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Kustomize configuration may be incorrect" -ForegroundColor Red
    }
    Pop-Location
} catch {
    Write-Host "   Error checking kustomize: $($_.Exception.Message)" -ForegroundColor Red
    Pop-Location
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Yellow
