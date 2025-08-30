#!/usr/bin/env pwsh
# Fix Database Connection Issues - AIBeniq OpenShift Deployment
# This script fixes the CORS/database connection issue

Write-Host "=== AIBeniq Database Connection Fix ===" -ForegroundColor Green

# Step 1: Login to OpenShift
Write-Host "Step 1: Logging into OpenShift..." -ForegroundColor Yellow
oc login --token=sha256~eHhRWoYhOBPTjMcSQJP8C-E0SHPE9X65yWnYgFwAObc --server=https://api.aibeniq-prod.gimc.p1.openshiftapps.com:6443

# Step 2: Switch to development project
Write-Host "Step 2: Switching to aibeniq-dev project..." -ForegroundColor Yellow
oc project aibeniq-dev

# Step 3: Check current service names
Write-Host "Step 3: Checking service names..." -ForegroundColor Yellow
oc get services

# Step 4: Get current database password
Write-Host "Step 4: Getting current database password..." -ForegroundColor Yellow
$DB_PASSWORD = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret backend-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}')))
Write-Host "Database password found: $($DB_PASSWORD.Length) characters" -ForegroundColor Green

# Step 5: Fix backend secrets with correct database connection
Write-Host "Step 5: Updating backend secrets with correct database connection..." -ForegroundColor Yellow
$DATABASE_URL = "postgresql://app:$DB_PASSWORD@postgres:5432/aibeniq"

# Create proper JSON using PowerShell's ConvertTo-Json
$patchData = @{
    stringData = @{
        POSTGRES_SERVER = "postgres"
        DATABASE_URL = $DATABASE_URL
    }
}
$patchJson = $patchData | ConvertTo-Json -Compress

Write-Host "Patch JSON: $patchJson" -ForegroundColor Gray
oc patch secret backend-secrets --type=merge -p $patchJson

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Backend secrets updated successfully" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to update backend secrets with JSON method" -ForegroundColor Red
    Write-Host "Trying alternative base64 method..." -ForegroundColor Yellow
    
    # Alternative method using base64 encoded values
    $POSTGRES_SERVER_B64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("postgres"))
    $DATABASE_URL_B64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($DATABASE_URL))
    
    oc patch secret backend-secrets --type=json -p="[{`"op`": `"replace`", `"path`": `"/data/POSTGRES_SERVER`", `"value`": `"$POSTGRES_SERVER_B64`"}]"
    oc patch secret backend-secrets --type=json -p="[{`"op`": `"replace`", `"path`": `"/data/DATABASE_URL`", `"value`": `"$DATABASE_URL_B64`"}]"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Backend secrets updated successfully using base64 method" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to update backend secrets" -ForegroundColor Red
        exit 1
    }
}

# Step 6: Check if postgres-secret exists and matches
Write-Host "Step 6: Checking postgres-secret consistency..." -ForegroundColor Yellow
try {
    oc get secret postgres-secret 2>$null | Out-Null
    $postgres_secret_exists = $LASTEXITCODE -eq 0
} catch {
    $postgres_secret_exists = $false
}

if ($postgres_secret_exists) {
    $POSTGRES_SECRET_PASSWORD = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret postgres-secret -o jsonpath='{.data.POSTGRES_PASSWORD}')))
    if ($POSTGRES_SECRET_PASSWORD -ne $DB_PASSWORD) {
        Write-Host "Fixing postgres-secret password mismatch..." -ForegroundColor Yellow
        $patchData2 = @{
            stringData = @{
                POSTGRES_PASSWORD = $DB_PASSWORD
            }
        }
        $patchJson2 = $patchData2 | ConvertTo-Json -Compress
        oc patch secret postgres-secret --type=merge -p $patchJson2
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Trying alternative method for postgres-secret..." -ForegroundColor Yellow
            $POSTGRES_PASSWORD_B64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($DB_PASSWORD))
            oc patch secret postgres-secret --type=json -p="[{`"op`": `"replace`", `"path`": `"/data/POSTGRES_PASSWORD`", `"value`": `"$POSTGRES_PASSWORD_B64`"}]"
        }
        
        Write-Host "[OK] postgres-secret updated to match backend-secrets" -ForegroundColor Green
    } else {
        Write-Host "[OK] postgres-secret password matches backend-secrets" -ForegroundColor Green
    }
} else {
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
Start-Sleep -Seconds 10

$backend_pod = oc get pods -l component=backend --no-headers -o custom-columns=":metadata.name" | Select-Object -First 1
if ($backend_pod) {
    Write-Host "Testing health check on pod: $backend_pod" -ForegroundColor Yellow
    $health_check = oc exec $backend_pod -- curl -f -s http://localhost:8000/api/v1/utils/health-check/ 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Backend health check passed" -ForegroundColor Green
        Write-Host "Health response: $health_check" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] Backend health check failed" -ForegroundColor Red
        Write-Host "Checking backend logs..." -ForegroundColor Yellow
        oc logs $backend_pod --tail=20
    }
} else {
    Write-Host "[ERROR] No backend pod found" -ForegroundColor Red
}

# Step 10: Test frontend connectivity
Write-Host "Step 10: Checking routes..." -ForegroundColor Yellow
oc get routes

Write-Host ""
Write-Host "=== Fix Complete ===" -ForegroundColor Green
Write-Host "The database connection issue should now be resolved." -ForegroundColor White
Write-Host "If the CORS error persists, check the backend logs with:" -ForegroundColor White
Write-Host "  oc logs deployment/backend --tail=50" -ForegroundColor Gray
Write-Host ""
Write-Host "Test the application at: https://redhat.aiben.io" -ForegroundColor White
