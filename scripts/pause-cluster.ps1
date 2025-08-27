<#
pause-cluster.ps1

Purpose: temporarily scale down workloads in a namespace to reduce AWS EC2 costs overnight
Target cluster/namespace: defaults to 'aibeniq-prod2' (you can override)

Usage examples:
  # show current status
  .\pause-cluster.ps1 -Action status -Namespace aibeniq-prod2

  # pause (save state + scale to zero)
  .\pause-cluster.ps1 -Action pause -Namespace aibeniq-prod2

  # resume (restore saved state)
  .\pause-cluster.ps1 -Action resume -Namespace aibeniq-prod2

Options:
  -Action pause|resume|status
  -Namespace   target namespace (default: aibeniq-prod2)
  -StateFile   path to save state (default: ./pause-state-<namespace>.json)
  -ScaleWorkers switch; if provided and you have cluster-admin rights the script will scale "worker" machinesets to 0 (risky)
  -DryRun      show commands without executing
  -Force       skip confirmations
#>

param(
    [ValidateSet('pause','resume','status')]
    [string]$Action = 'status',

    [string]$Namespace = 'aibeniq-prod2',

    [string]$StateFile = "./pause-state-$([System.IO.Path]::GetFileNameWithoutExtension($Namespace)).json",

    [switch]$ScaleWorkers,
    [switch]$DryRun,
    [switch]$Force,
    [switch]$Help
)

function Show-Usage {
    Write-Host "Usage: .\pause-cluster.ps1 -Action pause|resume|status [-Namespace name] [-StateFile path] [-ScaleWorkers] [-DryRun] [-Force]" -ForegroundColor Cyan
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

function Pause-Workloads {
    param($ns)
    Write-Host "Pausing workloads in namespace: $ns" -ForegroundColor Cyan

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

    Write-Host "Resume requested. Some pods may take time to become Ready." -ForegroundColor Green
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

Write-Host "Unknown action: $Action" ; Show-Usage ; exit 1
