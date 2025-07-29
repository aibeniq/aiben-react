# OpenShift Deployment Script for AIBeniq (PowerShell version)
# This script deploys the application to OpenShift using Kustomize

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod")]
    [string]$Environment,
    
    [switch]$Build,
    [switch]$Push,
    [switch]$DryRun,
    [switch]$Help
)

# Configuration
$REGISTRY = "quay.io"
$NAMESPACE = "aibeniq"
$PROJECT_NAME = ""
$OVERLAY_DIR = ""

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to show usage
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

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

# Set project name based on environment
if ($Environment -eq "dev") {
    $PROJECT_NAME = "aibeniq-dev"
    $OVERLAY_DIR = "openshift/overlays/development"
} elseif ($Environment -eq "prod") {
    $PROJECT_NAME = "aibeniq-prod"
    $OVERLAY_DIR = "openshift/overlays/production"
}

# Check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    # Check if oc is installed
    try {
        $null = Get-Command oc -ErrorAction Stop
    } catch {
        Write-Error-Custom "OpenShift CLI (oc) is not installed"
        exit 1
    }
    
    # Check if logged in to OpenShift
    try {
        $null = oc whoami 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Not logged in"
        }
    } catch {
        Write-Error-Custom "Not logged in to OpenShift. Run 'oc login' first"
        exit 1
    }
    
    # Check if kustomize is installed
    try {
        $null = Get-Command kustomize -ErrorAction Stop
    } catch {
        Write-Error-Custom "kustomize is not installed"
        exit 1
    }
    
    # Check if Docker is running (if building images)
    if ($Build) {
        try {
            $null = docker info 2>$null
            if ($LASTEXITCODE -ne 0) {
                throw "Docker not running"
            }
        } catch {
            Write-Error-Custom "Docker is not running"
            exit 1
        }
    }
    
    Write-Success "Prerequisites check passed"
}

# Build Docker images
function Build-Images {
    if (-not $Build) {
        return
    }
    
    Write-Status "Building Docker images..."
    
    # Get git commit hash for tagging
    try {
        $GIT_COMMIT = git rev-parse --short HEAD
        $BRANCH_NAME = git rev-parse --abbrev-ref HEAD
        $IMAGE_TAG = "$BRANCH_NAME-$GIT_COMMIT"
    } catch {
        Write-Warning "Could not get git information, using 'latest' tag"
        $IMAGE_TAG = "latest"
    }
    
    # Build backend image
    Write-Status "Building backend image..."
    docker build -t "$REGISTRY/$NAMESPACE/backend:$IMAGE_TAG" ./backend
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to build backend image"
        exit 1
    }
    docker tag "$REGISTRY/$NAMESPACE/backend:$IMAGE_TAG" "$REGISTRY/$NAMESPACE/backend:latest"
    
    # Build frontend image
    Write-Status "Building frontend image..."
    $API_URL = "https://api-$PROJECT_NAME.apps.your-cluster.com"
    docker build -t "$REGISTRY/$NAMESPACE/frontend:$IMAGE_TAG" ./frontend --build-arg VITE_API_URL=$API_URL
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to build frontend image"
        exit 1
    }
    docker tag "$REGISTRY/$NAMESPACE/frontend:$IMAGE_TAG" "$REGISTRY/$NAMESPACE/frontend:latest"
    
    Write-Success "Images built successfully"
    
    # Push images if requested
    if ($Push) {
        Write-Status "Pushing images to registry..."
        docker push "$REGISTRY/$NAMESPACE/backend:$IMAGE_TAG"
        docker push "$REGISTRY/$NAMESPACE/backend:latest"
        docker push "$REGISTRY/$NAMESPACE/frontend:$IMAGE_TAG"
        docker push "$REGISTRY/$NAMESPACE/frontend:latest"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Images pushed successfully"
        } else {
            Write-Error-Custom "Failed to push images"
            exit 1
        }
    }
}

# Deploy to OpenShift
function Deploy-ToOpenShift {
    Write-Status "Deploying to OpenShift environment: $Environment"
    
    # Ensure project exists
    $projectExists = oc get project $PROJECT_NAME 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Creating project: $PROJECT_NAME"
        oc new-project $PROJECT_NAME
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Custom "Failed to create project"
            exit 1
        }
    } else {
        Write-Status "Using existing project: $PROJECT_NAME"
        oc project $PROJECT_NAME
    }
    
    # Check if overlay directory exists
    if (-not (Test-Path $OVERLAY_DIR)) {
        Write-Error-Custom "Overlay directory not found: $OVERLAY_DIR"
        exit 1
    }
    
    # Change to the appropriate overlay directory
    Push-Location $OVERLAY_DIR
    
    try {
        # Generate the manifests
        Write-Status "Generating Kubernetes manifests..."
        $MANIFESTS = kustomize build .
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Custom "Failed to generate manifests"
            exit 1
        }
        
        if ($DryRun) {
            Write-Warning "DRY RUN - The following manifests would be applied:"
            Write-Output $MANIFESTS
            return
        }
        
        # Apply the manifests
        Write-Status "Applying manifests to OpenShift..."
        $MANIFESTS | oc apply -f -
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Custom "Failed to apply manifests"
            exit 1
        }
        
        # Wait for deployments to be ready
        Write-Status "Waiting for deployments to be ready..."
        oc rollout status deployment/postgres -n $PROJECT_NAME --timeout=300s
        oc rollout status deployment/backend -n $PROJECT_NAME --timeout=300s
        oc rollout status deployment/frontend -n $PROJECT_NAME --timeout=300s
        
        # Run database migrations if this is a new deployment
        Write-Status "Waiting for database prestart job..."
        oc wait --for=condition=complete job/prestart --timeout=300s -n $PROJECT_NAME
        
        Write-Success "Deployment completed successfully!"
        
        # Show application URLs
        Write-Status "Application URLs:"
        $routes = oc get routes -n $PROJECT_NAME -o json | ConvertFrom-Json
        foreach ($route in $routes.items) {
            $name = $route.metadata.name
            $host = $route.spec.host
            Write-Output "  $name`: https://$host"
        }
        
    } finally {
        Pop-Location
    }
}

# Main execution
function Main {
    Write-Status "Starting OpenShift deployment for environment: $Environment"
    
    Test-Prerequisites
    Build-Images
    Deploy-ToOpenShift
    
    Write-Success "Deployment script completed successfully!"
}

# Run main function
try {
    Main
} catch {
    Write-Error-Custom "Deployment failed: $($_.Exception.Message)"
    exit 1
}
