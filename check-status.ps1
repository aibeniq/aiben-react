# Check deployment status after architecture fix
Write-Host "=== Deployment Status Check ===" -ForegroundColor Green

oc get pods

Write-Host "`n=== Backend Logs (last 10 lines) ===" -ForegroundColor Yellow
$backendPod = oc get pods -l component=backend --no-headers -o custom-columns=":metadata.name" | Select-Object -First 1
if ($backendPod) {
    $backendPod = $backendPod.Trim()
    Write-Host "Backend pod: $backendPod" -ForegroundColor Gray
    oc logs $backendPod --tail=10
} else {
    Write-Host "No backend pod found" -ForegroundColor Red
}

Write-Host "`n=== Secret Validation ===" -ForegroundColor Yellow
$dbUrl = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret backend-secrets -o jsonpath='{.data.DATABASE_URL}')))
$postgresServer = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret backend-secrets -o jsonpath='{.data.POSTGRES_SERVER}')))
Write-Host "DATABASE_URL: $dbUrl" -ForegroundColor Gray
Write-Host "POSTGRES_SERVER: $postgresServer" -ForegroundColor Gray

Write-Host "`n=== Health Check ===" -ForegroundColor Yellow
if ($backendPod) {
    $health = oc exec $backendPod -- curl -f -s http://localhost:8000/api/v1/utils/health-check/ 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Health check passed: $health" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Health check failed" -ForegroundColor Red
    }
}

Write-Host "`n=== Routes ===" -ForegroundColor Yellow
oc get routes
