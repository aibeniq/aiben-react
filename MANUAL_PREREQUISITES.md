# Manual Prerequisites Installation Guide

If the automated script doesn't work, follow these manual installation steps:

## 1. OpenShift CLI (oc)

### Direct Download Method

1. **Download**: Go to https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/windows/
2. **Extract**: Download `oc.tar.gz` and extract `oc.exe`
3. **Install**: Move `oc.exe` to a directory in your PATH (e.g., `C:\Windows\System32`)
4. **Verify**: Open new PowerShell and run `oc version`

### Alternative: winget (Windows 11)

```powershell
winget install RedHat.Openshift-CLI
```

## 2. Kustomize

### Direct Download Method

1. **Download**: Go to https://github.com/kubernetes-sigs/kustomize/releases
2. **Find**: Look for `kustomize_v*_windows_amd64.tar.gz`
3. **Extract**: Extract `kustomize.exe`
4. **Install**: Move to a directory in your PATH
5. **Verify**: Run `kustomize version`

### PowerShell Script Method

```powershell
# Create a tools directory
$toolsDir = "$env:USERPROFILE\Tools"
New-Item -ItemType Directory -Path $toolsDir -Force

# Download and extract kustomize
$latestUrl = "https://github.com/kubernetes-sigs/kustomize/releases/latest/download/kustomize_v5.0.0_windows_amd64.tar.gz"
$downloadPath = "$toolsDir\kustomize.tar.gz"

Invoke-WebRequest -Uri $latestUrl -OutFile $downloadPath
tar -xzf $downloadPath -C $toolsDir
Remove-Item $downloadPath

# Add to PATH (current session)
$env:Path += ";$toolsDir"

# Add to PATH permanently
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$toolsDir", "User")

# Verify
kustomize version
```

## 3. Docker Desktop

1. **Download**: https://www.docker.com/products/docker-desktop
2. **Install**: Run the installer
3. **Start**: Launch Docker Desktop
4. **Verify**: Run `docker --version` and `docker info`

## 4. Verification Script

Save this as `verify-prerequisites.ps1`:

```powershell
Write-Host "=== Prerequisites Verification ===" -ForegroundColor Green

# Check OpenShift CLI
try {
    $ocVersion = oc version --client 2>$null
    Write-Host "✓ OpenShift CLI: $ocVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ OpenShift CLI not found" -ForegroundColor Red
}

# Check Kustomize
try {
    $kustomizeVersion = kustomize version --short 2>$null
    Write-Host "✓ Kustomize: $kustomizeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Kustomize not found" -ForegroundColor Red
}

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker: $dockerVersion" -ForegroundColor Green

    docker info 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker daemon is running" -ForegroundColor Green
    } else {
        Write-Host "⚠ Docker installed but daemon not running" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Docker not found" -ForegroundColor Red
}

Write-Host "=== Verification Complete ===" -ForegroundColor Green
```

## Quick Links

- **OpenShift CLI**: https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/windows/
- **Kustomize**: https://github.com/kubernetes-sigs/kustomize/releases
- **Docker Desktop**: https://www.docker.com/products/docker-desktop

Once all tools are installed, proceed to cluster setup using `OPENSHIFT_CLUSTER_SETUP.md`.
