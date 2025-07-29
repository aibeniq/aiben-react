# OpenShift Prerequisites Setup Script
# This script installs the required tools for OpenShift deployment

param(
    [switch]$SkipChocolatey,
    [switch]$Help
)

# Color functions
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

function Show-Usage {
    @"
OpenShift Prerequisites Setup Script

This script installs the required tools for deploying AIBeniq to OpenShift:
- OpenShift CLI (oc)
- Kustomize
- Chocolatey (package manager)

USAGE:
    .\setup-openshift-prerequisites.ps1 [OPTIONS]

OPTIONS:
    -SkipChocolatey    Skip Chocolatey installation (use if already installed)
    -Help              Show this help message

EXAMPLES:
    .\setup-openshift-prerequisites.ps1
    .\setup-openshift-prerequisites.ps1 -SkipChocolatey

REQUIREMENTS:
    - Windows PowerShell 5.1+ or PowerShell Core 6+
    - Administrator privileges (for Chocolatey installation)
    - Internet connection

"@
}

if ($Help) {
    Show-Usage
    exit 0
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Chocolatey {
    if ($SkipChocolatey) {
        Write-Status "Skipping Chocolatey installation as requested"
        return
    }

    Write-Status "Checking for Chocolatey..."
    
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Success "Chocolatey is already installed"
        return
    }

    Write-Status "Installing Chocolatey package manager..."
    
    if (-not (Test-Administrator)) {
        Write-Error-Custom "Administrator privileges required for Chocolatey installation"
        Write-Warning "Please run this script as Administrator or use -SkipChocolatey"
        exit 1
    }

    try {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Success "Chocolatey installed successfully"
    }
    catch {
        Write-Error-Custom "Failed to install Chocolatey: $($_.Exception.Message)"
        Write-Warning "You can install tools manually or try again with administrator privileges"
        exit 1
    }
}

function Install-OpenShiftCLI {
    Write-Status "Checking for OpenShift CLI..."
    
    if (Get-Command oc -ErrorAction SilentlyContinue) {
        $version = oc version --client 2>$null
        Write-Success "OpenShift CLI is already installed: $version"
        return
    }

    Write-Status "Installing OpenShift CLI..."
    
    try {
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install openshift-cli -y
        }
        elseif (Get-Command winget -ErrorAction SilentlyContinue) {
            winget install RedHat.Openshift-CLI
        }
        else {
            Write-Warning "Package manager not found. Please install manually:"
            Write-Host "1. Download from: https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/windows/" -ForegroundColor Cyan
            Write-Host "2. Extract oc.exe to a directory in your PATH" -ForegroundColor Cyan
            return
        }
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        if (Get-Command oc -ErrorAction SilentlyContinue) {
            $version = oc version --client
            Write-Success "OpenShift CLI installed successfully: $version"
        } else {
            Write-Error-Custom "OpenShift CLI installation may have failed. Please restart PowerShell and try again."
        }
    }
    catch {
        Write-Error-Custom "Failed to install OpenShift CLI: $($_.Exception.Message)"
        Write-Warning "Please install manually from: https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/windows/"
    }
}

