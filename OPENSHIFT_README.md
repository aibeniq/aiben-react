# OpenShift Deployment Guide for AIBeniq

## Table of Contents

1. [Overview](#overview)
2. [Current Architecture](#current-architecture)
3. [Prerequisites](#prerequisites)
4. [Environment Configuration](#environment-configuration)
5. [Secret Management](#secret-management)
6. [Deployment Process](#deployment-process)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Operational Procedures](#operational-procedures)
9. [Common Issues & Solutions](#common-issues--solutions)

## Overview

This document consolidates all OpenShift deployment knowledge for the AIBeniq application. It replaces multiple scattered documentation files and provides the single source of truth for deployment procedures.

### Current Status

- **Cluster**: `https://api.aibeniq-prod.gimc.p1.openshiftapps.com:6443`
- **Development Namespace**: `aibeniq-dev`
- **Production Namespace**: `aibeniq-prod`
- **Registry**: OpenShift Internal Registry
- **Domain**: `aiben.io` (with `redhat.*` prefix for services)

## Current Architecture

### Services & Routes

```
Frontend:    https://redhat.aiben.io           (React/Vite app)
Backend API: https://redhat-api.aiben.io       (FastAPI)
Database:    postgres (internal)               (PostgreSQL)
Cache:       redis (internal)                  (Redis)
Admin:       https://redhat-adminer.aiben.io   (Adminer)
AI:          ollama (internal)                 (Ollama)
```

### Components

- **Frontend**: React/Vite app (Nginx container, port 8080)
- **Backend**: FastAPI app (Python, port 8000)
- **Database**: PostgreSQL with persistent storage
- **Cache**: Redis for session storage and caching
- **AI Models**: Ollama container for local LLM inference
- **Database Admin**: Adminer for database management

### Container Registry

Using OpenShift internal registry:

- **External URL**: `default-route-openshift-image-registry.apps.aibeniq-prod.gimc.p1.openshiftapps.com`
- **Internal URL**: `image-registry.openshift-image-registry.svc:5000`
- **Images**: `{namespace}/backend:latest` and `{namespace}/frontend:latest`

## Prerequisites

### Required Tools

1. **OpenShift CLI (oc)**: Latest version, logged into cluster
2. **Docker**: For local image building
3. **PowerShell**: For running deployment scripts (Windows)

### Access Requirements

- OpenShift cluster access with admin permissions
- Container registry push/pull permissions
- Target namespace access (`aibeniq-dev`, `aibeniq-prod`)

### Verification Commands

```powershell
# Check OpenShift access
oc whoami
oc get projects

# Check Docker
docker version

# Check current project
oc project
```

## Environment Configuration

### Development Environment

- **Namespace**: `aibeniq-dev`
- **Domain**: `redhat*.aiben.io`
- **Resources**: Lower CPU/memory limits
- **TLS**: HTTP-only (no TLS termination)

### Production Environment

- **Namespace**: `aibeniq-prod`
- **Domain**: `redhat*.aiben.io`
- **Resources**: Production CPU/memory limits
- **TLS**: HTTPS with proper certificates

### Key Configuration Differences

| Setting              | Development                             | Production                  |
| -------------------- | --------------------------------------- | --------------------------- |
| ENVIRONMENT          | production                              | production                  |
| BACKEND_CORS_ORIGINS | http://localhost,http://redhat.aiben.io | https://redhat.aiben.io     |
| FRONTEND_HOST        | http://redhat.aiben.io                  | https://redhat.aiben.io     |
| VITE_API_URL         | http://redhat-api.aiben.io              | https://redhat-api.aiben.io |
| TLS Termination      | None (HTTP)                             | Edge (HTTPS)                |

## Secret Management

### Consolidated Secret Architecture

#### backend-secrets (Single Source of Truth)

Contains all application secrets with computed consistency:

```yaml
SECRET_KEY: "REPLACE_ME_SECRET_KEY" # FastAPI secret key
FIRST_SUPERUSER: "admin@example.com" # Admin user email
FIRST_SUPERUSER_PASSWORD: "REPLACE_ME_SUPERUSER_PWD" # Admin password
POSTGRES_PASSWORD: "REPLACE_ME_DB_PWD" # Database password
POSTGRES_SERVER: "postgres" # Correct service name (not postgres-service)
POSTGRES_PORT: "5432"
POSTGRES_DB: "aibeniq"
POSTGRES_USER: "app"
DATABASE_URL: "postgresql://app:REPLACE_ME_DB_PWD@postgres:5432/aibeniq" # Computed consistently
OPENAI_API_KEY: "REPLACE_ME_OPENAI_KEY" # OpenAI API key
OPENAI_ADMIN_KEY: "REPLACE_ME_OPENAI_ADMIN_KEY" # OpenAI Admin API key for usage dashboard
# Optional: SMTP, AWS, Replicate, Sentry configs
```

**🚀 Architecture Improvements:**

- ✅ **Single Source of Truth**: Only `backend-secrets` contains the database password
- ✅ **No Sync Issues**: PostgreSQL references the same secret as the backend
- ✅ **Computed DATABASE_URL**: No manual string construction, eliminates typos
- ✅ **Correct Service Names**: Uses `postgres` not `postgres-service`
- ✅ **No Redundant Secrets**: Eliminated `postgres-secret` completely

### Secret Management Best Practices

1. **Never commit real secrets to Git**: Base secrets contain only placeholders
2. **Use automated management**: Use `setup-secrets.ps1` for consistent configuration
3. **Restart after updates**: Pods automatically restart when using the script
4. **No manual synchronization**: Single secret source eliminates sync problems

### Secure Secret Setup

```powershell
# Interactive setup (secure input)
.\scripts\setup-secrets.ps1 -Environment dev -Interactive

# Automatic fix with existing values
.\scripts\setup-secrets.ps1 -Environment dev

# Validate configuration
.\scripts\setup-secrets.ps1 -Environment dev -Validate

# Full setup with restart
.\scripts\setup-secrets.ps1 -Environment dev -Interactive -Restart
```

## Deployment Process

### Main Deployment Script

Use `scripts\deploy-openshift.ps1` for all deployments:

```powershell
# Quick deployment (development)
.\scripts\deploy-openshift.ps1 -Environment dev

# Full build and push (production)
.\scripts\deploy-openshift.ps1 -Environment prod -Build -Push

# Dry run to check configuration
.\scripts\deploy-openshift.ps1 -Environment dev -DryRun

# Diagnose stuck deployment
.\scripts\deploy-openshift.ps1 -Environment dev -DiagnoseOnly -DiagnoseDeployment backend

# Force cleanup stuck deployment
.\scripts\deploy-openshift.ps1 -Environment dev -ForceCleanup -DiagnoseDeployment backend
```

### Script Parameters

- `-Environment`: `dev` or `prod` (required)
- `-Build`: Build Docker images locally
- `-Push`: Push images to registry (requires -Build)
- `-NoCache`: Build without Docker cache
- `-DryRun`: Show what would be deployed
- `-SkipSecrets`: Skip automatic secret configuration
- `-DiagnoseOnly`: Run diagnostics on stuck deployments
- `-DiagnoseDeployment`: Specify deployment to diagnose (default: backend)
- `-ForceCleanup`: Force cleanup and restart stuck deployment

### Manual Deployment Steps

1. **Build Images** (if needed):

```powershell
# Frontend
docker build -t default-route-openshift-image-registry.apps.aibeniq-prod.gimc.p1.openshiftapps.com/aibeniq-dev/frontend:latest ./frontend

# Backend
docker build -t default-route-openshift-image-registry.apps.aibeniq-prod.gimc.p1.openshiftapps.com/aibeniq-dev/backend:latest ./backend
```

2. **Push Images**:

```powershell
docker push default-route-openshift-image-registry.apps.aibeniq-prod.gimc.p1.openshiftapps.com/aibeniq-dev/frontend:latest
docker push default-route-openshift-image-registry.apps.aibeniq-prod.gimc.p1.openshiftapps.com/aibeniq-dev/backend:latest
```

3. **Deploy via Kustomize**:

```powershell
# Development
cd openshift/overlays/development
kustomize build . | oc apply -f -

# Production
cd openshift/overlays/production
kustomize build . | oc apply -f -
```

### Kustomize Structure

```
openshift/
├── base/                          # Base Kubernetes manifests
│   ├── kustomization.yaml        # Base kustomization
│   ├── domain-config.yaml        # Domain configuration
│   ├── configmap.yaml            # Application config
│   ├── secrets.yaml              # Secret templates (placeholders)
│   ├── postgres.yaml             # PostgreSQL deployment
│   ├── backend.yaml              # Backend deployment
│   ├── frontend.yaml             # Frontend deployment
│   ├── adminer.yaml              # Database admin
│   └── ollama.yaml               # AI model service
└── overlays/
    ├── development/               # Dev-specific configs
    │   ├── kustomization.yaml    # Dev kustomization
    │   ├── configmap-patch.yaml  # Dev config overrides
    │   ├── backend-patch.yaml    # Dev resource limits
    │   └── secret-patch.yaml     # Dev secret overrides
    └── production/                # Prod-specific configs
        ├── kustomization.yaml    # Prod kustomization
        ├── configmap-patch.yaml  # Prod config overrides
        ├── backend-patch.yaml    # Prod resource limits
        └── secret-patch.yaml     # Prod secret overrides
```

## Troubleshooting Guide

### Common Deployment Issues

#### 1. Backend CrashLoopBackOff / Init:1/2 Status

**Symptoms**:

- Backend pod shows `Init:1/2` status for extended periods
- Logs show database authentication failures
- Error: `FATAL: password authentication failed for user "app"`

**Root Cause**: Database connection configuration issues (service name or password problems)

**Solution**:

```powershell
# ✅ RECOMMENDED: Use the consolidated secret management to fix all issues
.\scripts\setup-secrets.ps1 -Environment dev

# Validate the fix worked
.\scripts\setup-secrets.ps1 -Environment dev -Validate

# Apply fix with automatic restart
.\scripts\setup-secrets.ps1 -Environment dev -Restart

# Manual fix if setup-secrets script has issues (should not be needed now)
$POSTGRES_PWD="aibeniq-dev-$(Get-Random)"
$DATABASE_URL="postgresql://app:$POSTGRES_PWD@postgres:5432/aibeniq"
oc patch secret backend-secrets --type=json -p="[{`"op`": `"replace`", `"path`": `"/data/POSTGRES_PASSWORD`", `"value`": `"$([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($POSTGRES_PWD)))`"}, {`"op`": `"replace`", `"path`": `"/data/DATABASE_URL`", `"value`": `"$([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($DATABASE_URL)))`"}]"
oc rollout restart deployment/postgres deployment/backend

# Manual check (if needed)
oc get secret backend-secrets -o yaml | grep -A 5 -B 5 POSTGRES
```

**✅ Recent Fixes Applied:**

- Fixed JSON patch syntax errors in setup-secrets.ps1
- Added automatic placeholder detection and replacement
- Added secret verification step to confirm updates worked
- Improved error handling and fallback methods

#### 2. OpenAI API Connection Errors

**Symptoms**:

- Backend logs show `APIConnectionError` or `Illegal header value b'Bearer '`
- OpenAI-related features fail

**Root Cause**: Missing or invalid `OPENAI_API_KEY`

**Solution**:

```powershell
# Use consolidated secret management
.\scripts\setup-secrets.ps1 -Environment dev -Interactive

# Update OpenAI API key specifically
$OPENAI_KEY = "sk-your-real-openai-key"
oc patch secret backend-secrets --type=json -p="[{`"op`": `"replace`", `"path`": `"/data/OPENAI_API_KEY`", `"value`": `"$([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($OPENAI_KEY)))`"}]"

# Restart backend
oc rollout restart deployment/backend
```

#### 3. CORS Errors in Frontend

**Symptoms**:

- Browser console shows CORS errors
- Frontend cannot communicate with backend

**Root Cause**: Incorrect `VITE_API_URL` or backend CORS configuration

**Solution**:

```powershell
# Check frontend configuration
oc get configmap frontend-config -o yaml

# Check backend CORS settings
oc get configmap backend-config -o yaml

# Update if needed and restart
oc rollout restart deployment/frontend deployment/backend
```

#### 4. Service Endpoint Warnings

**Symptoms**:

- Warning: Service has no endpoints
- Pods running but not accessible

**Root Cause**: Label mismatch between service selectors and pod labels

**Solution**:

```powershell
# Check service selectors
oc get service backend -o yaml | findstr -A 5 selector

# Check pod labels
oc get pods -l component=backend --show-labels

# If mismatched, the kustomization needs fixing
```

#### 5. "Old Replicas Pending Termination" During Deployment

**Symptoms**:

- Deployment stuck with message "Waiting for deployment rollout to finish: 1 old replicas are pending termination..."
- Pods appear to be running but rollout never completes
- New pods created but old ones won't terminate

**Root Cause**:

- Graceful shutdown issues in container
- Readiness probe failures preventing rolling update
- Resource constraints preventing pod scheduling

**Automated Solution**:

```powershell
# Use built-in diagnostic mode
.\scripts\deploy-openshift.ps1 -Environment dev -DiagnoseOnly -DiagnoseDeployment backend

# Use built-in force cleanup
.\scripts\deploy-openshift.ps1 -Environment dev -ForceCleanup -DiagnoseDeployment backend
```

**Manual Solution**:

```powershell
# Step 1: Diagnose the issue
oc get pods -l component=backend
oc get rs -l component=backend
oc get events --sort-by=.metadata.creationTimestamp | Select-String "backend" -Context 1

# Step 2: Force cleanup if stuck
oc scale deployment/backend --replicas=0
Start-Sleep -Seconds 15
oc delete pods -l component=backend --force --grace-period=0
oc delete rs -l component=backend --field-selector='status.replicas==0'

# Step 3: Scale back up
oc scale deployment/backend --replicas=1
oc rollout status deployment/backend --timeout=300s
```

**Prevention**:

- Ensure proper `STOPSIGNAL SIGTERM` in Dockerfile
- Implement graceful shutdown in FastAPI application
- Use single worker configuration: `--workers 1`
- Set appropriate graceful shutdown timeout: `--timeout-graceful-shutdown 30`

### Diagnostic Commands

```powershell
# Overall status
oc get all

# Pod status and events
oc get pods
oc describe pod <pod-name>
oc get events --sort-by=.metadata.creationTimestamp

# Service endpoints
oc get endpoints

# Configuration inspection
oc get configmap backend-config -o yaml
oc get secret backend-secrets -o yaml

# Logs
oc logs deployment/backend --tail=50
oc logs deployment/frontend --tail=50
oc logs deployment/postgres --tail=50

# Test connectivity
oc exec deployment/backend -- curl -f http://localhost:8000/api/v1/utils/health-check/

# Enhanced troubleshooting (built into deployment script)
.\scripts\deploy-openshift.ps1 -Environment dev -DiagnoseOnly -DiagnoseDeployment backend
.\scripts\deploy-openshift.ps1 -Environment dev -ForceCleanup -DiagnoseDeployment backend
```

## Operational Procedures

### Cost Management

#### Pause Deployment (Overnight)

```powershell
# Pause all workloads to save costs (includes cleanup)
.\scripts\pause-cluster.ps1 -Action pause -Namespace aibeniq-dev -Force

# Resume when needed (automatically applies environment-specific config)
.\scripts\pause-cluster.ps1 -Action resume -Namespace aibeniq-dev

# Check status
.\scripts\pause-cluster.ps1 -Action status -Namespace aibeniq-dev
```

**🚀 Enhanced Resume Features:**

- ✅ **Environment-Aware**: Automatically detects dev/prod from namespace
- ✅ **Config Restoration**: Applies proper HTTP/HTTPS settings after resume
- ✅ **Integration**: Uses deployment script for consistent configuration
- ✅ **Fallback**: Manual config patches if deployment script unavailable

#### Cleanup Orphaned Resources

```powershell
# Run cleanup only (without pausing)
.\scripts\pause-cluster.ps1 -Action cleanup -Namespace aibeniq-dev

# Or manually:
oc delete pods --field-selector=status.phase=Failed
oc delete pods --field-selector=status.phase=Succeeded
oc delete builds --field-selector=status.phase=Complete
oc delete builds --field-selector=status.phase=Failed
```

### Scaling Operations

```powershell
# Scale deployments
oc scale deployment/backend --replicas=2
oc scale deployment/frontend --replicas=3

# Check autoscaling
oc get hpa
```

### Updates and Rollbacks

```powershell
# Check rollout status
oc rollout status deployment/backend

# View rollout history
oc rollout history deployment/backend

# Rollback if needed
oc rollout undo deployment/backend
```

## Common Issues & Solutions

### Database Issues

**Issue**: PostgreSQL pod fails to start

```powershell
# Check persistent volume
oc get pvc
oc describe pvc postgres-storage

# Check pod events
oc describe pod -l component=database
```

**Issue**: Database connection timeouts

```powershell
# Check database service
oc get service postgres
oc describe service postgres

# Test internal connectivity
oc exec deployment/backend -- nc -zv postgres 5432
```

**Issue**: PostgreSQL Password Mismatch (Critical)

**Symptoms**:

- Backend shows authentication failures: `FATAL: password authentication failed for user "app"`
- Login fails consistently despite secret updates
- Backend pod crashes with database connection errors

**Root Cause**: PostgreSQL only uses `POSTGRES_PASSWORD` during initial database creation. Updating the secret doesn't change the running database's password.

**Detection**:

```powershell
# Quick detection with enhanced setup-secrets
.\scripts\setup-secrets.ps1 -Environment dev -Validate

# Manual password test
$SECRET_PWD = oc get secret backend-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}' | ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }
oc exec deploy/postgres -- bash -c "PGPASSWORD='$SECRET_PWD' psql -U app -d aibeniq -h postgres -c '\dt'"
```

**Resolution Options**:

**Option 1: Automatic Password Rotation** (Recommended)

```powershell
# Attempts to update database password to match secret
.\scripts\setup-secrets.ps1 -Environment dev -ForcePasswordRotate
```

**Option 2: Destructive Reset** (Data Loss Warning)

```powershell
# Deletes database and recreates with current secret
.\scripts\setup-secrets.ps1 -Environment dev -DestructiveReset
.\scripts\deploy-openshift.ps1 -Environment dev
```

**Option 3: Manual Database Password Update**

```powershell
# Get current secret password
$NEW_PWD = oc get secret backend-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}' | ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }

# Update database password (requires knowing current password)
oc exec deploy/postgres -- bash -c "PGPASSWORD='OLD_PASSWORD' psql -U app -d aibeniq -h postgres -c \"ALTER USER app PASSWORD '$NEW_PWD';\""
```

**Prevention**:

- Always use `.\scripts\setup-secrets.ps1` for password management
- Run with `-Validate` to detect mismatches before deployment
- Use `-ForcePasswordRotate` during updates to maintain consistency

**Architecture Notes**:

- PostgreSQL initialization behavior: `POSTGRES_PASSWORD` only used during first startup
- Runtime password changes require `ALTER USER` commands or database re-initialization
- Enhanced scripts now detect and resolve password mismatches automatically

### Redis Issues

**Issue**: Redis connection failures / Backend CrashLoopBackOff due to Redis

```powershell
# Check Redis pod status
oc get pods -l component=redis

# Check Redis logs
oc logs deployment/redis --tail=20

# Test Redis connectivity
oc exec deployment/backend -- redis-cli -h redis -p 6379 ping

# Check Redis service
oc get service redis
oc describe service redis
```

**Issue**: Redis pod fails to start

```powershell
# Check persistent volume
oc get pvc redis-storage
oc describe pvc redis-storage

# Check pod events
oc describe pod -l component=redis

# Check resource limits
oc describe deployment redis | findstr -A 10 -B 5 "Limits\|Requests"
```

### Frontend Issues

**Issue**: Frontend shows blank page

```powershell
# Check frontend logs
oc logs deployment/frontend

# Check Nginx configuration
oc exec deployment/frontend -- cat /etc/nginx/nginx.conf

# Test frontend service
curl -I http://redhat.aiben.io
```

**Issue**: API calls fail from frontend

```powershell
# Check API URL configuration
oc exec deployment/frontend -- grep -r "redhat-api" /usr/share/nginx/html/

# Verify CORS configuration
oc get configmap backend-config -o yaml | findstr CORS
```

### Image Issues

**Issue**: ImagePullBackOff errors

```powershell
# Check image streams
oc get imagestream

# Check registry authentication
oc registry login

# Verify image exists
oc describe pod <pod-name> | findstr -A 10 "Events"
```

### Performance Issues

**Issue**: Pods running out of memory

```powershell
# Check resource usage
oc top pods

# Check resource limits
oc describe deployment backend | findstr -A 10 -B 5 "Limits\|Requests"

# Update resource limits if needed
oc patch deployment backend -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","resources":{"limits":{"memory":"1Gi"}}}]}}}}'
```

### SSL/TLS Issues

**Issue**: Certificate problems with HTTPS

```powershell
# Check route configuration
oc get route frontend-dashboard -o yaml

# Test SSL
curl -I https://redhat.aiben.io

# For development, disable TLS
oc patch route frontend-dashboard -p '{"spec":{"tls":null}}'
```

## Development vs Production Differences

### Resource Allocation

```yaml
# Development (lower resources)
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 250m
    memory: 512Mi

# Production (higher resources)
resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 2Gi
```

### Environment Variables

```yaml
# Development
ENVIRONMENT: "production"  # Note: Still "production" for compatibility
DEBUG: "true"
LOG_LEVEL: "DEBUG"

# Production
ENVIRONMENT: "production"
DEBUG: "false"
LOG_LEVEL: "INFO"
```

### Security Settings

```yaml
# Development
- No TLS termination (HTTP only)
- Relaxed CORS origins
- Debug logging enabled

# Production
- TLS termination at route level
- Strict CORS origins
- Production logging levels
```

---

## Summary

This guide replaces all scattered OpenShift documentation and provides the complete deployment reference. For any issues not covered here, follow this troubleshooting order:

1. Check pod status: `oc get pods`
2. Check events: `oc get events --sort-by=.metadata.creationTimestamp`
3. Check logs: `oc logs deployment/[service] --tail=50`
4. Check configuration: `oc get configmap [name] -o yaml`
5. Check secrets: `oc get secret [name] -o yaml`
6. Restart if needed: `oc rollout restart deployment/[service]`

## Quick Troubleshooting Reference

### 🚨 Emergency Commands

```powershell
# Stuck deployment - diagnose
.\scripts\deploy-openshift.ps1 -Environment dev -DiagnoseOnly

# Stuck deployment - force fix
.\scripts\deploy-openshift.ps1 -Environment dev -ForceCleanup

# Complete reset
oc delete pods --all --force --grace-period=0
.\scripts\deploy-openshift.ps1 -Environment dev
```

### 🔍 Common Issues

| Issue                              | Quick Fix                                                       |
| ---------------------------------- | --------------------------------------------------------------- |
| "Old replicas pending termination" | `.\scripts\deploy-openshift.ps1 -Environment dev -ForceCleanup` |
| Backend CrashLoopBackOff           | Check postgres password match, restart both                     |
| OpenAI API errors                  | Update `OPENAI_API_KEY` secret, restart backend                 |
| CORS errors                        | Check `VITE_API_URL` and `BACKEND_CORS_ORIGINS`                 |
| ImagePullBackOff                   | `oc registry login` and rebuild images                          |

### 🛠 Standard Fixes

```powershell
# Secret update pattern
oc patch secret backend-secrets -p '{"stringData":{"KEY":"value"}}'
oc rollout restart deployment/backend

# Force pod cleanup
oc delete pods -l component=backend --force --grace-period=0

# Reset deployment
oc scale deployment/backend --replicas=0; Start-Sleep 10; oc scale deployment/backend --replicas=1
```

For emergency support, use the pause/cleanup scripts to stop costs and reset the environment if needed.
