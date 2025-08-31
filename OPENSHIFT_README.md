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

Use `scripts\deploy-openshift.ps1` for all deployments with Docker size optimization support:

```powershell
# Quick deployment (development with auto build type)
.\scripts\deploy-openshift.ps1 -Environment dev

# Production lean deployment (recommended - ~500MB-1GB) with memory optimization
.\scripts\deploy-openshift.ps1 -Environment prod -Build -Push -BackendBuild lean

# Production with runtime ML support (lean + on-demand ML) with memory optimization
.\scripts\deploy-openshift.ps1 -Environment prod -Build -Push -BackendBuild lean -EnableRuntimeML

# Development with full ML capabilities (~2-3GB) with memory optimization
.\scripts\deploy-openshift.ps1 -Environment dev -Build -Push -BackendBuild full

# Auto build type (lean for prod, full for dev)
.\scripts\deploy-openshift.ps1 -Environment prod -Build -Push

# Dry run to check configuration
.\scripts\deploy-openshift.ps1 -Environment dev -DryRun

# Diagnose stuck deployment
.\scripts\deploy-openshift.ps1 -Environment dev -DiagnoseOnly -DiagnoseDeployment backend

# Force cleanup stuck deployment
.\scripts\deploy-openshift.ps1 -Environment dev -ForceCleanup -DiagnoseDeployment backend
```

### Docker Size Optimization Options

The deployment script now supports **three backend build types** to optimize Docker image size:

#### 1. Lean Build (Recommended for Production)

- **Size**: ~500MB-1GB (90% reduction from original 11.3GB)
- **Usage**: `-BackendBuild lean`
- **Features**: OpenAI, AWS Bedrock, Ollama
- **Limitation**: No HuggingFace models by default
- **Best for**: Production deployments, OpenAI-only usage

#### 2. Lean + Runtime ML

- **Size**: ~500MB-1GB base + on-demand ML installation
- **Usage**: `-BackendBuild lean -EnableRuntimeML`
- **Features**: All providers (ML installed on first use)
- **Trade-off**: First ML operation has 30-60 second installation delay
- **Best for**: Occasional HuggingFace usage with minimal image size

#### 3. Full Build

- **Size**: ~2-3GB (70% reduction from original)
- **Usage**: `-BackendBuild full`
- **Features**: All ML capabilities pre-installed
- **Best for**: Heavy HuggingFace model usage, development

#### 4. Auto Build (Default)

- **Usage**: No `-BackendBuild` parameter
- **Logic**:
  - Production environment → lean build
  - Development environment → full build
- **Best for**: Most use cases

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

**New Docker Size Optimization Parameters:**

- `-BackendBuild`: Choose build type (`lean`|`full`|`auto`) [default: auto]
- `-EnableRuntimeML`: Enable runtime ML installation (use with `-BackendBuild lean`)

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

#### 0. Docker Image Push Timeouts / Large Image Size Issues

**Symptoms**:

- Docker push commands timeout or fail
- Backend image size is extremely large (>10GB)
- OpenShift deployment takes very long time
- Out of storage space errors

**Root Cause**: PyTorch+CUDA libraries add ~6GB to Docker image

**Solution**: Use the new lean build system

```powershell
# ✅ RECOMMENDED: Use lean build for production
.\scripts\deploy-openshift.ps1 -Environment prod -Build -Push -BackendBuild lean

# For development with ML capabilities
.\scripts\deploy-openshift.ps1 -Environment dev -Build -Push -BackendBuild full

# Lean build with on-demand ML installation
.\scripts\deploy-openshift.ps1 -Environment prod -Build -Push -BackendBuild lean -EnableRuntimeML
```

**Size Comparison**:

- Original: 11.3GB
- Lean build: ~500MB-1GB (90% reduction)
- Full build: ~2-3GB (70% reduction)

**Available Build Types**:

- `lean`: OpenAI, AWS, Ollama only (~500MB-1GB)
- `full`: All ML capabilities pre-installed (~2-3GB)
- `auto`: Lean for prod, full for dev (default)

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

#### 6. HuggingFace Model Loading Issues

**Symptoms**:

