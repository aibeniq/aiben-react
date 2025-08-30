<#
pause-cluster.ps1

Purpose: temporarily scale down workloads in a namespace to reduce AWS EC2 costs overnight
Target cluster/namespace: defaults to 'aibeniq-prod2' (you can override)

Usage examples:
  # show current status
  .\pause-cluster.ps1 -Action status -Namespace aibeniq-dev

  # cleanup failed resources without pausing
  .\pause-cluster.ps1 -Action cleanup -Namespace aibeniq-dev

  # pause (save state + scale to zero + cleanup)
  .\pause-cluster.ps1 -Action pause -Namespace aibeniq-dev

  # resume (restore saved state)
  .\pause-cluster.ps1 -Action resume -Namespace aibeniq-dev

Options:
  -Action pause|resume|status|cleanup
  -Namespace   target namespace (default: aibeniq-dev)
  -StateFile   path to save state (default: ./pause-state-<namespace>.json)
  -ScaleWorkers switch; if provided and you have cluster-admin rights the script will scale "worker" machinesets to 0 (risky)
  -DryRun      show commands without executing
  -Force       skip confirmations
#>

param(
    [ValidateSet('pause','resume','status','cleanup')]
    [string]$Action = 'status',

    [string]$Namespace = 'aibeniq-dev',

    [string]$StateFile = "./pause-state-$([System.IO.Path]::GetFileNameWithoutExtension($Namespace)).json",

    [switch]$ScaleWorkers,
    [switch]$DryRun,
    [switch]$Force,
    [switch]$Help
)

function Show-Usage {
    Write-Host "Usage: .\pause-cluster.ps1 -Action pause|resume|status|cleanup [-Namespace name] [-StateFile path] [-ScaleWorkers] [-DryRun] [-Force]" -ForegroundColor Cyan
}

if ($Help) { Show-Usage ; exit 0 }

function Check-OCLoggedIn {
    try { Get-Command oc -ErrorAction Stop } catch { Write-Error "oc CLI not found; install and login first" ; exit 1 }
    oc whoami > $null 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Error "Not logged in to OpenShift. Run 'oc login' first." ; exit 1 }
}

function Save-StateToFile($state) {
    $json = $state | ConvertTo-Json -Depth 10
    if ($DryRun) { Write-Host "DRYRUN: would write state to $StateFile" ; return }
    Set-Content -Path $StateFile -Value $json -Force -Encoding UTF8
    Write-Host "Saved state to $StateFile" -ForegroundColor Green
}

function Load-StateFromFile() {
    if (-not (Test-Path $StateFile)) { Write-Error "State file not found: $StateFile" ; exit 1 }
    $raw = Get-Content $StateFile -Raw
    return $raw | ConvertFrom-Json
}

function Cleanup-FailedResources {
    param($ns)
    Write-Host "Cleaning up failed/completed resources in namespace: $ns" -ForegroundColor Cyan
    
    # Clean up failed pods
    Write-Host "Cleaning up failed pods..." -ForegroundColor Yellow
    if ($DryRun) {
        Write-Host "DRYRUN: would delete failed pods" -ForegroundColor Yellow
        oc get pods -n $ns --field-selector=status.phase=Failed
    } else {
        oc delete pods -n $ns --field-selector=status.phase=Failed 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Deleted failed pods" -ForegroundColor Green
        } else {
            Write-Host "No failed pods to delete" -ForegroundColor Gray
        }
    }

    # Clean up succeeded pods (from completed jobs)
    Write-Host "Cleaning up succeeded pods..." -ForegroundColor Yellow
    if ($DryRun) {
        Write-Host "DRYRUN: would delete succeeded pods" -ForegroundColor Yellow
        oc get pods -n $ns --field-selector=status.phase=Succeeded
    } else {
        oc delete pods -n $ns --field-selector=status.phase=Succeeded 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Deleted succeeded pods" -ForegroundColor Green
        } else {
            Write-Host "No succeeded pods to delete" -ForegroundColor Gray
        }
    }

    # Clean up completed builds
    Write-Host "Cleaning up completed builds..." -ForegroundColor Yellow
    if ($DryRun) {
        Write-Host "DRYRUN: would delete completed builds" -ForegroundColor Yellow
        oc get builds -n $ns --field-selector=status.phase=Complete
    } else {
        oc delete builds -n $ns --field-selector=status.phase=Complete 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Deleted completed builds" -ForegroundColor Green
        } else {
            Write-Host "No completed builds to delete" -ForegroundColor Gray
        }
    }

    # Clean up failed builds
    Write-Host "Cleaning up failed builds..." -ForegroundColor Yellow
    if ($DryRun) {
        Write-Host "DRYRUN: would delete failed builds" -ForegroundColor Yellow
        oc get builds -n $ns --field-selector=status.phase=Failed
    } else {
        oc delete builds -n $ns --field-selector=status.phase=Failed 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Deleted failed builds" -ForegroundColor Green
        } else {
            Write-Host "No failed builds to delete" -ForegroundColor Gray
        }
    }

    # Clean up old ReplicaSets with 0 replicas
    Write-Host "Cleaning up old ReplicaSets..." -ForegroundColor Yellow
    if ($DryRun) {
        Write-Host "DRYRUN: would check for old ReplicaSets" -ForegroundColor Yellow
        oc get rs -n $ns -o jsonpath='{range .items[?(@.spec.replicas==0)]}{.metadata.name}{"\n"}{end}'
    } else {
        $oldRS = oc get rs -n $ns -o jsonpath='{range .items[?(@.spec.replicas==0)]}{.metadata.name}{" "}{end}' 2>$null
        if ($oldRS -and $oldRS.Trim()) {
            $rsList = $oldRS.Trim().Split(" ")
            foreach ($rs in $rsList) {
                if ($rs) {
                    oc delete rs $rs -n $ns
                    Write-Host "Deleted ReplicaSet: $rs" -ForegroundColor Green
                }
            }
        } else {
            Write-Host "No old ReplicaSets to delete" -ForegroundColor Gray
        }
    }
}

