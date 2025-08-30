# Quick fix for database connection issue
Write-Host "Logging into OpenShift..." -ForegroundColor Green
oc login --token=sha256~eHhRWoYhOBPTjMcSQJP8C-E0SHPE9X65yWnYgFwAObc --server=https://api.aibeniq-prod.gimc.p1.openshiftapps.com:6443

Write-Host "Switching to aibeniq-dev project..." -ForegroundColor Green  
oc project aibeniq-dev

Write-Host "Fixing database connection secrets..." -ForegroundColor Green
# Fix the service name from postgres-service to postgres
oc patch secret backend-secrets --type='merge' -p='{"stringData":{"POSTGRES_SERVER":"postgres"}}'

# Fix the DATABASE_URL to use correct service name
$currentPassword = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret backend-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}')))
$correctDatabaseUrl = "postgresql://app:$currentPassword@postgres:5432/aibeniq"
oc patch secret backend-secrets --type='merge' -p="{`"stringData`":{`"DATABASE_URL`":`"$correctDatabaseUrl`"}}"

Write-Host "Restarting backend deployment..." -ForegroundColor Green
oc rollout restart deployment/backend

Write-Host "Waiting for backend to be ready..." -ForegroundColor Green
oc rollout status deployment/backend --timeout=180s

Write-Host "Checking pod status..." -ForegroundColor Green
oc get pods -l component=backend

Write-Host "Done! Check the application at https://redhat.aiben.io" -ForegroundColor Green
