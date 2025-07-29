# Quick Start: OpenShift Deployment

This is a streamlined guide to get AIBeniq running on OpenShift quickly. For detailed instructions, see `OPENSHIFT_CLUSTER_SETUP.md`.

## 🚀 Fast Track Setup (30 minutes)

### Option A: Local Development (Free)

```powershell
# 1. Install prerequisites
.\scripts\setup-openshift-prerequisites.ps1

# 2. Download and setup CRC
# Download from: https://developers.redhat.com/products/codeready-containers/download
crc setup
crc config set memory 16384
crc start

# 3. Login to local cluster
oc login -u developer -p developer https://api.crc.testing:6443

# 4. Deploy application
.\scripts\deploy-openshift.ps1 -Environment dev
```

### Option B: AWS Production (40 minutes + AWS costs)

```powershell
# 1. Install prerequisites
.\scripts\setup-openshift-prerequisites.ps1

# 2. Install ROSA CLI
# Download from: https://console.redhat.com/openshift/downloads

# 3. Configure AWS and create cluster
aws configure
rosa login
rosa create cluster --cluster-name=aibeniq --region=us-east-1 --compute-nodes=3

# 4. Wait for cluster (30-40 min), then login
rosa create admin --cluster=aibeniq
# Use provided login command

# 5. Deploy application
.\scripts\deploy-openshift.ps1 -Environment dev
```

## 📋 Prerequisites Checklist

Run this script to install everything you need:

```powershell
.\scripts\setup-openshift-prerequisites.ps1
```

This installs:

- ✅ OpenShift CLI (oc)
- ✅ Kustomize
- ✅ Chocolatey (package manager)
- ✅ Verifies Docker

## 🔧 Manual Installation (if script fails)

### OpenShift CLI

```powershell
# Option 1: Chocolatey
choco install openshift-cli

# Option 2: Direct download
# https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/windows/
```

### Kustomize

```powershell
# Option 1: Chocolatey
choco install kustomize

# Option 2: Direct download
# https://github.com/kubernetes-sigs/kustomize/releases
```

## 🎯 Recommended Path

**For Learning/Development**: Use CRC (local)
**For Production**: Use ROSA (managed AWS)

## 💡 Need Help?

1. **Setup Issues**: Check `OPENSHIFT_CLUSTER_SETUP.md`
2. **Deployment Issues**: Check `OPENSHIFT_DEPLOYMENT.md`
3. **Application Issues**: Run `.\scripts\deploy-openshift.ps1 -Environment dev -DryRun`

## 📞 Support Commands

```powershell
# Check prerequisites
.\scripts\setup-openshift-prerequisites.ps1

# Validate configuration
.\scripts\deploy-openshift.ps1 -Environment dev -DryRun

# Check cluster status
oc get nodes
oc get projects

# Check application status
oc get pods -n aibeniq-dev
oc logs -f deployment/backend -n aibeniq-dev
```

Choose your path and get started! 🚀