- Backend logs show `PermissionError: [Errno 13] Permission denied: '/app/.cache/huggingface/'`
- HuggingFace model downloads fail with cache directory errors
- 404 errors for `sentence-transformers/all-MiniLM-L6-v2` (incorrect model name format)
- Backend returns 500 errors when using embedding models

**Root Cause**:

- **OpenShift Security Conflict**: OpenShift assigns random UIDs that don't match Dockerfile's `appuser`
- **Permission Mismatch**: Even though Dockerfile creates `/app/.cache/` with proper permissions, OpenShift's random UID can't write to it
- **Incorrect Model Naming**: Should be `all-MiniLM-L6-v2`, not `sentence-transformers/all-MiniLM-L6-v2`

**✅ Comprehensive Fix Applied**:

**1. Updated Dockerfile** ([`backend/Dockerfile`](backend/Dockerfile)) now uses a simplified, robust pattern:

```dockerfile
# Create writable cache (model files are non-sensitive) for arbitrary OpenShift UID
RUN mkdir -p /app/.cache/huggingface /app/.cache/transformers \
  && chmod -R 0777 /app/.cache

# Runtime entrypoint validates writability and can fall back to /tmp if needed
COPY docker/entrypoint-hf.sh /entrypoint-hf.sh
ENTRYPOINT ["/entrypoint-hf.sh"]
```

Key improvements:

- 0777 permissions avoid reliance on fsGroup for image-layer dirs
- Lightweight entrypoint (`entrypoint-hf.sh`) auto-falls back to `/tmp/huggingface-cache` if primary path not writable
- Eliminated redundant chown/chgrp layers and multiple tmp dirs
- Healthcheck retained (`/ready`) ensuring readiness gating

**2. Updated OpenShift Deployment** ([`backend.yaml`](openshift/base/backend.yaml)):

```yaml
securityContext:
  runAsNonRoot: true
  # Use fsGroup: 0 (root group) to match Dockerfile's group permissions
  fsGroup: 0
```

**3. Removed Conflicting Environment Variables**:

- Dockerfile sets `HF_HOME=/app/.cache/huggingface`
- OpenShift deployment no longer overrides this
- Both configurations now work together instead of conflicting

**Manual Verification**:

```powershell
# Test HuggingFace model loading with Docker's cache configuration
oc exec deployment/backend -- python -c "
import os
print('HF_HOME:', os.environ.get('HF_HOME'))
print('TRANSFORMERS_CACHE:', os.environ.get('TRANSFORMERS_CACHE'))
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('✅ Model loaded successfully with cache:', model.cache_folder)
"

# Check that cache directories exist and are writable
oc exec deployment/backend -- ls -la /app/.cache/
oc exec deployment/backend -- touch /app/.cache/test_write
```

**Alternative: Switch to OpenAI Embeddings** (Recommended for Production):

```powershell
# Update to use OpenAI embeddings (no local model downloads required)
oc patch configmap backend-config -p '{"data":{"FORCE_DEFAULT_EMBEDDING":"text-embedding-3-small"}}'
oc rollout restart deployment/backend
```

**Prevention & Hardening**:

- ✅ Writable cache independent of assigned UID/GID
- ✅ Automatic `/tmp` fallback if primary path blocked
- ✅ Minimal permissions scope (only cache dirs relaxed)
- ✅ Avoids stale partial downloads (entrypoint test writes)
- ✅ Configurable via `HF_HOME`, `TRANSFORMERS_CACHE`, and fallback `HF_FALLBACK`

**Optional Preload Optimization**:

You can warm the embedding cache at pod startup:

1. Set in `backend-config` ConfigMap:

```yaml
PRELOAD_EMBEDDING_MODEL: all-MiniLM-L6-v2
PRELOAD_EMBEDDING_PROVIDER: huggingface # huggingface|openai|ollama|replicate|aws
```

2. Redeploy / restart backend.
3. Logs will show: `Preloading embedding model 'all-MiniLM-L6-v2'...`.

If preload fails it logs a warning but does not block readiness.

#### 7. ML Features Not Available in Lean Deployment

**Symptoms**:

- Backend logs show "ML capabilities not available" warnings
- HuggingFace embedding models return 503 errors
- Only OpenAI, AWS, and Ollama models work

