# Clean Deployment Restart Script
# Run this after logging into OpenShift with: oc login

# 1. Clean up old/stale pods and deployments
Write-Host "[INFO] Cleaning up old pods and deployments..." -ForegroundColor Cyan

# Delete all pods to force recreation
oc delete pods --all -n aibeniq-prod --ignore-not-found

# Delete old build pods specifically  
oc delete pods -l openshift.io/build.name -n aibeniq-prod --ignore-not-found

# Clean up failed jobs
oc delete jobs -l job-name=backend-prestart -n aibeniq-prod --ignore-not-found

# 2. Apply secure overlay patches (placeholders only)
Write-Host "[INFO] Applying secure overlay patches..." -ForegroundColor Cyan
cd openshift/overlays/production
kustomize build . | oc apply -f -
cd ..\..\..

# 3. Apply secure secrets interactively
Write-Host "[INFO] Applying secure secrets..." -ForegroundColor Cyan
./scripts/apply-secrets-secure.ps1 -Interactive -Restart

# 4. Use deploy script for fresh deployment
Write-Host "[INFO] Running fresh deployment..." -ForegroundColor Cyan
./scripts/deploy-openshift.ps1 -Environment prod -Internal

# 5. Verify deployment
Write-Host "[INFO] Verifying deployment..." -ForegroundColor Cyan
oc get pods
oc get routes

Write-Host "[SUCCESS] Clean deployment restart completed!" -ForegroundColor Green
