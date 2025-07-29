# OpenShift Deployment Guide

This guide covers deploying the AIBeniq application to RedHat OpenShift using Kubernetes manifests and GitOps practices.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Overview](#architecture-overview)
3. [Quick Start](#quick-start)
4. [Manual Deployment](#manual-deployment)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Configuration Management](#configuration-management)
7. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
8. [Security Considerations](#security-considerations)

## Prerequisites

### Required Tools

- **OpenShift CLI (oc)**: Version 4.10+
- **Kustomize**: Version 4.0+
- **Docker**: For building images locally
- **Git**: For source control

### Installation

#### OpenShift CLI

```bash
# Download from OpenShift Console or
curl -LO https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz
tar -xzf oc.tar.gz
sudo mv oc /usr/local/bin/
```

#### Kustomize

```bash
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
sudo mv kustomize /usr/local/bin/
```

### OpenShift Access

1. **Log in to OpenShift cluster:**

   ```bash
   oc login --token=<your-token> --server=<cluster-api-url>
   ```

2. **Verify access:**
   ```bash
   oc whoami
   oc cluster-info
   ```

## Architecture Overview

### Components

- **Frontend**: React application served by Nginx
- **Backend**: FastAPI application with async support
- **Database**: PostgreSQL with persistent storage
- **Vector Database**: Milvus for semantic search
- **Reverse Proxy**: OpenShift Routes (replaces Traefik)

### Deployment Structure

```
openshift/
├── base/                           # Base Kubernetes manifests
│   ├── configmap.yaml             # Application configuration
│   ├── secrets.yaml               # Secret templates
│   ├── postgres.yaml              # PostgreSQL deployment
│   ├── backend.yaml               # Backend API deployment
│   ├── frontend.yaml              # Frontend deployment
│   ├── prestart-job.yaml          # Database migration job
│   └── kustomization.yaml         # Base kustomization
└── overlays/                      # Environment-specific overlays
    ├── development/
    │   ├── kustomization.yaml     # Dev-specific configuration
    │   ├── configmap-patch.yaml   # Dev config overrides
    │   └── resources-patch.yaml   # Dev resource limits
    └── production/
        ├── kustomization.yaml     # Prod-specific configuration
        ├── configmap-patch.yaml   # Prod config overrides
        ├── resources-patch.yaml   # Prod resource limits
        └── hpa.yaml               # Horizontal Pod Autoscaler
```

## Quick Start

### Using Deployment Scripts

#### Linux/macOS

```bash
# Deploy to development
./scripts/deploy-openshift.sh -e dev

# Build and deploy to production
./scripts/deploy-openshift.sh -e prod -b -p

# Dry run
./scripts/deploy-openshift.sh -e dev -d
```

#### Windows (PowerShell)

```powershell
# Deploy to development
.\scripts\deploy-openshift.ps1 -Environment dev

# Build and deploy to production
.\scripts\deploy-openshift.ps1 -Environment prod -Build -Push

# Dry run
.\scripts\deploy-openshift.ps1 -Environment dev -DryRun
```

## Manual Deployment

### Step 1: Create Projects

```bash
# Development environment
oc new-project aibeniq-dev

# Production environment
oc new-project aibeniq-prod
```

### Step 2: Configure Secrets

Create the necessary secrets in each project:

```bash
# Database secret
oc create secret generic postgres-secret \
  --from-literal=username=aibeniq \
  --from-literal=password=your-secure-password \
  --from-literal=database=aibeniq

# Application secrets
oc create secret generic app-secrets \
  --from-literal=secret-key=your-secret-key \
  --from-literal=openai-api-key=your-openai-key \
  --from-literal=aws-access-key-id=your-aws-key \
  --from-literal=aws-secret-access-key=your-aws-secret
```

### Step 3: Deploy Applications

#### Development Environment

```bash
cd openshift/overlays/development
kustomize build . | oc apply -f -
```

#### Production Environment

```bash
cd openshift/overlays/production
kustomize build . | oc apply -f -
```

### Step 4: Verify Deployment

```bash
# Check pod status
oc get pods

# Check deployments
oc get deployments

# Check routes
oc get routes

# Follow logs
oc logs -f deployment/backend
```

## CI/CD Pipeline

### GitHub Actions Workflow

The `.github/workflows/openshift-deploy.yml` file provides automated deployment:

1. **Build Stage**: Builds and pushes container images
2. **Deploy Dev**: Automatically deploys develop branch to development
3. **Deploy Prod**: Automatically deploys main branch to production

### Required Secrets

Configure these secrets in your GitHub repository:

- `REGISTRY_USERNAME`: Container registry username
- `REGISTRY_PASSWORD`: Container registry password/token
- `OPENSHIFT_TOKEN`: OpenShift service account token
- `OPENSHIFT_SERVER`: OpenShift cluster API server URL

### Service Account Setup

Create a service account for CI/CD:

```bash
# Create service account
oc create serviceaccount cicd-sa

# Grant necessary permissions
oc policy add-role-to-user admin system:serviceaccount:aibeniq-dev:cicd-sa
oc policy add-role-to-user admin system:serviceaccount:aibeniq-prod:cicd-sa

# Get token
oc serviceaccounts get-token cicd-sa
```

## Configuration Management

### Environment Variables

Configuration is managed through ConfigMaps and can be overridden per environment:

#### Development Configuration

```yaml
# openshift/overlays/development/configmap-patch.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  ENVIRONMENT: "development"
  DEBUG: "true"
  LOG_LEVEL: "DEBUG"
```

#### Production Configuration

```yaml
# openshift/overlays/production/configmap-patch.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
```

### Resource Management

#### Development Resources

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

#### Production Resources

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

## Monitoring and Troubleshooting

### Health Checks

The application includes health check endpoints:

- **Liveness**: `/health` - Basic application health
- **Readiness**: `/ready` - Database connectivity check

### Common Commands

```bash
# Check application status
oc get all

# View pod logs
oc logs -f deployment/backend
oc logs -f deployment/frontend

# Access pod shell
oc exec -it deployment/backend -- /bin/bash

# Port forward for local testing
oc port-forward service/backend 8000:8000

# Scale deployment
oc scale deployment/backend --replicas=3

# Check resource usage
oc top pods
oc top nodes
```

### Troubleshooting Issues

#### Database Connection Issues

```bash
# Check postgres pod
oc get pods -l app=postgres

# Check database logs
oc logs deployment/postgres

# Test database connection
oc exec deployment/postgres -- psql -U aibeniq -d aibeniq -c "\dt"
```

#### Image Pull Issues

```bash
# Check image pull secrets
oc get secrets

# Check events
oc get events --sort-by=.metadata.creationTimestamp

# Describe pod for detailed error
oc describe pod <pod-name>
```

#### Route Issues

```bash
# Check routes
oc get routes

# Check route configuration
oc describe route frontend

# Test internal service
oc exec deployment/backend -- curl http://frontend:80
```

## Security Considerations

### Container Security

1. **Non-root execution**: All containers run as non-root users
2. **Security contexts**: Proper security context constraints
3. **Resource limits**: CPU and memory limits enforced
4. **Image scanning**: Regular vulnerability scanning

### Network Security

1. **Network policies**: Restrict pod-to-pod communication
2. **TLS termination**: HTTPS enforced at route level
3. **Service mesh**: Consider implementing Istio for enhanced security

### Secret Management

1. **Sealed secrets**: Consider using sealed-secrets operator
2. **External secrets**: Integrate with HashiCorp Vault or AWS Secrets Manager
3. **Rotation**: Regular secret rotation policies

### Example Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aibeniq-network-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
```

## Scaling and Performance

### Horizontal Pod Autoscaler

Production environment includes HPA configuration:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Performance Tuning

1. **Resource requests/limits**: Properly sized based on load testing
2. **Readiness probes**: Ensure pods are ready before receiving traffic
3. **Connection pooling**: Database connection pooling configured
4. **Caching**: Redis integration for caching layer

## Backup and Disaster Recovery

### Database Backups

```bash
# Create backup job
oc create job postgres-backup --from=cronjob/postgres-backup

# Manual backup
oc exec deployment/postgres -- pg_dump -U aibeniq aibeniq > backup.sql
```

### Application Data

1. **Persistent volumes**: Ensure proper backup of PVs
2. **Configuration**: Store all configuration in Git
3. **Secrets**: Backup secret definitions (not values)

## Maintenance

### Rolling Updates

```bash
# Update image
oc set image deployment/backend backend=quay.io/aibeniq/backend:v2.0.0

# Check rollout status
oc rollout status deployment/backend

# Rollback if needed
oc rollout undo deployment/backend
```

### Maintenance Windows

1. **Schedule**: Plan maintenance during low-usage periods
2. **Communication**: Notify users of planned downtime
3. **Rollback plan**: Always have a rollback strategy

This documentation provides a comprehensive guide for deploying and managing the AIBeniq application on OpenShift. For additional support, refer to the OpenShift documentation or contact the development team.
