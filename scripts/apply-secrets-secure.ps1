<#!
.SYNOPSIS
  Securely injects secrets into OpenShift without reading from tracked files.
.DESCRIPTION
  Implements secure secret management as per OPENAI_API_KEY_EXTERNALIZATION_STEPS.md:
  - Never reads secrets from tracked files (.env)
  - Uses interactive prompts or secure environment variables
  - Generates secure defaults for placeholder values
  - Supports rotation without Git commits
.PARAMETER Interactive
  Prompt for secrets interactively (secure input)
.PARAMETER FromEnv
  Use secure environment variables (CI/CD mode)
.PARAMETER Restart
  Restart backend deployment after secret update
.PARAMETER Environment
  Target environment: development or production (default: production)
.EXAMPLE
  ./scripts/apply-secrets-secure.ps1 -Interactive -Restart
.EXAMPLE
  $env:OPENAI_API_KEY_SECURE = "sk-real-key"; ./scripts/apply-secrets-secure.ps1 -FromEnv -Restart
.NOTES
  Follows externalization best practices - never commits real secrets to Git.
#>
[CmdletBinding()]
param(
  [switch]$Interactive,
  [switch]$FromEnv,
  [switch]$Restart,
  [ValidateSet('development','production')]
  [string]$Environment = 'production'
)

function Write-Info($msg){ Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg){ Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg){ Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Success($msg){ Write-Host "[SUCCESS] $msg" -ForegroundColor Green }

function Generate-SecurePassword($length = 16) {
  return -join ((65..90) + (97..122) + (48..57) | Get-Random -Count $length | ForEach-Object {[char]$_})
}

function Generate-SecureKey($length = 48) {
  $bytes = New-Object byte[] $length
  [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
  return [Convert]::ToBase64String($bytes)
}

function Get-SecureInput($prompt, $default = $null) {
  if($default) {
    $choice = Read-Host "$prompt (press Enter for secure random)"
    if([string]::IsNullOrWhiteSpace($choice)) {
      return $default
    }
    return $choice
  } else {
    do {
      $secure = Read-Host $prompt -AsSecureString
      $plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure))
      if([string]::IsNullOrWhiteSpace($plain)) {
        Write-Warn "Value cannot be empty. Please try again."
      }
    } while([string]::IsNullOrWhiteSpace($plain))
    return $plain
  }
}

if(-not $Interactive -and -not $FromEnv) {
  Write-Err "Must specify either -Interactive or -FromEnv"
  Write-Host "Examples:"
  Write-Host "  Interactive: ./apply-secrets-secure.ps1 -Interactive -Restart"
  Write-Host "  CI/CD mode:  ./apply-secrets-secure.ps1 -FromEnv -Restart"
  exit 1
}

Write-Info "Secure secret injection for environment: $Environment"

