<#
.SYNOPSIS
  Verify Postgres PVC persistence & optionally recycle deployment + take logical backup.

.PARAMETER Namespace
  Kubernetes/OpenShift namespace (project) containing the Postgres deployment.

.PARAMETER Deployment
  Name of the Postgres Deployment (default: postgres).

.PARAMETER Pvc
  Name of the PersistentVolumeClaim (default: postgres-pvc).

.PARAMETER DbUser
  Database user for connectivity tests (default: app).

.PARAMETER DbName
  Database name for connectivity tests (default: app).

.PARAMETER LabelSelector
  Override pod label selector (default: app=aibeniq,component=database).

.PARAMETER Recycle
  Scale deployment to 0, wait, scale back to 1 to prove persistence across restart.

.PARAMETER Dump
  Perform logical pg_dump and copy dump locally.

.PARAMETER DumpOutDir
  Local directory to store dump (default: current dir).

.EXAMPLE
  ./verify-postgres-pvc.ps1 -Namespace aibeniq-prod -Recycle -Dump

.NOTES
  Requires oc CLI logged in & exec permission in pod.
#>
param(
  [string]$Namespace = 'aibeniq-prod',
  [string]$Deployment = 'postgres',
  [string]$Pvc = 'postgres-pvc',
  [string]$DbUser = 'app',
  [string]$DbName = 'app',
  [string]$LabelSelector = 'app=aibeniq,component=database',
  [switch]$Recycle,
  [switch]$Dump,
  [string]$DumpOutDir = '.'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info    { param([string]$m) ; Write-Host "[INFO ] $m" -ForegroundColor Cyan }
function Write-OK      { param([string]$m) ; Write-Host "[ OK  ] $m" -ForegroundColor Green }
function Write-Warn    { param([string]$m) ; Write-Host "[WARN ] $m" -ForegroundColor Yellow }
function Write-Err     { param([string]$m) ; Write-Host "[FAIL ] $m" -ForegroundColor Red }

function Exec-OrFail {
  param([string]$Cmd,[string]$ErrMsg)
  Write-Info $Cmd
  Invoke-Expression $Cmd | Out-String | ForEach-Object { if ($_ -ne '') { Write-Host $_ } }
  if ($LASTEXITCODE -ne 0) { throw $ErrMsg }
}

function Require-Binary {
  param([string]$Name)
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) { throw "Required command '$Name' not found" }
}

try {
  $start = Get-Date
  Write-Info "Verifying prerequisites"
  Require-Binary oc
  oc whoami > $null 2>&1 || throw 'Not logged in (oc whoami failed)'
  Write-OK "oc present & logged in"

  Write-Info "Gather PVC state"
  $pvcJson = oc get pvc $Pvc -n $Namespace -o json | ConvertFrom-Json
  $status = $pvcJson.status.phase
  $volName = $pvcJson.spec.volumeName
  $capacity = $pvcJson.status.capacity.storage
  Write-OK "PVC $Pvc status=$status volume=$volName capacity=$capacity"
  if ($status -ne 'Bound') { throw "PVC $Pvc not Bound" }

  function Get-PostgresPod {
    $pod = oc get pods -n $Namespace -l $LabelSelector -o jsonpath='{.items[0].metadata.name}' 2>$null
    if (-not $pod) { return $null } else { return $pod }
  }

  $prePod = Get-PostgresPod
  if ($prePod) { Write-OK "Current pod: $prePod" } else { Write-Warn "No running pod matches selector ($LabelSelector) yet" }

  if ($Recycle) {
    Write-Info "Recycling deployment $Deployment"
    Exec-OrFail "oc scale deployment/$Deployment --replicas=0 -n $Namespace" "Failed to scale down"
    Write-Info "Waiting for pods to terminate"
    oc wait --for=delete pod -l $LabelSelector -n $Namespace --timeout=120s 2>$null | Out-Null
    Write-OK "Scaled down"
    Exec-OrFail "oc scale deployment/$Deployment --replicas=1 -n $Namespace" "Failed to scale up"
    Exec-OrFail "oc rollout status deployment/$Deployment -n $Namespace --timeout=180s" "Rollout failed"
  } elseif (-not $prePod) {
    Write-Info "No pod found; scaling deployment to 1"
    Exec-OrFail "oc scale deployment/$Deployment --replicas=1 -n $Namespace" "Failed to scale up"
    Exec-OrFail "oc rollout status deployment/$Deployment -n $Namespace --timeout=180s" "Rollout failed"
  }

  $pod = Get-PostgresPod
  if (-not $pod) { throw 'Pod not found after (re)start' }
  Write-OK "Active pod: $pod"

  Write-Info "Checking pg_isready"
  Exec-OrFail "oc exec $pod -n $Namespace -- pg_isready -U $DbUser -d $DbName" "pg_isready failed"

  Write-Info "Collecting data directory size"
  $size = oc exec $pod -n $Namespace -- sh -c "du -sh /var/lib/postgresql/data/pgdata 2>/dev/null | cut -f1" | Select-Object -First 1
  Write-OK "Data directory size: $size"

  Write-Info "Counting user tables"
  $tableCount = oc exec $pod -n $Namespace -- psql -U $DbUser -d $DbName -t -A -c "SELECT count(*) FROM pg_catalog.pg_tables WHERE schemaname NOT IN ('pg_catalog','information_schema');" 2>$null
  $tableCount = $tableCount.Trim()
  Write-OK "User tables: $tableCount"

  if ($Dump) {
    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $remoteDump="/tmp/${DbName}_dump_${stamp}.sql"
    $localDir = Resolve-Path $DumpOutDir
    $localDump = Join-Path $localDir.Path ("${DbName}_dump_${stamp}.sql")
    Write-Info "Creating logical dump $remoteDump"
    Exec-OrFail "oc exec $pod -n $Namespace -- pg_dump -U $DbUser -d $DbName > \"$localDump\"" "pg_dump failed"
    Write-OK "Dump saved locally: $localDump"
  }

  Write-Info "Re-check PVC bound to same volume"
  $pvcJson2 = oc get pvc $Pvc -n $Namespace -o json | ConvertFrom-Json
  $volName2 = $pvcJson2.spec.volumeName
  if ($volName2 -ne $volName) { Write-Warn "PVC volume changed: was $volName now $volName2" } else { Write-OK "PVC volume unchanged ($volName2)" }

  $elapsed = (Get-Date) - $start
  Write-OK "Verification complete in {0:N1}s" -f $elapsed.TotalSeconds
  Write-Host "Summary: PVC=$Pvc Bound, Pod=$pod, Size=$size, Tables=$tableCount" -ForegroundColor Green
  exit 0
}
catch {
  Write-Err $_.Exception.Message
  exit 1
}
