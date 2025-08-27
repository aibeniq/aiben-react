# OpenShift Deployment Script for AIBeniq (PowerShell version)
# This script deploys the application to OpenShift using Kustomize

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod")]
    [string]$Environment,

    [switch]$Build,
    [switch]$Push,
    [switch]$DryRun,
    [switch]$Help,
    [switch]$Internal
)

# Configuration
# Default values - using script scope for global access
$script:REGISTRY = "quay.io"
$script:NAMESPACE = "aibeniq"
$PROJECT_NAME = ""
$OVERLAY_DIR = ""

# Output helpers
function Write-Status { param([string]$Message) ; Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param([string]$Message) ; Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) ; Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error-Custom { param([string]$Message) ; Write-Host "[ERROR] $Message" -ForegroundColor Red }

function Show-Usage {
@"
Usage: .\deploy-openshift.ps1 [OPTIONS]

Deploy AIBeniq application to OpenShift

PARAMETERS:
    -Environment ENV         Target environment (dev|prod) [required]
    -Build                  Build Docker images locally
    -Push                   Push images to registry (requires -Build)
    -DryRun                 Show what would be deployed without applying
    -Help                   Show this help message

EXAMPLES:
    .\deploy-openshift.ps1 -Environment dev
    .\deploy-openshift.ps1 -Environment prod -Build -Push
    .\deploy-openshift.ps1 -Environment dev -DryRun

PREREQUISITES:
    - oc CLI must be installed and logged in
    - Docker must be running (if building images)
    - kustomize must be installed

"@
}

if ($Help) { Show-Usage ; exit 0 }

if ($Environment -eq "dev") {
    $script:PROJECT_NAME = "aibeniq-dev"
    $script:OVERLAY_DIR = "openshift/overlays/development"
} elseif ($Environment -eq "prod") {
    $script:PROJECT_NAME = "aibeniq-prod"
    $script:OVERLAY_DIR = "openshift/overlays/production"
}

function Setup-InternalRegistry {
    if (-not $Internal) { return }
    
    Write-Status "Setting up OpenShift internal registry configuration..."
    Write-Status "Attempting 'oc registry login' to configure Docker credentials..."
    oc registry login
    
    try {
        $script:REGISTRY = (oc registry info).Trim()
        $script:NAMESPACE = $script:PROJECT_NAME
        Write-Status "Internal registry: $script:REGISTRY, namespace: $script:NAMESPACE"
    } catch {
        Write-Warning "Could not determine internal registry info; falling back to configured registry: $script:REGISTRY"
    }

    # Check if Docker credentials exist for the registry
    $dockerConfigPath = Join-Path $env:USERPROFILE '.docker\config.json'
    $hasAuth = $false
    if (Test-Path $dockerConfigPath) {
        try {
            $cfg = Get-Content $dockerConfigPath -Raw | ConvertFrom-Json
            if ($cfg.auths -and $cfg.auths.$script:REGISTRY) { $hasAuth = $true }
        } catch { }
    }

    if (-not $hasAuth) {
        Write-Status "No docker credentials found for $script:REGISTRY - performing manual docker login with token"
        $token = oc whoami -t
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($token)) { 
            Write-Error-Custom "Could not obtain OpenShift token for docker login" 
            exit 1 
        }
        $user = oc whoami
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($user)) { 
            $user = 'oc-user' 
        }

        $token | docker login --username $user --password-stdin $script:REGISTRY
        if ($LASTEXITCODE -ne 0) { 
            Write-Error-Custom "Docker login to $script:REGISTRY failed" 
            exit 1 
        }
        Write-Status "Docker login to $script:REGISTRY succeeded"
    }
    
    Write-Success "Internal registry setup completed"
}

