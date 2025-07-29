# OpenShift Cluster Setup Guide

This guide provides multiple options for setting up an OpenShift cluster for the AIBeniq application deployment.

## Table of Contents

1. [Quick Setup Options](#quick-setup-options)
2. [Red Hat OpenShift Service on AWS (ROSA)](#red-hat-openshift-service-on-aws-rosa)
3. [OpenShift Local (CRC)](#openshift-local-crc)
4. [Self-Managed OpenShift on AWS](#self-managed-openshift-on-aws)
5. [Azure Red Hat OpenShift (ARO)](#azure-red-hat-openshift-aro)
6. [Google Cloud Platform OpenShift](#google-cloud-platform-openshift)
7. [Cluster Configuration](#cluster-configuration)
8. [Post-Setup Validation](#post-setup-validation)

## Quick Setup Options

### **Option 1: Red Hat OpenShift Service on AWS (ROSA) - RECOMMENDED**

- **Best for**: Production deployments, enterprise use
- **Setup time**: 30-40 minutes
- **Cost**: Pay-as-you-go, starts ~$0.30/hour
- **Managed**: Fully managed by Red Hat

### **Option 2: OpenShift Local (CRC) - DEVELOPMENT**

- **Best for**: Local development, testing
- **Setup time**: 15-20 minutes
- **Cost**: Free
- **Managed**: Local development cluster

### **Option 3: Self-Managed on AWS**

- **Best for**: Custom requirements, full control
- **Setup time**: 1-2 hours
- **Cost**: EC2 + storage costs
- **Managed**: Self-managed

## Red Hat OpenShift Service on AWS (ROSA)

### Prerequisites

- AWS account with billing enabled
- Red Hat account
- AWS CLI configured
- ROSA CLI installed

### Step 1: Install ROSA CLI

```powershell
# Download ROSA CLI
# Go to: https://console.redhat.com/openshift/downloads
# Download rosa-windows-amd64.exe and add to PATH

# Verify installation
rosa version
```

### Step 2: Configure AWS and Red Hat Accounts

```powershell
# Configure AWS CLI (if not already done)
aws configure

# Login to Red Hat
rosa login

# Verify AWS account
rosa whoami
```

### Step 3: Create ROSA Cluster

```powershell
# Create cluster (replace with your preferred settings)
rosa create cluster `
  --cluster-name=aibeniq-cluster `
  --region=us-east-1 `
  --compute-machine-type=m5.xlarge `
  --compute-nodes=3 `
  --machine-cidr=10.0.0.0/16 `
  --service-cidr=172.30.0.0/16 `
  --pod-cidr=10.128.0.0/14 `
  --host-prefix=23

# Monitor cluster creation (takes 30-40 minutes)
rosa logs install --cluster=aibeniq-cluster --watch

# Check cluster status
rosa describe cluster --cluster=aibeniq-cluster
```

### Step 4: Create Admin User

```powershell
# Create cluster admin
rosa create admin --cluster=aibeniq-cluster

# Note: Save the login command and password provided
```

### Step 5: Login to Cluster

```powershell
# Use the login command from previous step
oc login https://api.aibeniq-cluster.xxxx.p1.openshiftapps.com:6443 `
  --username cluster-admin `
  --password <password-from-previous-step>

# Verify access
oc whoami
oc get nodes
```

## OpenShift Local (CRC)

### Step 1: Download and Install CRC

```powershell
# Download CRC from: https://developers.redhat.com/products/codeready-containers/download
# Extract to a directory in your PATH

# Verify installation
crc version
```

### Step 2: Setup CRC

```powershell
# Setup CRC (one time only)
crc setup

# Configure resources (minimum for AIBeniq)
crc config set cpus 4
crc config set memory 16384
crc config set disk-size 120

# Start CRC
crc start

# Get login information
crc console --credentials
```

### Step 3: Login to Local Cluster

```powershell
# Use credentials from previous step
oc login -u developer -p developer https://api.crc.testing:6443

# Or as admin
oc login -u kubeadmin -p <password> https://api.crc.testing:6443
```

## Self-Managed OpenShift on AWS

### Prerequisites

- AWS account with appropriate permissions
- Domain name for cluster
- Route 53 hosted zone

### Step 1: Download OpenShift Installer

```powershell
# Download from: https://console.redhat.com/openshift/install/aws/installer-provisioned
# Extract openshift-install.exe to PATH

# Verify
openshift-install version
```

### Step 2: Create Install Configuration

```powershell
# Create installation directory
mkdir openshift-install
cd openshift-install

# Generate install config
openshift-install create install-config --dir .

# Edit install-config.yaml as needed
```

### Step 3: Deploy Cluster

```powershell
# Create cluster (takes 30-45 minutes)
openshift-install create cluster --dir . --log-level=info

# Login using provided credentials
oc login https://api.aibeniq.your-domain.com:6443 -u kubeadmin -p <password>
```

## Azure Red Hat OpenShift (ARO)

### Step 1: Install Azure CLI and ARO Extension

```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI

# Add ARO extension
az extension add -n aro --index https://az.aroapp.io/stable
```

### Step 2: Create ARO Cluster

```powershell
# Login to Azure
az login

# Set subscription
az account set --subscription "Your Subscription Name"

# Create resource group
az group create --name aibeniq-rg --location eastus

# Create virtual network
az network vnet create `
  --resource-group aibeniq-rg `
  --name aro-vnet `
  --address-prefixes 10.0.0.0/22

# Create subnets
az network vnet subnet create `
  --resource-group aibeniq-rg `
  --vnet-name aro-vnet `
  --name master-subnet `
  --address-prefixes 10.0.0.0/23

az network vnet subnet create `
  --resource-group aibeniq-rg `
  --vnet-name aro-vnet `
  --name worker-subnet `
  --address-prefixes 10.0.2.0/23

# Create ARO cluster
az aro create `
  --resource-group aibeniq-rg `
  --name aibeniq-aro `
  --vnet aro-vnet `
  --master-subnet master-subnet `
  --worker-subnet worker-subnet `
  --worker-count 3
```

### Step 3: Get Cluster Credentials

```powershell
# Get console URL
az aro show --name aibeniq-aro --resource-group aibeniq-rg --query "consoleProfile.url" -o tsv

# Get API server URL
az aro show --name aibeniq-aro --resource-group aibeniq-rg --query "apiserverProfile.url" -o tsv

# Get admin credentials
az aro list-credentials --name aibeniq-aro --resource-group aibeniq-rg
```

## Google Cloud Platform OpenShift

### Option 1: Google Cloud OpenShift

```powershell
# Install gcloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# Create cluster through Anthos
gcloud container clusters create aibeniq-cluster `
  --enable-autoscaling `
  --min-nodes=1 `
  --max-nodes=10 `
  --zone=us-central1-a
```

### Option 2: Self-managed on GCP

Follow the self-managed approach but use GCP instead of AWS.

## Cluster Configuration

### Step 1: Create Projects

```powershell
# Create development project
oc new-project aibeniq-dev

# Create production project
oc new-project aibeniq-prod

# Verify projects
oc get projects
```

### Step 2: Configure RBAC (if needed)

```powershell
# Grant developer access to projects
oc policy add-role-to-user admin developer -n aibeniq-dev
oc policy add-role-to-user view developer -n aibeniq-prod
```

### Step 3: Configure Image Registry

```powershell
# For external registry (Quay.io)
oc create secret docker-registry quay-secret `
  --docker-server=quay.io `
  --docker-username=<username> `
  --docker-password=<password> `
  --docker-email=<email> `
  -n aibeniq-dev

oc create secret docker-registry quay-secret `
  --docker-server=quay.io `
  --docker-username=<username> `
  --docker-password=<password> `
  --docker-email=<email> `
  -n aibeniq-prod

# Link secret to default service account
oc secrets link default quay-secret --for=pull -n aibeniq-dev
oc secrets link default quay-secret --for=pull -n aibeniq-prod
```

## Post-Setup Validation

### Step 1: Verify Cluster Health

```powershell
# Check cluster status
oc get nodes
oc get clusteroperators

# Check projects
oc get projects

# Check storage classes
oc get storageclass
```

### Step 2: Test Application Deployment

```powershell
# Navigate to your project
cd c:\miniconda\aibeniq-react

# Run validation
.\scripts\setup-openshift-prerequisites.ps1

# Test deployment (dry run)
.\scripts\deploy-openshift.ps1 -Environment dev -DryRun

# If dry run succeeds, deploy
.\scripts\deploy-openshift.ps1 -Environment dev
```

### Step 3: Access Application

```powershell
# Get routes
oc get routes -n aibeniq-dev

# Check pod status
oc get pods -n aibeniq-dev

# Follow logs
oc logs -f deployment/backend -n aibeniq-dev
```

## Cost Optimization

### ROSA Cost Management

- Use spot instances for development
- Scale down non-production environments
- Set up cluster autoscaling
- Monitor usage with AWS Cost Explorer

### CRC Resource Management

```powershell
# Stop CRC when not in use
crc stop

# Start when needed
crc start
```

### Self-Managed Optimization

- Use AWS Savings Plans
- Implement cluster autoscaling
- Use mixed instance types
- Schedule start/stop for development clusters

## Troubleshooting

### Common Issues

#### ROSA Creation Fails

```powershell
# Check AWS limits
aws service-quotas get-service-quota --service-code ec2 --quota-code L-1216C47A

# Check IAM permissions
rosa verify permissions
```

#### CRC Won't Start

```powershell
# Reset CRC
crc delete
crc setup
crc start
```

#### Authentication Issues

```powershell
# Check token
oc whoami -t

# Re-login
oc login --token=<new-token> --server=<server-url>
```

## Security Considerations

### Network Security

- Configure VPC with private subnets
- Use security groups to restrict access
- Enable VPN or Direct Connect for on-premises access

### Access Control

- Implement RBAC policies
- Use federated authentication (LDAP/AD)
- Regular access reviews

### Compliance

- Enable audit logging
- Configure monitoring and alerting
- Regular security scanning

## Next Steps

After setting up your cluster:

1. **Run the prerequisites script**:

   ```powershell
   .\scripts\setup-openshift-prerequisites.ps1
   ```

2. **Configure your environment**:

   - Update `.env` file with cluster details
   - Configure container registry access

3. **Deploy AIBeniq**:

   ```powershell
   .\scripts\deploy-openshift.ps1 -Environment dev
   ```

4. **Set up monitoring** (optional):

   - Configure Prometheus/Grafana
   - Set up alerting rules

5. **Configure CI/CD**:
   - Set up GitHub Actions secrets
   - Test automated deployment

Choose the setup option that best fits your requirements and budget. For production use, ROSA is recommended for its managed service benefits.
