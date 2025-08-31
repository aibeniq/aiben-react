#!/usr/bin/env powershell

# Docker Image Size Optimization Script
# This script builds both lean (OpenAI-only) and full (with ML capabilities) versions

param(
    [Parameter(Mandatory=$false)]
    [string]$Version = "v1.0.0",
    
    [Parameter(Mandatory=$false)]
    [string]$Registry = "image-registry.openshift-image-registry.svc:5000/aibeniq-dev",
    
    [Parameter(Mandatory=$false)]
    [switch]$LeanOnly = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$FullOnly = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Push = $false
)

function Write-ColorOutput($ForegroundColor, $Text) {
    $originalColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Text
    $Host.UI.RawUI.ForegroundColor = $originalColor
}

Write-ColorOutput "Green" "=== Docker Image Size Optimization ==="
Write-Output ""

# Check if we're in the backend directory
if (!(Test-Path "pyproject.toml")) {
    Write-ColorOutput "Red" "Error: Please run this script from the backend directory"
    exit 1
}

$leanTag = "$Registry/aibeniq-backend-lean:$Version"
$fullTag = "$Registry/aibeniq-backend-full:$Version"

# Build lean version (OpenAI-only, ~500MB-1GB)
if (!$FullOnly) {
    Write-ColorOutput "Cyan" "Building lean version (OpenAI-only)..."
    Write-Output "Expected size: ~500MB-1GB"
    Write-Output "Features: OpenAI, AWS Bedrock, Ollama"
    Write-Output "Excluded: HuggingFace models (can be enabled at runtime)"
    Write-Output ""
    
    docker build -f Dockerfile.lean -t $leanTag .
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "Green" "✓ Lean image built successfully: $leanTag"
        $leanSize = docker images $leanTag --format "table {{.Size}}" | Select-Object -Skip 1
        Write-Output "Size: $leanSize"
    } else {
        Write-ColorOutput "Red" "✗ Failed to build lean image"
        exit 1
    }
    Write-Output ""
}

# Build full version (with all ML capabilities, larger size)
if (!$LeanOnly) {
    Write-ColorOutput "Cyan" "Building full version (with ML capabilities)..."
    Write-Output "Expected size: Larger (~2-3GB)"
    Write-Output "Features: All providers including HuggingFace"
    Write-Output ""
    
    docker build -f Dockerfile -t $fullTag .
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "Green" "✓ Full image built successfully: $fullTag"
        $fullSize = docker images $fullTag --format "table {{.Size}}" | Select-Object -Skip 1
        Write-Output "Size: $fullSize"
    } else {
        Write-ColorOutput "Red" "✗ Failed to build full image"
        exit 1
    }
    Write-Output ""
}

# Push images if requested
if ($Push) {
    Write-ColorOutput "Cyan" "Pushing images to registry..."
    
    if (!$FullOnly) {
        Write-Output "Pushing lean image..."
        docker push $leanTag
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "Green" "✓ Lean image pushed successfully"
        } else {
            Write-ColorOutput "Red" "✗ Failed to push lean image"
        }
    }
    
    if (!$LeanOnly) {
        Write-Output "Pushing full image..."
        docker push $fullTag
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "Green" "✓ Full image pushed successfully"
        } else {
            Write-ColorOutput "Red" "✗ Failed to push full image"
        }
    }
    Write-Output ""
}

# Display size comparison
Write-ColorOutput "Yellow" "=== Size Comparison ==="
if (!$FullOnly) {
    Write-Output "Lean version: $leanTag"
    docker images $leanTag --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}
if (!$LeanOnly) {
    Write-Output "Full version: $fullTag"
    docker images $fullTag --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
}

Write-Output ""
Write-ColorOutput "Yellow" "=== Usage Instructions ==="
Write-Output "For OpenShift deployment:"
Write-Output ""
Write-Output "1. Lean version (recommended for production):"
Write-Output "   - Use image: $leanTag"
Write-Output "   - Features: OpenAI, AWS, Ollama"
Write-Output "   - Size: ~500MB-1GB"
Write-Output ""
Write-Output "2. Full version (if you need HuggingFace models):"
Write-Output "   - Use image: $fullTag"
Write-Output "   - Features: All ML capabilities"
Write-Output "   - Size: Larger (~2-3GB)"
Write-Output ""
Write-Output "3. Runtime ML installation (lean + on-demand):"
Write-Output "   - Use lean image with environment variables:"
Write-Output "   - RUNTIME_INSTALL_PYTORCH=true"
Write-Output "   - This installs ML packages when first needed"
Write-Output ""

Write-ColorOutput "Green" "Build completed successfully!"
