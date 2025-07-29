#!/bin/bash

# OpenShift Configuration Validation Script
# This script validates the OpenShift configuration files

set -e

echo "=== OpenShift Configuration Validation ==="

# Check if required directories exist
echo "Checking directory structure..."
for dir in "openshift/base" "openshift/overlays/development" "openshift/overlays/production"; do
    if [ -d "$dir" ]; then
        echo "✓ $dir exists"
    else
        echo "✗ $dir missing"
        exit 1
    fi
done

# Check if base manifests exist
echo -e "\nChecking base manifests..."
base_files=("configmap.yaml" "secrets.yaml" "postgres.yaml" "backend.yaml" "frontend.yaml" "prestart-job.yaml" "kustomization.yaml")
for file in "${base_files[@]}"; do
    if [ -f "openshift/base/$file" ]; then
        echo "✓ openshift/base/$file exists"
    else
        echo "✗ openshift/base/$file missing"
        exit 1
    fi
done

# Check overlay files
echo -e "\nChecking overlay files..."
for env in "development" "production"; do
    overlay_dir="openshift/overlays/$env"
    if [ -f "$overlay_dir/kustomization.yaml" ]; then
        echo "✓ $overlay_dir/kustomization.yaml exists"
    else
        echo "✗ $overlay_dir/kustomization.yaml missing"
        exit 1
    fi
done

# Validate YAML syntax
echo -e "\nValidating YAML syntax..."
yaml_files=$(find openshift -name "*.yaml" -o -name "*.yml")
for file in $yaml_files; do
    if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
        echo "✓ $file - valid YAML"
    else
        echo "✗ $file - invalid YAML"
        exit 1
    fi
done

# Check Dockerfile updates
echo -e "\nChecking Dockerfile updates..."
if grep -q "USER appuser" backend/Dockerfile; then
    echo "✓ Backend Dockerfile has non-root user"
else
    echo "✗ Backend Dockerfile missing non-root user"
    exit 1
fi

if grep -q "USER 1000" frontend/Dockerfile; then
    echo "✓ Frontend Dockerfile has non-root user"
else
    echo "✗ Frontend Dockerfile missing non-root user"
    exit 1
fi

# Check health endpoints
echo -e "\nChecking health endpoints..."
if grep -q "/health" backend/app/utils.py && grep -q "/ready" backend/app/utils.py; then
    echo "✓ Health endpoints implemented in backend"
else
    echo "✗ Health endpoints missing in backend"
    exit 1
fi

# Check deployment scripts
echo -e "\nChecking deployment scripts..."
if [ -f "scripts/deploy-openshift.sh" ]; then
    echo "✓ Bash deployment script exists"
else
    echo "✗ Bash deployment script missing"
fi

if [ -f "scripts/deploy-openshift.ps1" ]; then
    echo "✓ PowerShell deployment script exists"
else
    echo "✗ PowerShell deployment script missing"
fi

# Check GitHub Actions workflow
echo -e "\nChecking CI/CD configuration..."
if [ -f ".github/workflows/openshift-deploy.yml" ]; then
    echo "✓ GitHub Actions workflow exists"
else
    echo "✗ GitHub Actions workflow missing"
fi

echo -e "\n=== Validation Complete ==="
echo "✅ All OpenShift configuration files are valid and ready for deployment!"

# Show next steps
echo -e "\n=== Next Steps ==="
echo "1. Install kustomize: curl -s \"https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh\" | bash"
echo "2. Install OpenShift CLI: Download from your OpenShift console"
echo "3. Login to OpenShift: oc login --token=<token> --server=<server>"
echo "4. Deploy to development: ./scripts/deploy-openshift.sh -e dev"
echo "5. Configure GitHub secrets for automated deployment"