function Setup-InternalRegistryPatches {
    if (-not $Internal) { return }
    
    Write-Status "Setting up internal registry image patches..."
    
    # Update the internal registry patches with current registry URL
    $registryUrl = $script:REGISTRY
    $namespace = $script:NAMESPACE
    
    $patchFile = Join-Path $script:OVERLAY_DIR "internal-registry-patches.yaml"
    
    # Update the patch file with the current registry URL
    $patchContent = @"
---
# Patch backend deployment to use internal registry
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    spec:
      containers:
        - name: backend
          image: $registryUrl/$namespace/backend:latest
---
# Patch frontend deployment to use internal registry  
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  template:
    spec:
      containers:
        - name: frontend
          image: $registryUrl/$namespace/frontend:latest
---
# Patch backend prestart job to use internal registry
apiVersion: batch/v1
kind: Job
metadata:
  name: backend-prestart
spec:
  template:
    spec:
      containers:
        - name: backend-prestart
          image: $registryUrl/$namespace/backend:latest
"@

    Set-Content -Path $patchFile -Value $patchContent -Encoding UTF8
    Write-Status "Created internal registry patches at: $patchFile"
    
    # Update kustomization.yaml to include the internal registry patches
    $kustomizationFile = Join-Path $script:OVERLAY_DIR "kustomization.yaml"
    
    if (Test-Path $kustomizationFile) {
        $kustomizationContent = Get-Content $kustomizationFile -Raw
        
        # Check if internal-registry-patches.yaml is already in the patches section
        if ($kustomizationContent -notmatch "internal-registry-patches\.yaml") {
            # Add the patch to the patches section
            if ($kustomizationContent -match "patches:") {
                # Add to existing patches section
                $kustomizationContent = $kustomizationContent -replace "(patches:)", "`$1`n- internal-registry-patches.yaml"
            } else {
                # Add patches section
                $kustomizationContent += "`npatches:`n- internal-registry-patches.yaml`n"
            }
            
            Set-Content -Path $kustomizationFile -Value $kustomizationContent -Encoding UTF8
            Write-Status "Updated $kustomizationFile to include internal registry patches"
        }
    }
    
    Write-Success "Internal registry patches configured"
}

function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    try { Get-Command oc -ErrorAction Stop } catch { Write-Error-Custom "OpenShift CLI (oc) is not installed" ; exit 1 }
    try { oc whoami > $null 2>&1 ; if ($LASTEXITCODE -ne 0) { throw 'Not logged in' } } catch { Write-Error-Custom "Not logged in to OpenShift. Run 'oc login' first" ; exit 1 }
    try { Get-Command kustomize -ErrorAction Stop } catch { Write-Error-Custom "kustomize is not installed" ; exit 1 }
    if ($Build) { try { docker info > $null 2>&1 ; if ($LASTEXITCODE -ne 0) { throw 'Docker not running' } } catch { Write-Error-Custom "Docker is not running" ; exit 1 } }
    Write-Success "Prerequisites check passed"
}

# Add this after the Build-Images function

function Create-NamespaceAndImageStreams {
    if (-not $Push) { return }
    
    # Ensure the namespace exists BEFORE creating ImageStreams
    Write-Status "Ensuring project exists: $script:PROJECT_NAME"
    & oc get project $script:PROJECT_NAME -o name > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Creating project: $script:PROJECT_NAME"
        & oc new-project $script:PROJECT_NAME
        if ($LASTEXITCODE -ne 0) { Write-Error-Custom "Failed to create project" ; exit 1 }
    }
    
    if ($Internal) {
        # Now create ImageStreams in the existing namespace
        Write-Status "Ensuring ImageStreams exist in namespace: $script:NAMESPACE"
        oc create imagestream backend -n $script:NAMESPACE --dry-run=client -o yaml | oc apply -f -
        oc create imagestream frontend -n $script:NAMESPACE --dry-run=client -o yaml | oc apply -f -
    }
}

function Push-Images {
    if (-not $Push) { return }
    
    Write-Status "Pushing images to registry: $script:REGISTRY/$script:NAMESPACE"
    
    # Get the IMAGE_TAG (should be available from Build-Images)
    if (-not $script:IMAGE_TAG) {
        try {
            $GIT_COMMIT = git rev-parse --short HEAD
            $BRANCH_NAME = git rev-parse --abbrev-ref HEAD
            $script:IMAGE_TAG = "$BRANCH_NAME-$GIT_COMMIT"
        } catch {
            $script:IMAGE_TAG = "latest"
        }
    }
    
    $pushCommands = @(
        "$script:REGISTRY/$script:NAMESPACE/backend:$script:IMAGE_TAG",
        "$script:REGISTRY/$script:NAMESPACE/backend:latest", 
        "$script:REGISTRY/$script:NAMESPACE/frontend:$script:IMAGE_TAG",
        "$script:REGISTRY/$script:NAMESPACE/frontend:latest"
    )
    
    foreach ($img in $pushCommands) {
        Write-Status "Pushing $img..."
        docker push $img
        if ($LASTEXITCODE -ne 0) { Write-Error-Custom "Failed to push image: $img" ; exit 1 }
    }
    Write-Success "Images pushed successfully"
}