**Root Cause**: Using lean build (`-BackendBuild lean`) without runtime ML installation

**This is Expected Behavior**: Lean builds exclude PyTorch to achieve 90% size reduction

**Solutions**:

**Option A: Enable Runtime ML Installation**

```powershell
# Redeploy with runtime ML support
.\scripts\deploy-openshift.ps1 -Environment prod -Build -Push -BackendBuild lean -EnableRuntimeML
```

**Option B: Use Full Build**

```powershell
# Switch to full build with pre-installed ML
.\scripts\deploy-openshift.ps1 -Environment prod -Build -Push -BackendBuild full
```

**Option C: Use OpenAI/AWS Alternatives (Recommended)**

- Configure OpenAI API key for embeddings
- Use AWS Bedrock for embeddings
- Use Ollama for local models (no PyTorch dependency)

**Verify ML Configuration**:

```powershell
# Check ML environment settings
oc get configmap backend-config -o yaml | findstr PYTORCH

# Check backend logs for ML capability status
oc logs deployment/backend | findstr -i "ML\|pytorch\|huggingface"
```

#### 8. Runtime ML Installation Failures

**Symptoms**:

- First HuggingFace operation takes very long or fails
- Backend logs show "Failed to install PyTorch" errors
- Error: `/app/.venv/bin/python: No module named pip`
- Runtime installation hangs or times out
- **Backend pod restarts frequently (RestartCount > 0)**
- **OOMKilled events in `oc get events`**

**Root Cause**:

- `pip` module not available in `uv`-based virtual environments
- Permission issues with cache directories in OpenShift
- Using `uv add` instead of `uv pip install` causes lockfile conflicts
- **NEW: Memory pressure during ML installation causing OOMKilled**

**✅ CRITICAL FIX: Increased Memory Limits**

As of August 2025, all environments now include memory-optimized resource limits:

```yaml
# Backend resource limits (applied automatically via memory patches)
resources:
  requests:
    memory: "10Gi" # Increased from 6Gi to 10Gi
    cpu: "1000m"
  limits:
    memory: "12Gi" # Increased from 8Gi to 12Gi to handle ML installations
    cpu: "2000m" # Increased for faster installation
```

**Memory-Aware Installation Logic**: ML installation functions now monitor available memory and warn when memory is low (<3GB available).

**Solutions**:

**Check for OOMKilled Events**:

```powershell
# Check for memory-related restarts
oc get events --sort-by=.metadata.creationTimestamp | Select-String "OOMKilled"

# Check current pod memory usage
oc top pods

# Monitor memory during installation
oc logs deployment/backend -f | Select-String -i "memory|install|pytorch"
```

**Verify Memory Configuration**:

```powershell
# Check if memory patches are applied
oc describe deployment backend | Select-String -A 10 -B 5 "Limits|Requests"

# Should show: memory: 12Gi limit, 10Gi request
```

**Check Container Permissions**:

```powershell
# Verify container can write to filesystem
oc exec deployment/backend -- touch /tmp/test_write
oc exec deployment/backend -- ls -la /tmp/test_write

# Check if pip is available
oc exec deployment/backend -- /app/.venv/bin/python -m pip --version

# Check if writable cache directories exist
oc exec deployment/backend -- ls -la /tmp/ | findstr cache
```

**Check Network Connectivity**:

```powershell
# Test PyPI connectivity
oc exec deployment/backend -- curl -I https://pypi.org/
```

**Use Full Build Instead**:

```powershell
# Switch to pre-installed ML capabilities
.\scripts\deploy-openshift.ps1 -Environment prod -Build -Push -BackendBuild full
```

**Fix Lean Build (if pip is missing)**:

```powershell
# Both Dockerfile and Dockerfile.lean need the pip installation fix
# This should already be included in the latest version:
# RUN uv pip install pip
# RUN mkdir -p /tmp/uv-cache /tmp/pip-cache && chmod 777 /tmp/uv-cache /tmp/pip-cache

# Rebuild and deploy with the fixes
.\scripts\deploy-openshift.ps1 -Environment dev -Build -Push -BackendBuild lean -EnableRuntimeML
```

**Manual Runtime Installation Debug**:

