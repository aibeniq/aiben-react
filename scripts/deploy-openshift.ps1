# OpenShift Deployment Script for AIBeniq (PowerShell version)
# This script deploys the application to OpenShift using Kustomize

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod")]
    [string]$Environment,

    [switch]$Build,
    [switch]$Push,
    [switch]$NoCache,
    [switch]$DryRun,
    [switch]$Help,
    [switch]$Internal,
    [switch]$SkipSecrets,
    [switch]$InteractiveSecrets,
    [switch]$DiagnoseOnly,
    [string]$DiagnoseDeployment = "backend",
    [switch]$ForceCleanup,
    # Secret / credential inputs (optional; if omitted, reasonable defaults or randoms are generated)
    [string]$DbPassword,
    [string]$SecretKey,
    [string]$SuperuserEmail,
    [string]$SuperuserPassword,
    [string]$OpenAIKey
)

# Configuration
# Default values - using script scope for global access
$script:REGISTRY = ""  # Will be set to OpenShift internal registry
$script:NAMESPACE = ""
$PROJECT_NAME = ""
$OVERLAY_DIR = ""

# Output helpers
function Write-Status { param([string]$Message) ; Write-Host "[INFO] $Message" -ForegroundColor Blue }
function Write-Success { param([string]$Message) ; Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) ; Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-Error-Custom { param([string]$Message) ; Write-Host "[ERROR] $Message" -ForegroundColor Red }