function Pause-Workloads {
    param($ns)
    Write-Host "Pausing workloads in namespace: $ns" -ForegroundColor Cyan

    # First cleanup failed/completed resources
    Cleanup-FailedResources -ns $ns

    # gather deployments
    $deployJson = oc get deployment -n $ns -o json 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed to get deployments in $ns" ; exit 1 }
    $deploy = $deployJson | ConvertFrom-Json
    $deployState = @()
    foreach ($item in $deploy.items) {
        $rep = if ($null -ne $item.spec.replicas) { $item.spec.replicas } else { 1 }
        $deployState += [pscustomobject]@{ kind = 'Deployment'; name = $item.metadata.name; replicas = $rep }
    }

    # gather statefulsets
    $stsJson = oc get statefulset -n $ns -o json 2>$null
    $sts = $stsJson | ConvertFrom-Json
    $stsState = @()
    foreach ($item in $sts.items) {
        $rep = if ($null -ne $item.spec.replicas) { $item.spec.replicas } else { 1 }
        $stsState += [pscustomobject]@{ kind = 'StatefulSet'; name = $item.metadata.name; replicas = $rep }
    }

    # gather cronjobs suspend state
    $cjJson = oc get cronjob -n $ns -o json 2>$null
    $cjState = @()
    if ($cjJson) {
        $cjs = $cjJson | ConvertFrom-Json
        foreach ($item in $cjs.items) {
            $suspend = if ($null -ne $item.spec.suspend) { $item.spec.suspend } else { $false }
            $cjState += [pscustomobject]@{ name = $item.metadata.name; suspend = $suspend }
        }
    }

    # gather HPA minReplicas
    $hpaJson = oc get hpa -n $ns -o json 2>$null
    $hpaState = @()
    if ($hpaJson) {
        $hpas = $hpaJson | ConvertFrom-Json
        foreach ($item in $hpas.items) {
            $min = if ($null -ne $item.spec.minReplicas) { $item.spec.minReplicas } else { $null }
            $hpaState += [pscustomobject]@{ name = $item.metadata.name; minReplicas = $min }
        }
    }

    # Compose state object
    $state = [pscustomobject]@{
        namespace = $ns
        timestamp = (Get-Date).ToString('o')
        deployments = $deployState
        statefulsets = $stsState
        cronjobs = $cjState
        hpas = $hpaState
        machinesets = @()
    }

    # save state
    Save-StateToFile $state

    if ($DryRun) { Write-Host "DRYRUN: would scale deployments and statefulsets to 0 and suspend cronjobs/hpas" ; return }

    # scale deployments and statefulsets to 0
    Write-Host "Scaling deployments to 0..."
    oc scale deployment --replicas=0 --all -n $ns
    Write-Host "Scaling statefulsets to 0..."
    oc scale statefulset --replicas=0 --all -n $ns

    # suspend cronjobs
    foreach ($cj in $cjState) {
        if (-not $cj.suspend) {
            Write-Host "Suspending cronjob: $($cj.name)"
            oc patch cronjob $cj.name -n $ns -p '{"spec":{"suspend":true}}' --type=merge
        }
    }

    # set HPA minReplicas to 0 to avoid autoscale
    foreach ($h in $hpaState) {
        if ($h.minReplicas -ne $null -and $h.minReplicas -gt 0) {
            Write-Host "Patching HPA $($h.name) minReplicas -> 0"
            oc patch hpa $h.name -n $ns -p '{"spec":{"minReplicas":0}}' --type=merge
        }
    }

    Write-Host "Pausing complete. Pods will be terminated and stop consuming vCPU/EC2. Persistent volumes will still be billed." -ForegroundColor Yellow
}