```powershell
# Check installation logs in real-time
oc logs deployment/backend -f

# Test PyTorch installation manually
oc exec deployment/backend -- python -c "
import sys
sys.path.append('/app')
from app.core.ml_imports import ensure_pytorch
print('Testing PyTorch installation...')
result = ensure_pytorch()
print(f'Installation result: {result}')
"
```

**Recent Fixes Applied (August 2025)**:

- ✅ **Fixed pip availability**: Both `Dockerfile` and `Dockerfile.lean` now install pip properly
- ✅ **Added writable cache directories**: `/tmp/uv-cache` and `/tmp/pip-cache` with proper permissions
- ✅ **Fixed installation logic**: Uses `uv pip install` instead of `uv add` to avoid lockfile issues
- ✅ **OpenShift compatibility**: Handles arbitrary UIDs and read-only filesystems
- ✅ **Proper fallback**: Falls back from `uv` to `pip` with custom cache directories
- ✅ **Memory optimization**: Increased backend memory from 4Gi to 8Gi limit
- ✅ **Memory monitoring**: Added memory checks before ML installation
- ✅ **Timeout handling**: Reduced timeouts to prevent hanging under memory pressure

**🚨 Emergency Recovery Commands**

If the backend keeps restarting due to OOM:

```powershell
# Scale down to stop failing pods
oc scale deployment/backend --replicas=0

# Wait a moment
Start-Sleep -Seconds 10

# Scale back up with new memory limits
oc scale deployment/backend --replicas=1

# Monitor the restart
oc get pods -w

# Check if memory patches are applied
oc describe deployment backend | Select-String "memory.*8Gi"
```

**Alternative Solutions**:
oc logs deployment/backend -f | findstr -i "install\|pytorch\|pip"

# Restart deployment to retry installation

oc rollout restart deployment/backend

````

#### 9. Backend Pod Memory Issues and Restarts

**Symptoms**:
- Backend pod shows `RestartCount > 0` in `oc get pods`
- Pod status cycles between `Running` and `Restarting`
- Logs show abrupt termination during ML package installation
- `oc get events` shows `OOMKilled` events

**Root Cause**: Runtime ML installation (PyTorch, HuggingFace) consumes significant memory, exceeding the original 4Gi limit.

**✅ Automated Fix Applied**:

All environments now automatically include memory-optimized patches:

- **Memory Limit**: Increased from 4Gi → 8Gi
- **Memory Request**: Increased from 4Gi → 6Gi
- **CPU Limit**: Increased from 1000m → 2000m (faster installation)
- **Memory Monitoring**: Functions check available memory before installation
- **Timeout Handling**: Shorter timeouts prevent hanging under memory pressure

**Verification**:

```powershell
# Check if memory optimization is applied
oc describe deployment backend | findstr -A 5 -B 5 "Limits\|Requests"

# Expected output should show:
# Limits:      cpu: 2, memory: 8Gi
# Requests:    cpu: 1, memory: 6Gi

# Monitor pod restart count
oc get pods -l component=backend

# Check for OOMKilled events
oc get events --sort-by=.metadata.creationTimestamp | findstr "OOMKilled"
```

**If Issues Persist**:

```powershell
# Option 1: Use full build to avoid runtime installation
.\scripts\deploy-openshift.ps1 -Environment dev -Build -Push -BackendBuild full

# Option 2: Use OpenAI/AWS instead of local ML
oc patch configmap backend-config -p '{"data":{"FORCE_DEFAULT_EMBEDDING":"text-embedding-3-small"}}'
oc rollout restart deployment/backend
```

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
````

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

### 🔍 HuggingFace Model Testing

```powershell
# Test HuggingFace model loading after fix
oc exec deployment/backend -- python -c "
import os
print('HF_HOME:', os.environ.get('HF_HOME'))
print('TRANSFORMERS_CACHE:', os.environ.get('TRANSFORMERS_CACHE'))
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('✅ Model loaded successfully with cache:', model.cache_folder)
"

# Check cache directory was created successfully
oc exec deployment/backend -- ls -la /tmp/ | findstr huggingface

# Test embedding generation
oc exec deployment/backend -- python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(['test sentence'])
print('✅ Embedding generated:', embeddings.shape)
"
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