function Install-Kustomize {
    Write-Status "Checking for Kustomize..."
    
    if (Get-Command kustomize -ErrorAction SilentlyContinue) {
        $version = kustomize version --short 2>$null
        Write-Success "Kustomize is already installed: $version"
        return
    }

    Write-Status "Installing Kustomize..."
    
    try {
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            choco install kustomize -y
        }
        else {
            Write-Warning "Installing Kustomize manually..."
            
            # Download latest release
            $latestRelease = Invoke-RestMethod -Uri "https://api.github.com/repos/kubernetes-sigs/kustomize/releases/latest"
            $downloadUrl = ($latestRelease.assets | Where-Object { $_.name -like "*windows_amd64.tar.gz" }).browser_download_url
            
            if (-not $downloadUrl) {
                throw "Could not find Windows release for Kustomize"
            }
            
            $tempPath = "$env:TEMP\kustomize.tar.gz"
            $extractPath = "$env:TEMP\kustomize"
            
            Write-Status "Downloading Kustomize from $downloadUrl"
            Invoke-WebRequest -Uri $downloadUrl -OutFile $tempPath
            
            # Extract (requires tar, available in Windows 10+)
            if (Get-Command tar -ErrorAction SilentlyContinue) {
                tar -xzf $tempPath -C $env:TEMP
                
                # Move to a permanent location
                $installPath = "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps"
                Copy-Item "$env:TEMP\kustomize.exe" "$installPath\kustomize.exe" -Force
                
                Write-Success "Kustomize installed to $installPath"
            } else {
                Write-Warning "Please install manually:"
                Write-Host "1. Download from: https://github.com/kubernetes-sigs/kustomize/releases" -ForegroundColor Cyan
                Write-Host "2. Extract kustomize.exe to a directory in your PATH" -ForegroundColor Cyan
                return
            }
        }
        
        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        if (Get-Command kustomize -ErrorAction SilentlyContinue) {
            $version = kustomize version --short
            Write-Success "Kustomize installed successfully: $version"
        } else {
            Write-Error-Custom "Kustomize installation may have failed. Please restart PowerShell and try again."
        }
    }
    catch {
        Write-Error-Custom "Failed to install Kustomize: $($_.Exception.Message)"
        Write-Warning "Please install manually from: https://github.com/kubernetes-sigs/kustomize/releases"
    }
}

function Test-Docker {
    Write-Status "Checking Docker installation..."
    
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        try {
            $dockerVersion = docker --version
            Write-Success "Docker is available: $dockerVersion"
            
            # Test if Docker daemon is running
            docker info 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Docker daemon is running"
            } else {
                Write-Warning "Docker is installed but daemon is not running. Please start Docker Desktop."
            }
        }
        catch {
            Write-Warning "Docker is installed but not accessible. Please ensure Docker Desktop is running."
        }
    }
    else {
        Write-Warning "Docker is not installed. Please install Docker Desktop for Windows:"
        Write-Host "Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    }
}

function Show-NextSteps {
    Write-Status "`nSetup completed! Next steps:"
    Write-Host ""
    Write-Host "1. OPENSHIFT CLUSTER ACCESS:" -ForegroundColor Cyan
    Write-Host "   Login to your OpenShift cluster:" -ForegroundColor White
    Write-Host "   oc login --token=<your-token> --server=<cluster-api-url>" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. CONTAINER REGISTRY ACCESS:" -ForegroundColor Cyan
    Write-Host "   Login to your container registry:" -ForegroundColor White
    Write-Host "   docker login quay.io" -ForegroundColor Gray
    Write-Host "   # or" -ForegroundColor Gray
    Write-Host "   docker login" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. TEST CONFIGURATION:" -ForegroundColor Cyan
    Write-Host "   Validate your OpenShift setup:" -ForegroundColor White
    Write-Host "   .\scripts\deploy-openshift.ps1 -Environment dev -DryRun" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. DEPLOY APPLICATION:" -ForegroundColor Cyan
    Write-Host "   Deploy to development environment:" -ForegroundColor White
    Write-Host "   .\scripts\deploy-openshift.ps1 -Environment dev" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Need help setting up an OpenShift cluster? See OPENSHIFT_CLUSTER_SETUP.md" -ForegroundColor Yellow
    Write-Host ""
}

function Main {
    Write-Host "=== OpenShift Prerequisites Setup ===" -ForegroundColor Green
    Write-Host "Setting up prerequisites for AIBeniq OpenShift deployment..." -ForegroundColor White
    Write-Host ""
    
    Install-Chocolatey
    Install-OpenShiftCLI
    Install-Kustomize
    Test-Docker
    
    Write-Host ""
    Write-Host "=== Prerequisites Setup Complete ===" -ForegroundColor Green
    Show-NextSteps
}

# Run main function
try {
    Main
}
catch {
    Write-Error-Custom "Setup failed: $($_.Exception.Message)"
    exit 1
}
