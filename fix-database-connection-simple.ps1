#!/usr/bin/env pwsh
# Simplified Database Connection Fix - AIBeniq OpenShift Deployment
# This script fixes the CORS/database connection issue using reliable methods

Write-Host "=== AIBeniq Database Connection Fix (Simplified) ===" -ForegroundColor Green

# Step 1: Login to OpenShift
Write-Host "Step 1: Logging into OpenShift..." -ForegroundColor Yellow
oc login --token=sha256~eHhRWoYhOBPTjMcSQJP8C-E0SHPE9X65yWnYgFwAObc --server=https://api.aibeniq-prod.gimc.p1.openshiftapps.com:6443

# Step 2: Switch to development project
Write-Host "Step 2: Switching to aibeniq-dev project..." -ForegroundColor Yellow
oc project aibeniq-dev

# Step 3: Get current database password
Write-Host "Step 3: Getting current database password..." -ForegroundColor Yellow
$DB_PASSWORD = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret backend-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}')))
Write-Host "Database password found: $($DB_PASSWORD.Length) characters" -ForegroundColor Green

# Step 4: Fix backend secrets using base64 method (most reliable)
Write-Host "Step 4: Updating backend secrets with correct database connection..." -ForegroundColor Yellow
$DATABASE_URL = "postgresql://app:$DB_PASSWORD@postgres:5432/aibeniq"

# Use base64 encoded values (most reliable method for OpenShift)
$POSTGRES_SERVER_B64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("postgres"))
$DATABASE_URL_B64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($DATABASE_URL))

Write-Host "Patching POSTGRES_SERVER..." -ForegroundColor Gray
oc patch secret backend-secrets --type=json -p="[{`"op`": `"replace`", `"path`": `"/data/POSTGRES_SERVER`", `"value`": `"$POSTGRES_SERVER_B64`"}]"

Write-Host "Patching DATABASE_URL..." -ForegroundColor Gray
oc patch secret backend-secrets --type=json -p="[{`"op`": `"replace`", `"path`": `"/data/DATABASE_URL`", `"value`": `"$DATABASE_URL_B64`"}]"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Backend secrets updated successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to update backend secrets" -ForegroundColor Red
    exit 1
}

# Step 5: Verify the secret updates
Write-Host "Step 5: Verifying secret updates..." -ForegroundColor Yellow
$NEW_POSTGRES_SERVER = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret backend-secrets -o jsonpath='{.data.POSTGRES_SERVER}')))
$NEW_DATABASE_URL = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret backend-secrets -o jsonpath='{.data.DATABASE_URL}')))

Write-Host "POSTGRES_SERVER: $NEW_POSTGRES_SERVER" -ForegroundColor Gray
Write-Host "DATABASE_URL: $NEW_DATABASE_URL" -ForegroundColor Gray

if ($NEW_POSTGRES_SERVER -eq "postgres" -and $NEW_DATABASE_URL.Contains("@postgres:5432")) {
    Write-Host "[OK] Secret updates verified successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Secret updates verification failed" -ForegroundColor Red
    exit 1
}

# Step 6: Check postgres-secret exists
Write-Host "Step 6: Checking postgres-secret..." -ForegroundColor Yellow
try {
    $null = oc get secret postgres-secret 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] postgres-secret exists" -ForegroundColor Green
    } else {
        Write-Host "Creating postgres-secret..." -ForegroundColor Yellow
        oc create secret generic postgres-secret --from-literal=POSTGRES_PASSWORD="$DB_PASSWORD"
        Write-Host "[OK] postgres-secret created" -ForegroundColor Green
    }
} catch {
    Write-Host "Creating postgres-secret..." -ForegroundColor Yellow
    oc create secret generic postgres-secret --from-literal=POSTGRES_PASSWORD="$DB_PASSWORD"
    Write-Host "[OK] postgres-secret created" -ForegroundColor Green
}

# Step 7: Restart backend deployment
Write-Host "Step 7: Restarting backend deployment..." -ForegroundColor Yellow
oc rollout restart deployment/backend

# Step 8: Wait for deployment to complete
Write-Host "Step 8: Waiting for backend deployment to complete..." -ForegroundColor Yellow
oc rollout status deployment/backend --timeout=300s

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Backend deployment completed successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Backend deployment failed or timed out" -ForegroundColor Red
    Write-Host "Checking deployment status..." -ForegroundColor Yellow
    oc get pods -l component=backend
    oc describe deployment/backend
}

# Step 9: Test backend health
Write-Host "Step 9: Testing backend health..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

$backend_pod = oc get pods -l component=backend --no-headers -o custom-columns=":metadata.name" | Where-Object {$_ -and $_.Trim() -ne ""} | Select-Object -First 1
if ($backend_pod) {
    $backend_pod = $backend_pod.Trim()
    Write-Host "Testing health check on pod: $backend_pod" -ForegroundColor Yellow
    try {
        $health_check = oc exec $backend_pod -- curl -f -s http://localhost:8000/api/v1/utils/health-check/ 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Backend health check passed" -ForegroundColor Green
            Write-Host "Health response: $health_check" -ForegroundColor Gray
        } else {
            Write-Host "[WARNING] Backend health check failed, checking logs..." -ForegroundColor Yellow
            oc logs $backend_pod --tail=10
        }
    } catch {
        Write-Host "[WARNING] Could not execute health check, checking logs..." -ForegroundColor Yellow
        oc logs $backend_pod --tail=10
    }
} else {
    Write-Host "[WARNING] No backend pod found, checking all pods..." -ForegroundColor Yellow
    oc get pods
}

# Step 10: Final status
Write-Host ""
Write-Host "=== Fix Complete ===" -ForegroundColor Green
Write-Host "The database connection issue should now be resolved." -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Test the application at: https://redhat.aiben.io" -ForegroundColor Gray
Write-Host "2. Try logging in to verify CORS is fixed" -ForegroundColor Gray
Write-Host "3. If issues persist, check logs with: oc logs deployment/backend --tail=50" -ForegroundColor Gray
Write-Host ""