# Collect secrets securely
if($Interactive) {
  Write-Info "Interactive mode: Enter secrets securely (input will be hidden)"
  
  $SECRET_KEY = Get-SecureInput "SECRET_KEY for $Environment" (Generate-SecureKey)
  $FIRST_SUPERUSER = Get-SecureInput "FIRST_SUPERUSER email" "admin@yourdomain.com"
  $FIRST_SUPERUSER_PASSWORD = Get-SecureInput "FIRST_SUPERUSER_PASSWORD" (Generate-SecurePassword)
  $POSTGRES_PASSWORD = Get-SecureInput "POSTGRES_PASSWORD" (Generate-SecurePassword)
  $OPENAI_API_KEY = Get-SecureInput "OPENAI_API_KEY (sk-...)"
  
  Write-Host "Optional secrets (press Enter to skip):"
  $REPLICATE_API_TOKEN = Get-SecureInput "REPLICATE_API_TOKEN (r8_...)" ""
  $AWS_ACCESS_KEY_ID = Get-SecureInput "AWS_ACCESS_KEY_ID" ""
  $AWS_SECRET_ACCESS_KEY = Get-SecureInput "AWS_SECRET_ACCESS_KEY" ""
  $SMTP_PASSWORD = Get-SecureInput "SMTP_PASSWORD" ""
  
} elseif($FromEnv) {
  Write-Info "Environment variable mode: Reading from secure env vars"
  
  $envSuffix = $Environment.ToUpper()
  $SECRET_KEY = [Environment]::GetEnvironmentVariable("SECRET_KEY_$envSuffix")
  if([string]::IsNullOrWhiteSpace($SECRET_KEY)) { $SECRET_KEY = Generate-SecureKey }
  
  $FIRST_SUPERUSER = [Environment]::GetEnvironmentVariable("FIRST_SUPERUSER_$envSuffix")
  if([string]::IsNullOrWhiteSpace($FIRST_SUPERUSER)) { $FIRST_SUPERUSER = "admin@yourdomain.com" }
  
  $FIRST_SUPERUSER_PASSWORD = [Environment]::GetEnvironmentVariable("FIRST_SUPERUSER_PASSWORD_$envSuffix")
  if([string]::IsNullOrWhiteSpace($FIRST_SUPERUSER_PASSWORD)) { $FIRST_SUPERUSER_PASSWORD = Generate-SecurePassword }
  
  $POSTGRES_PASSWORD = [Environment]::GetEnvironmentVariable("POSTGRES_PASSWORD_$envSuffix")
  if([string]::IsNullOrWhiteSpace($POSTGRES_PASSWORD)) { $POSTGRES_PASSWORD = Generate-SecurePassword }
  
  $OPENAI_API_KEY = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY_$envSuffix")
  
  $REPLICATE_API_TOKEN = [Environment]::GetEnvironmentVariable("REPLICATE_API_TOKEN_$envSuffix")
  if([string]::IsNullOrWhiteSpace($REPLICATE_API_TOKEN)) { $REPLICATE_API_TOKEN = "" }
  
  $AWS_ACCESS_KEY_ID = [Environment]::GetEnvironmentVariable("AWS_ACCESS_KEY_ID_$envSuffix")
  if([string]::IsNullOrWhiteSpace($AWS_ACCESS_KEY_ID)) { $AWS_ACCESS_KEY_ID = "" }
  
  $AWS_SECRET_ACCESS_KEY = [Environment]::GetEnvironmentVariable("AWS_SECRET_ACCESS_KEY_$envSuffix")
  if([string]::IsNullOrWhiteSpace($AWS_SECRET_ACCESS_KEY)) { $AWS_SECRET_ACCESS_KEY = "" }
  
  $SMTP_PASSWORD = [Environment]::GetEnvironmentVariable("SMTP_PASSWORD_$envSuffix")
  if([string]::IsNullOrWhiteSpace($SMTP_PASSWORD)) { $SMTP_PASSWORD = "" }
  
  if([string]::IsNullOrWhiteSpace($OPENAI_API_KEY)) {
    Write-Err "OPENAI_API_KEY_$envSuffix environment variable is required"
    exit 1
  }
}

# Validate required secrets
if(-not $OPENAI_API_KEY.StartsWith("sk-")) {
  Write-Err "OPENAI_API_KEY must start with 'sk-'"
  exit 1
}

Write-Info "Creating backend-secrets with secure values"
oc delete secret backend-secrets --ignore-not-found | Out-Null

$createArgs = @(
  'create','secret','generic','backend-secrets',
  "--from-literal=SECRET_KEY=$SECRET_KEY",
  "--from-literal=FIRST_SUPERUSER=$FIRST_SUPERUSER",
  "--from-literal=FIRST_SUPERUSER_PASSWORD=$FIRST_SUPERUSER_PASSWORD",
  "--from-literal=POSTGRES_PASSWORD=$POSTGRES_PASSWORD",
  "--from-literal=SMTP_HOST=smtp.gmail.com",
  "--from-literal=SMTP_USER=$FIRST_SUPERUSER",
  "--from-literal=SMTP_PASSWORD=$SMTP_PASSWORD",
  "--from-literal=EMAILS_FROM_EMAIL=noreply@yourdomain.com",
  "--from-literal=OPENAI_API_KEY=$OPENAI_API_KEY",
  "--from-literal=REPLICATE_API_TOKEN=$REPLICATE_API_TOKEN",
  "--from-literal=AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID",
  "--from-literal=AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY",
  "--from-literal=SENTRY_DSN="
)

try {
  & oc @createArgs | Out-Null
  Write-Success "backend-secrets created successfully"
} catch {
  Write-Err "Failed to create backend-secrets: $_"
  exit 1
}

Write-Info "Creating postgres-secret"
oc delete secret postgres-secret --ignore-not-found | Out-Null
oc create secret generic postgres-secret --from-literal=POSTGRES_PASSWORD=$POSTGRES_PASSWORD | Out-Null
Write-Success "postgres-secret created successfully"

if($Restart) {
  Write-Info "Restarting backend deployment"
  oc rollout restart deployment/backend | Out-Null
  Write-Info "Waiting for rollout to complete"
  oc rollout status deployment/backend
  Write-Success "Backend restarted with new secrets"
}

Write-Success "Secret injection completed for $Environment environment"
Write-Info "Verify with: oc exec deployment/backend -- env | findstr OPENAI_API_KEY"
Write-Warn "Remember: Real secrets were NOT saved to any tracked files"