function Check-ServiceEndpoints {
    param($ns)
    Write-Host "Checking service endpoints consistency..." -ForegroundColor Yellow
    
    $services = (oc get service -n $ns -o json | ConvertFrom-Json).items
    foreach ($svc in $services) {
        $endpoints = oc get endpoints $svc.metadata.name -n $ns -o jsonpath='{.subsets[*].addresses[*].ip}' 2>$null
        if (-not $endpoints -and $svc.spec.selector) {
            Write-Warning "Service '$($svc.metadata.name)' has no endpoints. Check if pod labels match service selector."
            Write-Host "Service selector:" -ForegroundColor Gray
            $svc.spec.selector | ConvertTo-Json -Compress | Write-Host -ForegroundColor Gray
        }
    }
}

function Resume-Workloads {
    param($ns)
    Write-Host "Resuming workloads in namespace: $ns" -ForegroundColor Cyan
    $state = Load-StateFromFile
    if ($state.namespace -ne $ns) { Write-Warning "State file namespace ($($state.namespace)) does not match requested namespace ($ns). Continuing..." }

    if ($DryRun) { Write-Host "DRYRUN: would restore deployments/statefulsets/crons/hpas from $StateFile" ; return }

    foreach ($d in $state.deployments) {
        Write-Host "Restoring deployment $($d.name) -> replicas $($d.replicas)"
        oc scale deployment/$($d.name) --replicas=$($d.replicas) -n $ns
    }
    foreach ($s in $state.statefulsets) {
        Write-Host "Restoring statefulset $($s.name) -> replicas $($s.replicas)"
        oc scale statefulset/$($s.name) --replicas=$($s.replicas) -n $ns
    }

    # restore cronjobs
    foreach ($cj in $state.cronjobs) {
        if ($cj.suspend) {
            Write-Host "Cronjob $($cj.name) was suspended before; leaving suspended"
        } else {
            Write-Host "Unsuspending cronjob: $($cj.name)"
            oc patch cronjob $($cj.name) -n $ns -p '{"spec":{"suspend":false}}' --type=merge
        }
    }

    # restore HPAs
    foreach ($h in $state.hpas) {
        if ($h.minReplicas -ne $null) {
            Write-Host "Restoring HPA $($h.name) minReplicas -> $($h.minReplicas)"
            # construct patch JSON safely to avoid quoting problems
            $patchObj = @{ spec = @{ minReplicas = [int]$h.minReplicas } }
            $patchJson = $patchObj | ConvertTo-Json -Compress
            oc patch hpa $($h.name) -n $ns -p $patchJson --type=merge
        }
    }

    # 🚀 NEW: Apply environment-specific configuration after resume
    Apply-EnvironmentConfig -ns $ns

    Write-Host "Resume requested. Some pods may take time to become Ready." -ForegroundColor Green
    
    # Check for service endpoint issues that might prevent pods from starting
    Start-Sleep -Seconds 5
    Check-ServiceEndpoints $ns
}

function Show-Status {
    param($ns)
    Write-Host "Status for namespace: $ns" -ForegroundColor Cyan
    oc get pods -n $ns
    oc get deployment,statefulset -n $ns
    if (Test-Path $StateFile) { Write-Host "Saved state file: $StateFile" -ForegroundColor Yellow }
    else { Write-Host "No saved state file found at: $StateFile" -ForegroundColor Green }
    if ($ScaleWorkers) {
        Write-Host "Machinesets (worker*) in openshift-machine-api:" -ForegroundColor Cyan
        oc get machinesets -n openshift-machine-api | Select-String -Pattern 'worker' -SimpleMatch
    }
}