# Update Build-Images function to remove the push logic
function Build-Images {
    if (-not $Build) { return }
    Write-Status "Building Docker images..."

    try {
        $GIT_COMMIT = git rev-parse --short HEAD
        $BRANCH_NAME = git rev-parse --abbrev-ref HEAD
        $script:IMAGE_TAG = "$BRANCH_NAME-$GIT_COMMIT"
    } catch {
        Write-Warning "Could not get git information, using 'latest' tag"
        $script:IMAGE_TAG = "latest"
    }

    Write-Status "Building backend image..."
    docker build -t "$script:REGISTRY/$script:NAMESPACE/backend:$script:IMAGE_TAG" ./backend
    if ($LASTEXITCODE -ne 0) { Write-Error-Custom "Failed to build backend image" ; exit 1 }
    docker tag "$script:REGISTRY/$script:NAMESPACE/backend:$script:IMAGE_TAG" "$script:REGISTRY/$script:NAMESPACE/backend:latest"

    Write-Status "Building frontend image..."
    # Use the correct API URL based on environment
    if ($Environment -eq "dev") {
        $API_URL = "https://redhat-api-dev.aiben.io"
    } elseif ($Environment -eq "prod") {
        $API_URL = "https://redhat-api.aiben.io"
    } else {
        $API_URL = "https://api-$script:PROJECT_NAME.apps.your-cluster.com"
    }
    Write-Status "Using API URL for frontend build: $API_URL"
    docker build -t "$script:REGISTRY/$script:NAMESPACE/frontend:$script:IMAGE_TAG" ./frontend --build-arg VITE_API_URL=$API_URL
    if ($LASTEXITCODE -ne 0) { Write-Error-Custom "Failed to build frontend image" ; exit 1 }
    docker tag "$script:REGISTRY/$script:NAMESPACE/frontend:$script:IMAGE_TAG" "$script:REGISTRY/$script:NAMESPACE/frontend:latest"

    Write-Success "Images built successfully"
}

function Deploy-ToOpenShift {
    Write-Status "Deploying to OpenShift environment: $Environment"
    & oc get project $script:PROJECT_NAME -o name > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Creating project: $script:PROJECT_NAME"
        & oc new-project $script:PROJECT_NAME
        if ($LASTEXITCODE -ne 0) { Write-Error-Custom "Failed to create project" ; exit 1 }
    } else {
        Write-Status "Using existing project: $script:PROJECT_NAME"
        & oc project $script:PROJECT_NAME
    }
    if (-not (Test-Path $script:OVERLAY_DIR)) { Write-Error-Custom "Overlay directory not found: $script:OVERLAY_DIR" ; exit 1 }
    Push-Location $script:OVERLAY_DIR
    try {
        Write-Status "Generating Kubernetes manifests..."
        $MANIFESTS = kustomize build .
        if ($LASTEXITCODE -ne 0) { Write-Error-Custom "Failed to generate manifests" ; exit 1 }
        if ($DryRun) { Write-Warning "DRY RUN - The following manifests would be applied:" ; Write-Output $MANIFESTS ; Pop-Location ; return }

        Write-Status "Applying manifests to OpenShift..."
        $MANIFESTS | oc apply -f -
        if ($LASTEXITCODE -ne 0) { Write-Error-Custom "Failed to apply manifests" ; exit 1 }

        Write-Status "Waiting for deployments to be ready..."
        oc rollout status deployment/postgres -n $script:PROJECT_NAME --timeout=300s
        oc rollout status deployment/backend -n $script:PROJECT_NAME --timeout=300s
        oc rollout status deployment/frontend -n $script:PROJECT_NAME --timeout=300s

        Write-Status "Waiting for database prestart job..."
        oc wait --for=condition=complete job/backend-prestart --timeout=300s -n $script:PROJECT_NAME

        Write-Success "Deployment completed successfully!"
        Write-Status "Application URLs:"
        $routes = oc get routes -n $script:PROJECT_NAME -o json | ConvertFrom-Json
        foreach ($route in $routes.items) {
            $routeName = $route.metadata.name
            $routeHost = $route.spec.host
            Write-Output ("  ${routeName}: https://${routeHost}")
        }
    } finally {
        Pop-Location
    }
}

# Main execution
function Main {
    Write-Status "Starting OpenShift deployment for environment: $Environment"
    Test-Prerequisites
    Setup-InternalRegistry          # Setup internal registry if needed
    Setup-InternalRegistryPatches   # Configure image patches for internal registry
    Build-Images                    # Build images with correct registry
    Create-NamespaceAndImageStreams # Create namespace and ImageStreams before pushing
    Push-Images                     # Push images to registry
    Deploy-ToOpenShift             # Deploy the application
    Write-Success "Deployment script completed successfully!"
}

# Run main function
try { Main } catch { Write-Error-Custom "Deployment failed: $($_.Exception.Message)" ; exit 1 }
