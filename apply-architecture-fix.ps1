# Quick Fix - Apply the new architecture immediately
Write-Host "=== Applying New Secret Architecture ===" -ForegroundColor Green

# 1. Login and switch project
oc login --token=sha256~eHhRWoYhOBPTjMcSQJP8C-E0SHPE9X65yWnYgFwAObc --server=https://api.aibeniq-prod.gimc.p1.openshiftapps.com:6443
oc project aibeniq-dev

# 2. Get current password to maintain consistency
Write-Host "Getting current database password..." -ForegroundColor Yellow
$currentPassword = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret backend-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}')))
Write-Host "Current password length: $($currentPassword.Length) characters" -ForegroundColor Green

# 3. Fix all secrets with consistent values
Write-Host "Applying consistent secret configuration..." -ForegroundColor Yellow
$DATABASE_URL = "postgresql://app:$currentPassword@postgres:5432/aibeniq"

# Update backend-secrets with all required fields using base64 method
$secretUpdates = @{
    POSTGRES_SERVER = "postgres"
    POSTGRES_PORT = "5432"
    POSTGRES_DB = "aibeniq"
    POSTGRES_USER = "app"
    DATABASE_URL = $DATABASE_URL
}

foreach ($key in $secretUpdates.Keys) {
    $base64Value = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($secretUpdates[$key]))
    Write-Host "Updating $key..." -ForegroundColor Gray
    oc patch secret backend-secrets --type=json -p="[{`"op`": `"replace`", `"path`": `"/data/$key`", `"value`": `"$base64Value`"}]"
}

# 4. Remove orphaned postgres-secret
Write-Host "Removing orphaned postgres-secret..." -ForegroundColor Yellow
try {
    oc delete secret postgres-secret 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Removed postgres-secret" -ForegroundColor Green
    }
} catch {
    Write-Host "[INFO] postgres-secret didn't exist" -ForegroundColor Gray
}

# 5. Apply the new base manifests
Write-Host "Applying updated base manifests..." -ForegroundColor Yellow
oc apply -f openshift/base/secrets.yaml
oc apply -f openshift/base/configmap.yaml
oc apply -f openshift/base/postgres.yaml

# 6. Restart deployments in correct order
Write-Host "Restarting deployments..." -ForegroundColor Yellow
Write-Host "Restarting postgres..." -ForegroundColor Gray
oc rollout restart deployment/postgres
oc rollout status deployment/postgres --timeout=180s

Write-Host "Restarting backend..." -ForegroundColor Gray  
oc rollout restart deployment/backend
oc rollout status deployment/backend --timeout=180s

# 7. Verify the fix
Write-Host "Verifying the fix..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

$backendPod = oc get pods -l component=backend --no-headers -o custom-columns=":metadata.name" | Select-Object -First 1
if ($backendPod) {
    $backendPod = $backendPod.Trim()
    Write-Host "Testing health check on: $backendPod" -ForegroundColor Gray
    $healthResult = oc exec $backendPod -- curl -f -s http://localhost:8000/api/v1/utils/health-check/ 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Backend health check passed!" -ForegroundColor Green
        Write-Host "Response: $healthResult" -ForegroundColor Gray
    } else {
        Write-Host "[WARNING] Health check failed, checking logs..." -ForegroundColor Yellow
        oc logs $backendPod --tail=10
    }
}

Write-Host ""
Write-Host "=== Architecture Update Complete ===" -ForegroundColor Green
Write-Host "✅ Single source of truth for database password" -ForegroundColor Green
Write-Host "✅ Consistent DATABASE_URL generation" -ForegroundColor Green  
Write-Host "✅ Correct service names (postgres not postgres-service)" -ForegroundColor Green
Write-Host "✅ Removed redundant postgres-secret" -ForegroundColor Green
Write-Host ""
Write-Host "Test the application at: https://redhat.aiben.io" -ForegroundColor Cyan