function Scale-Workers-ToZero {
    Write-Host "Scaling worker machinesets to 0 (only machinesets with 'worker' in their name will be touched)" -ForegroundColor Yellow
    $msJson = oc get machinesets -n openshift-machine-api -o json 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed to list machinesets; need cluster-admin rights" ; exit 1 }
    $ms = $msJson | ConvertFrom-Json
    $msState = @()
    foreach ($m in $ms.items) {
        if ($m.metadata.name -match 'worker') {
            $rep = if ($null -ne $m.spec.replicas) { $m.spec.replicas } else { 0 }
            $msState += [pscustomobject]@{ name = $m.metadata.name; replicas = $rep }
        }
    }
    if ($msState.Count -eq 0) { Write-Host "No worker machinesets detected (no name match 'worker'). Skipping." ; return }

    # save machineset info into state file
    if (-not (Test-Path $StateFile)) {
        $state = [pscustomobject]@{ namespace = $Namespace; timestamp = (Get-Date).ToString('o'); machinesets = $msState }
        Save-StateToFile $state
    } else {
        $state = Load-StateFromFile
        $state.machinesets = $msState
        Save-StateToFile $state
    }

    foreach ($m in $msState) {
        Write-Host "Scaling machineset $($m.name) -> 0"
        if (-not $DryRun) { oc scale machineset/$($m.name) --replicas=0 -n openshift-machine-api }
    }
    Write-Host "Machineset scaling requested. Nodes will be terminated in AWS; control plane still billed." -ForegroundColor Yellow
}

# Main
if ($Action -eq 'status') { Check-OCLoggedIn ; Show-Status -ns $Namespace ; exit 0 }

if ($Action -eq 'cleanup') {
    Check-OCLoggedIn
    if (-not $Force) {
        Write-Host "About to cleanup failed/completed resources in namespace: $Namespace" -ForegroundColor Yellow
        $confirm = Read-Host "Proceed? (y/N)"
        if ($confirm -ne 'y' -and $confirm -ne 'Y') { Write-Host "Aborted by user." ; exit 0 }
    }
    Cleanup-FailedResources -ns $Namespace
    exit 0
}

if ($Action -eq 'pause') {
    Check-OCLoggedIn
    if (-not $Force) {
        Write-Host "About to save current replica counts and scale workloads to zero in namespace: $Namespace" -ForegroundColor Yellow
        $confirm = Read-Host "Proceed? (y/N)"
        if ($confirm -ne 'y' -and $confirm -ne 'Y') { Write-Host "Aborted by user." ; exit 0 }
    }
    Pause-Workloads -ns $Namespace
    if ($ScaleWorkers) { Scale-Workers-ToZero }
    exit 0
}

if ($Action -eq 'resume') {
    Check-OCLoggedIn
    if (-not (Test-Path $StateFile)) { Write-Error "State file not found: $StateFile" ; exit 1 }
    Resume-Workloads -ns $Namespace
    # resume machinesets if present in state
    $s = Load-StateFromFile
    if ($s.machinesets -and $s.machinesets.Count -gt 0) {
        foreach ($m in $s.machinesets) {
            Write-Host "Restoring machineset $($m.name) -> replicas $($m.replicas)"
            if (-not $DryRun) { oc scale machineset/$($m.name) --replicas=$($m.replicas) -n openshift-machine-api }
        }
    }
    exit 0
}

# Enhanced environment-aware functions
function Apply-EnvironmentConfig {
    param($ns)
    
    # Determine environment from namespace
    $environment = if ($ns -like "*dev*") { "dev" } elseif ($ns -like "*prod*") { "prod" } else { "dev" }
    
    Write-Host "Applying $environment environment configuration to namespace: $ns" -ForegroundColor Cyan
    
    if (-not $DryRun) {
        # Use the deployment script to apply proper environment config
        if (Test-Path ".\scripts\deploy-openshift.ps1") {
            Write-Host "Running deployment script to restore environment configuration..."
            & ".\scripts\deploy-openshift.ps1" -Environment $environment -SkipSecrets
        } else {
            Write-Warning "deploy-openshift.ps1 not found. Applying basic configuration manually..."
            
            if ($environment -eq "dev") {
                # Development: HTTP URLs
                oc patch configmap frontend-config -n $ns -p '{"data":{"VITE_API_URL":"http://redhat-api.aiben.io"}}' 2>$null
                oc patch configmap backend-config -n $ns -p '{"data":{"FRONTEND_HOST":"http://redhat.aiben.io","BACKEND_CORS_ORIGINS":"http://localhost,http://localhost:5173,http://redhat.aiben.io"}}' 2>$null
            } else {
                # Production: HTTPS URLs
                oc patch configmap frontend-config -n $ns -p '{"data":{"VITE_API_URL":"https://redhat-api.aiben.io"}}' 2>$null
                oc patch configmap backend-config -n $ns -p '{"data":{"FRONTEND_HOST":"https://redhat.aiben.io","BACKEND_CORS_ORIGINS":"https://redhat.aiben.io,https://redhat-api.aiben.io,http://redhat.aiben.io,http://redhat-api.aiben.io,http://localhost:5173"}}' 2>$null
            }
            
            # Restart deployments to pick up config changes
            oc rollout restart deployment/frontend deployment/backend -n $ns 2>$null
        }
    }
}

Write-Host "Unknown action: $Action" ; Show-Usage ; exit 1