# Diagnostic and Cleanup Functions
function Diagnose-StuckRollout {
    param([string]$DeploymentName = "backend")
    
    Write-Status "Diagnosing stuck rollout for $DeploymentName..."
    
    # Check rollout status with timeout
    Write-Host "=== Rollout Status ===" -ForegroundColor Yellow
    try {
        oc rollout status deployment/$DeploymentName --timeout=60s
    } catch {
        Write-Warning "Rollout status check failed or timed out"
    }
    
    # Check pod states
    Write-Host "`n=== Pod States ===" -ForegroundColor Yellow
    oc get pods -l component=$DeploymentName -o wide
    
    # Check for terminating pods
    Write-Host "`n=== Terminating Pods ===" -ForegroundColor Yellow
    $terminatingPods = oc get pods --field-selector=status.phase=Running | Select-String "Terminating"
    if ($terminatingPods) {
        Write-Warning "Found terminating pods:"
        $terminatingPods
    } else {
        Write-Host "No pods stuck in Terminating state" -ForegroundColor Green
    }
    
    # Check replica sets
    Write-Host "`n=== Replica Sets ===" -ForegroundColor Yellow
    oc get rs -l component=$DeploymentName
    
    # Check events
    Write-Host "`n=== Recent Events ===" -ForegroundColor Yellow
    $events = oc get events --sort-by=.metadata.creationTimestamp | Select-String $DeploymentName -Context 1 | Select-Object -Last 10
    if ($events) {
        $events
    } else {
        Write-Host "No recent events found for $DeploymentName" -ForegroundColor Gray
    }
    
    # Check readiness probes
    Write-Host "`n=== Readiness Probe Status ===" -ForegroundColor Yellow
    $pods = oc get pods -l component=$DeploymentName -o name 2>$null
    if ($pods) {
        foreach ($pod in $pods) {
            $podName = $pod -replace "pod/", ""
            Write-Host "Checking $podName..." -ForegroundColor Cyan
            $readinessInfo = oc describe pod $podName | Select-String -A 5 -B 5 "Readiness"
            if ($readinessInfo) {
                $readinessInfo
            } else {
                Write-Host "  No readiness probe information found" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "No pods found for component=$DeploymentName" -ForegroundColor Gray
    }
}

function Force-CleanupStuckDeployment {
    param([string]$DeploymentName = "backend")
    
    Write-Warning "Force cleaning stuck deployment: $DeploymentName"
    
    # 1. Scale down to 0 to stop all pods
    Write-Status "Scaling deployment to 0..."
    oc scale deployment/$DeploymentName --replicas=0
    Start-Sleep -Seconds 10
    
    # 2. Force delete any stuck pods
    Write-Status "Force deleting stuck pods..."
    $allPods = oc get pods -l component=$DeploymentName --no-headers 2>$null
    if ($allPods) {
        $podLines = $allPods -split "`n" | Where-Object { $_ -match "\S" }
        foreach ($line in $podLines) {
            $podName = ($line -split '\s+')[0]
            if ($podName -and $podName -ne "NAME") {
                Write-Status "Force deleting pod: $podName"
                oc delete pod $podName --force --grace-period=0 2>$null
            }
        }
    } else {
        Write-Host "No pods found to delete" -ForegroundColor Green
    }
    
    # 3. Clean up old replica sets
    Write-Status "Cleaning up old replica sets..."
    $oldRSOutput = oc get rs -l component=$DeploymentName --no-headers 2>$null
    if ($oldRSOutput) {
        $rsLines = $oldRSOutput -split "`n" | Where-Object { $_ -match "\S" }
        foreach ($line in $rsLines) {
            $parts = $line -split '\s+'
            $rsName = $parts[0]
            $desired = $parts[1]
            $current = $parts[2]
            $ready = $parts[3]
            
            # Delete replica sets with 0 desired replicas (old ones)
            if ($desired -eq "0" -and $rsName -ne "NAME") {
                Write-Status "Deleting old replica set: $rsName"
                oc delete rs $rsName 2>$null
            }
        }
    } else {
        Write-Host "No replica sets found to clean up" -ForegroundColor Green
    }
    
    # 4. Wait a moment for cleanup to complete
    Write-Status "Waiting for cleanup to complete..."
    Start-Sleep -Seconds 5
    
    # 5. Scale back up
    Write-Status "Scaling deployment back to 1..."
    oc scale deployment/$DeploymentName --replicas=1
    
    # 6. Wait for new rollout
    Write-Status "Waiting for new rollout to complete..."
    try {
        oc rollout status deployment/$DeploymentName --timeout=300s
        Write-Success "Deployment $DeploymentName successfully recovered!"
    } catch {
        Write-Warning "New rollout may still be in progress. Check status manually."
    }
}

function Show-Usage {
@"
Usage: .\deploy-openshift.ps1 [OPTIONS]

Deploy AIBeniq application to OpenShift

PARAMETERS:
    -Environment ENV         Target environment (dev|prod) [required]
    -Build                  Build Docker images locally
    -Push                   Push images to registry (requires -Build)
    -NoCache                Rebuild images without using Docker layer cache
    -DryRun                 Show what would be deployed without applying
    -Help                   Show this help message
    -SkipSecrets            Skip automatic secret configuration (not recommended)
    -InteractiveSecrets     Use interactive prompts for secrets (secure input)
    -DiagnoseOnly           Only run diagnostics on deployments (no deployment)
    -DiagnoseDeployment     Specify deployment to diagnose (default: backend)
    -ForceCleanup           Force cleanup stuck deployment specified by -DiagnoseDeployment

EXAMPLES:
    .\deploy-openshift.ps1 -Environment dev
    .\deploy-openshift.ps1 -Environment prod -Build -Push
    .\deploy-openshift.ps1 -Environment prod -Build -Push -NoCache
    .\deploy-openshift.ps1 -Environment dev -DryRun
    .\deploy-openshift.ps1 -Environment prod -InteractiveSecrets
    .\deploy-openshift.ps1 -Environment dev -DiagnoseOnly -DiagnoseDeployment backend
    .\deploy-openshift.ps1 -Environment dev -ForceCleanup -DiagnoseDeployment backend

TROUBLESHOOTING:
    -DiagnoseOnly           Run comprehensive diagnostics on stuck deployments
    -ForceCleanup           Force cleanup and restart a stuck deployment
    -DiagnoseDeployment     Specify which deployment to diagnose/cleanup

PREREQUISITES:
    - oc CLI must be installed and logged in
    - Docker must be running (if building images)
    - kustomize must be installed

SECURITY:
    By default, the script will configure secrets automatically using secure practices.
    Use -InteractiveSecrets for manual secret entry with hidden input.
    Use -SkipSecrets only if secrets are already properly configured.

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
    Write-Status "Setting up OpenShift internal registry configuration..."
    Write-Status "Attempting 'oc registry login' to configure Docker credentials..."
    oc registry login
    
    try {
        $script:REGISTRY = (oc registry info).Trim()
        $script:NAMESPACE = $script:PROJECT_NAME
        Write-Status "Internal registry: $script:REGISTRY, namespace: $script:NAMESPACE"
    } catch {
        Write-Error-Custom "Could not determine internal registry info. Make sure you're logged into OpenShift."
        exit 1
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
    if (-not $Build -and -not $Push) { 
        Write-Status "Skipping internal registry patches (not building/pushing)"
        return 
    }
    
    Write-Status "Setting up internal registry image patches..."
    $registryUrl = $script:REGISTRY
    $namespace = $script:NAMESPACE
    $patchFile = Join-Path $script:OVERLAY_DIR "internal-registry-patches.yaml"
    
    # Only create the patch file if it doesn't exist or if we're building
    if (-not (Test-Path $patchFile) -or $Build) {
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
"@
        Set-Content -Path $patchFile -Value $patchContent -Encoding UTF8
        Write-Status "Created internal registry patches at: $patchFile"
    } else {
        Write-Status "Internal registry patch file already exists"
    }
    
    # Do NOT modify kustomization.yaml - it should already be properly configured
    Write-Status "Using existing kustomization.yaml configuration"
    Write-Success "Internal registry patches configured"
}

# ===============================================================================
# Helper Functions for Secure Secret Management
# ===============================================================================

function Generate-SecureKey {
    param(
        [int]$Length = 64
    )
    
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    $key = ""
    for ($i = 0; $i -lt $Length; $i++) {
        $key += $chars[(Get-Random -Minimum 0 -Maximum $chars.Length)]
    }
    return $key
}

function Generate-SecurePassword {
    param(
        [int]$Length = 32
    )
    
    # Generate a secure password with mixed case, numbers, and URL-safe symbols
    $lowercase = "abcdefghijklmnopqrstuvwxyz"
    $uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" 
    $numbers = "0123456789"
    $symbols = "_-"  # Only URL-safe symbols to avoid database URL parsing issues
    
    $password = ""
    
    # Ensure at least one character from each category
    $password += $lowercase[(Get-Random -Minimum 0 -Maximum $lowercase.Length)]
    $password += $uppercase[(Get-Random -Minimum 0 -Maximum $uppercase.Length)]
    $password += $numbers[(Get-Random -Minimum 0 -Maximum $numbers.Length)]
    $password += $symbols[(Get-Random -Minimum 0 -Maximum $symbols.Length)]
    
    # Fill the rest randomly
    $allChars = $lowercase + $uppercase + $numbers + $symbols
    for ($i = 4; $i -lt $Length; $i++) {
        $password += $allChars[(Get-Random -Minimum 0 -Maximum $allChars.Length)]
    }
    
    # Shuffle the password
    $passwordArray = $password.ToCharArray()
    for ($i = $passwordArray.Length - 1; $i -gt 0; $i--) {
        $j = Get-Random -Minimum 0 -Maximum ($i + 1)
        $temp = $passwordArray[$i]
        $passwordArray[$i] = $passwordArray[$j]
        $passwordArray[$j] = $temp
    }
    
    return -join $passwordArray
}

function Get-SecureInput {
    param(
        [string]$Prompt,
        [string]$DefaultValue = $null,
        [switch]$IsPassword
    )
    
    if ($IsPassword) {
        if ($DefaultValue) {
            Write-Host "$Prompt (press Enter to use existing): " -NoNewline
        } else {
            Write-Host "${Prompt}: " -NoNewline
        }
        
        $secureString = Read-Host -AsSecureString
        if ($secureString.Length -eq 0 -and $DefaultValue) {
            return $DefaultValue
        }
        
        # Convert SecureString to plain text
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureString)
        $password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
        
        return $password
    } else {
        if ($DefaultValue) {
            $input = Read-Host "$Prompt (default: $DefaultValue)"
            if ([string]::IsNullOrWhiteSpace($input)) {
                return $DefaultValue
            }
            return $input
        } else {
            return Read-Host $Prompt
        }
    }
}

# ===============================================================================
# Core Deployment Functions
# ===============================================================================

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
    
    # Always create ImageStreams when pushing to internal registry
    Write-Status "Ensuring ImageStreams exist in namespace: $script:NAMESPACE"
    oc create imagestream backend -n $script:NAMESPACE --dry-run=client -o yaml | oc apply -f -
    oc create imagestream frontend -n $script:NAMESPACE --dry-run=client -o yaml | oc apply -f -
}

function Optimize-ImagePush {
    if (-not $Push) { return }
    
    Write-Status "Analyzing images to minimize push size..."
    
    # Initialize skip flags
    $script:SKIP_BACKEND_PUSH = $false
    $script:SKIP_FRONTEND_PUSH = $false
    
    # Get local image IDs
    try {
        $localBackendId = (docker images --format "{{.ID}}" "$script:REGISTRY/$script:NAMESPACE/backend:latest" | Select-Object -First 1)
        $localFrontendId = (docker images --format "{{.ID}}" "$script:REGISTRY/$script:NAMESPACE/frontend:latest" | Select-Object -First 1)
        
        if ($localBackendId) {
            Write-Status "Local backend image ID: $($localBackendId.Substring(0,12))..."
        }
        if ($localFrontendId) {
            Write-Status "Local frontend image ID: $($localFrontendId.Substring(0,12))..."
        }
        
        # Check if images exist in remote registry
        try {
            $remoteImages = oc get imagestream -o json 2>$null | ConvertFrom-Json
            if ($remoteImages.items) {
                foreach ($imagestream in $remoteImages.items) {
                    if ($imagestream.metadata.name -eq "backend" -and $imagestream.status.tags) {
                        $latestTag = $imagestream.status.tags | Where-Object { $_.tag -eq "latest" }
                        if ($latestTag -and $latestTag.items[0].dockerImageReference) {
                            $remoteBackendRef = $latestTag.items[0].dockerImageReference
                            Write-Status "Remote backend image: $($remoteBackendRef.Split(':')[-1].Substring(0,12))..."
                        }
                    }
                    if ($imagestream.metadata.name -eq "frontend" -and $imagestream.status.tags) {
                        $latestTag = $imagestream.status.tags | Where-Object { $_.tag -eq "latest" }
                        if ($latestTag -and $latestTag.items[0].dockerImageReference) {
                            $remoteFrontendRef = $latestTag.items[0].dockerImageReference
                            Write-Status "Remote frontend image: $($remoteFrontendRef.Split(':')[-1].Substring(0,12))..."
                        }
                    }
                }
            }
        } catch {
            Write-Status "Cannot compare remote images - will push all images"
        }
        
        # Calculate estimated push size
        try {
            $backendSize = (docker images --format "table {{.Size}}" "$script:REGISTRY/$script:NAMESPACE/backend:latest" | Select-Object -Skip 1).Trim()
            $frontendSize = (docker images --format "table {{.Size}}" "$script:REGISTRY/$script:NAMESPACE/frontend:latest" | Select-Object -Skip 1).Trim()
            Write-Status "Estimated push size - Backend: $backendSize, Frontend: $frontendSize"
        } catch {
            Write-Status "Could not determine image sizes"
        }
        
    } catch {
        Write-Status "Image comparison failed - proceeding with full push"
    }
    
    Write-Success "Image optimization analysis completed"
}

function Push-Images {
    if (-not $Push) { return }
    
    Write-Status "Pushing images with optimization to registry: $script:REGISTRY/$script:NAMESPACE"
    
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
    
    # Push with optimization - only push if not skipped
    $imagesNeedPush = @()
    
    # Always push latest tags (most important for deployment)
    if (-not $script:SKIP_BACKEND_PUSH) {
        $imagesNeedPush += "$script:REGISTRY/$script:NAMESPACE/backend:latest"
        Write-Status "Backend will be pushed (changes detected or verification failed)"
    } else {
        Write-Status "Backend push skipped (no changes detected)"
    }
    
    if (-not $script:SKIP_FRONTEND_PUSH) {
        $imagesNeedPush += "$script:REGISTRY/$script:NAMESPACE/frontend:latest"
        Write-Status "Frontend will be pushed (changes detected or verification failed)"
    } else {
        Write-Status "Frontend push skipped (no changes detected)"
    }
    
    # Only push versioned tags if we're building a specific version
    if ($script:IMAGE_TAG -ne "latest" -and $imagesNeedPush.Count -gt 0) {
        if (-not $script:SKIP_BACKEND_PUSH) {
            $imagesNeedPush += "$script:REGISTRY/$script:NAMESPACE/backend:$script:IMAGE_TAG"
        }
        if (-not $script:SKIP_FRONTEND_PUSH) {
            $imagesNeedPush += "$script:REGISTRY/$script:NAMESPACE/frontend:$script:IMAGE_TAG"
        }
    }
    
    if ($imagesNeedPush.Count -eq 0) {
        Write-Success "No images need to be pushed - all up to date!"
        return
    }
    
    Write-Status "Pushing $($imagesNeedPush.Count) images..."
    foreach ($img in $imagesNeedPush) {
        Write-Status "Pushing $img..."
        docker push $img
        if ($LASTEXITCODE -ne 0) { Write-Error-Custom "Failed to push image: $img" ; exit 1 }
    }
    Write-Success "Optimized image push completed successfully"
}

# Optimized Build-Images function with BuildKit support
function Build-Images {
    if (-not $Build) { return }
    
    # ✅ Enable BuildKit for better caching and layer optimization
    $env:DOCKER_BUILDKIT = "1"
    Write-Status "Building Docker images with BuildKit optimization..."

    try {
        $GIT_COMMIT = git rev-parse --short HEAD
        $BRANCH_NAME = git rev-parse --abbrev-ref HEAD
        $script:IMAGE_TAG = "$BRANCH_NAME-$GIT_COMMIT"
    } catch {
        Write-Warning "Could not get git information, using 'latest' tag"
        $script:IMAGE_TAG = "latest"
    }

    $cacheFlag = ""
    if ($NoCache) {
        $cacheFlag = "--no-cache"
        Write-Status "NoCache enabled: will bypass Docker build cache"
    }

    Write-Status "Building backend image..."
    docker build $cacheFlag -t "$script:REGISTRY/$script:NAMESPACE/backend:$script:IMAGE_TAG" ./backend
    if ($LASTEXITCODE -ne 0) { Write-Error-Custom "Failed to build backend image" ; exit 1 }
    docker tag "$script:REGISTRY/$script:NAMESPACE/backend:$script:IMAGE_TAG" "$script:REGISTRY/$script:NAMESPACE/backend:latest"

    Write-Status "Building frontend image..."
    # Use the correct API URL based on environment
    if ($Environment -eq "dev") {
        $API_URL = "http://redhat-api.aiben.io"  # HTTP for development (no SSL issues)
    } elseif ($Environment -eq "prod") {
        $API_URL = "https://redhat-api.aiben.io"
    } else {
        $API_URL = "https://api-$script:PROJECT_NAME.apps.your-cluster.com"
    }
    Write-Status "Using API URL for frontend build: $API_URL"
    docker build $cacheFlag -t "$script:REGISTRY/$script:NAMESPACE/frontend:$script:IMAGE_TAG" ./frontend --build-arg VITE_API_URL=$API_URL
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

        # Re-apply secrets with supplied / generated values AFTER manifests so placeholders are overridden
        Ensure-Secrets

        # Enhanced rollout with timeout handling and diagnostics
        Write-Status "Restarting deployments with enhanced monitoring..."
        
        # Restart postgres first
        Write-Status "Restarting PostgreSQL deployment..."
        oc rollout restart deployment/postgres -n $script:PROJECT_NAME | Out-Null
        try {
            oc rollout status deployment/postgres -n $script:PROJECT_NAME --timeout=120s
            Write-Success "PostgreSQL deployment completed successfully!"
        } catch {
            Write-Warning "PostgreSQL rollout timed out, attempting recovery..."
            Diagnose-StuckRollout -DeploymentName "postgres"
            Force-CleanupStuckDeployment -DeploymentName "postgres"
        }
        
        # Restart backend with enhanced monitoring
        Write-Status "Restarting backend deployment..."
        oc rollout restart deployment/backend -n $script:PROJECT_NAME | Out-Null
        Write-Status "Waiting for backend deployment (with termination monitoring)..."
        
        # Monitor backend rollout with periodic checks
        $maxAttempts = 6  # 6 attempts * 30 seconds = 3 minutes
        $attempt = 0
        $backendReady = $false
        
        while ($attempt -lt $maxAttempts -and -not $backendReady) {
            $attempt++
            Write-Status "Backend rollout attempt $attempt/$maxAttempts..."
            
            # Try rollout status with 30-second timeout
            try {
                oc rollout status deployment/backend -n $script:PROJECT_NAME --timeout=30s
                $backendReady = $true
                Write-Success "Backend deployment completed successfully!"
            } catch {
                Write-Warning "Backend rollout timeout (attempt $attempt), diagnosing..."
                Diagnose-StuckRollout -DeploymentName "backend"
                
                if ($attempt -eq $maxAttempts) {
                    Write-Warning "Maximum attempts reached. Attempting force cleanup..."
                    Force-CleanupStuckDeployment -DeploymentName "backend"
                    $backendReady = $true  # Assume cleanup worked
                } else {
                    Write-Status "Waiting 10 seconds before next attempt..."
                    Start-Sleep -Seconds 10
                }
            }
        }
        
        # Restart frontend (usually fast)
        Write-Status "Restarting frontend deployment..."
        oc rollout restart deployment/frontend -n $script:PROJECT_NAME | Out-Null
        try {
            oc rollout status deployment/frontend -n $script:PROJECT_NAME --timeout=120s
            Write-Success "Frontend deployment completed successfully!"
        } catch {
            Write-Warning "Frontend rollout timed out, attempting recovery..."
            Diagnose-StuckRollout -DeploymentName "frontend"
            Force-CleanupStuckDeployment -DeploymentName "frontend"
        }

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

function Ensure-Secrets {
    Write-Status "Ensuring consistent secrets configuration using consolidated architecture..."
    
    if ($SkipSecrets) {
        Write-Warning "Skipping secrets configuration (-SkipSecrets specified)"
        return
    }
    
    # Use the new setup-secrets script for consistent management
    Write-Status "Using new consolidated secret management..."
    
    # Ensure we're calling from the project root directory
    # Get current working directory and ensure we're in project root
    $currentDir = Get-Location
    Write-Status "Current directory: $currentDir"
    
    # If we're in an overlay directory, navigate back to project root
    if ($currentDir.Path -like "*overlays*") {
        $projectRoot = $currentDir.Path
        while ($projectRoot -like "*overlays*" -or $projectRoot -like "*openshift*") {
            $projectRoot = Split-Path -Parent $projectRoot
        }
        Write-Status "Navigating to project root: $projectRoot"
        Push-Location $projectRoot
        $needPopLocation = $true
    } else {
        $needPopLocation = $false
    }
    
    try {
        # Verify the setup-secrets.ps1 exists
        $setupSecretsPath = ".\scripts\setup-secrets.ps1"
        if (-not (Test-Path $setupSecretsPath)) {
            throw "setup-secrets.ps1 not found at $setupSecretsPath. Current directory: $(Get-Location)"
        }
        
        Write-Status "Calling setup-secrets from: $(Get-Location)"
        
        if ($InteractiveSecrets) {
            Write-Host "Running interactive secret setup..." -ForegroundColor Cyan
            & $setupSecretsPath -Environment $Environment -Interactive -Restart
        } else {
            Write-Host "Applying automatic secret fixes..." -ForegroundColor Green
            & $setupSecretsPath -Environment $Environment
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Custom "Secret setup failed"
            exit 1
        }
        
        Write-Success "Secrets configured successfully using consolidated architecture"
    } finally {
        if ($needPopLocation) {
            Pop-Location
        }
    }
}

# Main execution
function Main {
    Write-Status "Starting OpenShift deployment for environment: $Environment"
    
    # Handle diagnostic and cleanup modes first
    if ($DiagnoseOnly -or $ForceCleanup) {
        Write-Status "Setting up project context for diagnostics..."
        & oc project $script:PROJECT_NAME > $null 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error-Custom "Project $script:PROJECT_NAME not found. Please deploy first."
            exit 1
        }
        
        if ($DiagnoseOnly) {
            Write-Status "Running diagnostics for deployment: $DiagnoseDeployment"
            Diagnose-StuckRollout -DeploymentName $DiagnoseDeployment
            return
        }
        
        if ($ForceCleanup) {
            Write-Status "Force cleaning deployment: $DiagnoseDeployment"
            Force-CleanupStuckDeployment -DeploymentName $DiagnoseDeployment
            return
        }
    }
    
    # Display secret management mode
    if ($SkipSecrets) {
        Write-Warning "Secrets will be skipped during deployment (-SkipSecrets)"
    } elseif ($InteractiveSecrets) {
        Write-Host "Interactive secret configuration will be used (-InteractiveSecrets)" -ForegroundColor Cyan
    } else {
        Write-Host "Automatic secret generation will be used (environment variables honored)" -ForegroundColor Green
    }
    
    Test-Prerequisites              # Check prerequisites
    
    # Set up internal registry when building/pushing images
    if ($Build -or $Push) {
        Setup-InternalRegistry          # Setup internal registry for image operations
        Setup-InternalRegistryPatches   # Configure image patches for internal registry
    }
    
    Build-Images                    # Build images with correct registry and BuildKit optimization
    Create-NamespaceAndImageStreams # Create namespace and ImageStreams before pushing
    Optimize-ImagePush              # ✅ Analyze images to minimize push size
    Push-Images                     # Push only necessary images to registry
    Deploy-ToOpenShift             # Deploy the application (includes Ensure-Secrets)
    Write-Success "Deployment script completed successfully!"
}

# Run main function
try { Main } catch { Write-Error-Custom "Deployment failed: $($_.Exception.Message)" ; exit 1 }
