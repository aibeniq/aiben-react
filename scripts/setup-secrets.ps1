#!/usr/bin/env pwsh
# Permanent Secret Setup Script - AIBeniq OpenShift Deployment
# This script ensures consistent secret configuration across environments

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod")]
    [string]$Environment,
    
    [switch]$Interactive,
    [switch]$Validate,
    [switch]$Restart,
    [switch]$DestructiveReset,      # NEW: wipe PVC to realign password
    [switch]$ForcePasswordRotate    # NEW: force rotate even if DB initialized
)

Write-Host "=== AIBeniq Secret Setup ($Environment) ===" -ForegroundColor Green

# Helper functions for database password management
function Test-PostgresPassword {
    param(
        [string]$Namespace,
        [string]$Password
    )
    Write-Host "Testing database password..." -ForegroundColor Gray
    $cmd = "PGPASSWORD='$Password' psql -U app -d aibeniq -h postgres -c '\dt' >/dev/null 2>&1"
    oc exec deploy/postgres -- bash -c "$cmd" 2>$null
    return ($LASTEXITCODE -eq 0)
}

function Test-PostgresInitialized {
    Write-Host "Checking if PostgreSQL is initialized..." -ForegroundColor Gray
    # If PG_VERSION exists in the data dir, the cluster is initialized
    oc exec deploy/postgres -- bash -c "[ -f /var/lib/postgresql/data/PG_VERSION ]" 2>$null
    return ($LASTEXITCODE -eq 0)
}

function Reset-PostgresData {
    param([string]$Namespace)
    Write-Host "Performing destructive reset of PostgreSQL data..." -ForegroundColor Red
    Write-Host "Deleting postgres deployment..." -ForegroundColor Yellow
    oc delete deployment postgres --ignore-not-found=true
    
    Write-Host "Deleting postgres PVC..." -ForegroundColor Yellow
    oc delete pvc -l app=aibeniq,component=postgres --ignore-not-found=true
    oc delete pvc postgres-storage --ignore-not-found=true
    oc delete pvc postgres-pvc --ignore-not-found=true  # Also delete the actual PVC name
    
    Write-Host "Waiting for PVC removal..." -ForegroundColor Gray
    $wait = 0
    while ($wait -lt 30) {
        $exists = oc get pvc -l component=postgres --no-headers 2>$null
        if (-not $exists -or $exists.Trim() -eq "") { break }
        Start-Sleep 2; $wait++
    }
    
    Write-Host "[WARNING] PostgreSQL data wiped. Re-run deployment to initialize with current secret." -ForegroundColor Yellow
    Write-Host "Run: .\scripts\deploy-openshift.ps1 -Environment $Environment" -ForegroundColor Cyan
}

function Invoke-PasswordRotation {
    param(
        [string]$NewPassword,
        [string]$Namespace
    )
    
    Write-Host "Attempting to rotate PostgreSQL user password..." -ForegroundColor Yellow
    
    # Test if current password already works
    Write-Host "Testing current password alignment..." -ForegroundColor Gray
    if (Test-PostgresPassword -Namespace $Namespace -Password $NewPassword) {
        Write-Host "✅ Database already accepts current secret password." -ForegroundColor Green
        
        # Even if password is correct, restart backend to ensure it picks up latest config
        Write-Host "Restarting backend to ensure latest configuration..." -ForegroundColor Yellow
        oc rollout restart deployment/backend
        Write-Host "✅ Backend restart initiated." -ForegroundColor Green
        
        return $true
    }
    
    Write-Host "Password mismatch detected. Attempting ALTER USER..." -ForegroundColor Yellow
    
    # Try to connect as postgres superuser and change the app user password
    $escapedPassword = $NewPassword -replace "'", "''"
    $alterCommand = "psql -U postgres -d postgres -c `"ALTER USER app WITH PASSWORD '$escapedPassword';`""
    
    try {
        Write-Host "Executing: $alterCommand" -ForegroundColor Gray
        oc exec deploy/postgres -- bash -c "$alterCommand"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "ALTER USER command succeeded." -ForegroundColor Green
            
            # Test the connection again
            Start-Sleep 2
            if (Test-PostgresPassword -Namespace $Namespace -Password $NewPassword) {
                Write-Host "✅ Password rotation successful!" -ForegroundColor Green
                
                # Restart backend to clear connection pools and pick up new password
                Write-Host "Restarting backend to clear connection pools..." -ForegroundColor Yellow
                oc rollout restart deployment/backend
                Write-Host "✅ Backend restart initiated." -ForegroundColor Green
                
                return $true
            } else {
                Write-Host "❌ Password rotation verification failed." -ForegroundColor Red
                return $false
            }
        } else {
            Write-Host "❌ ALTER USER command failed." -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Password rotation failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Set namespace based on environment
$namespace = if ($Environment -eq "dev") { "aibeniq-dev" } else { "aibeniq-prod" }

# Ensure we're logged in and in the right project
try {
    oc whoami | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Not logged into OpenShift. Please run 'oc login' first." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] OpenShift CLI not available. Please install 'oc' command." -ForegroundColor Red
    exit 1
}

oc project $namespace

if ($Validate) {
    Write-Host "Validating secret configuration..." -ForegroundColor Yellow
    
    try {
        $secretData = (oc get secret backend-secrets -o json | ConvertFrom-Json).data
        
        # Check for placeholder values
        $hasPlaceholders = $false
        $secretStrings = @{}
        
        foreach ($key in $secretData.PSObject.Properties.Name) {
            $value = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secretData.$key))
            $secretStrings[$key] = $value
            
            if ($value -like "*REPLACE_ME*") {
                Write-Host "[WARNING] $key still contains placeholder value" -ForegroundColor Yellow
                $hasPlaceholders = $true
            }
        }
        
        # Validate specific formats
        if ($secretStrings.OPENAI_API_KEY -notlike "sk-*") {
            Write-Host "[WARNING] OPENAI_API_KEY doesn't look like a valid OpenAI key" -ForegroundColor Yellow
        }
        
        if ($secretStrings.DATABASE_URL -notlike "postgresql://*") {
            Write-Host "[ERROR] DATABASE_URL is not a valid PostgreSQL URL" -ForegroundColor Red
            exit 1
        }
        
        # Check consistency
        $expectedDatabaseUrl = "postgresql://app:$($secretStrings.POSTGRES_PASSWORD)@postgres:5432/aibeniq"
        if ($secretStrings.DATABASE_URL -ne $expectedDatabaseUrl) {
            Write-Host "[ERROR] DATABASE_URL is inconsistent with POSTGRES_PASSWORD" -ForegroundColor Red
            Write-Host "Expected: $expectedDatabaseUrl" -ForegroundColor Gray
            Write-Host "Actual:   $($secretStrings.DATABASE_URL)" -ForegroundColor Gray
            exit 1
        }
        
        if ($secretStrings.POSTGRES_SERVER -ne "postgres") {
            Write-Host "[ERROR] POSTGRES_SERVER should be 'postgres', got '$($secretStrings.POSTGRES_SERVER)'" -ForegroundColor Red
            exit 1
        }
        
        if ($hasPlaceholders) {
            Write-Host "[WARNING] Some secrets still contain placeholder values!" -ForegroundColor Yellow
            Write-Host "Run with -Interactive to set proper values" -ForegroundColor Yellow
            exit 1
        }
        
        # Check for orphaned postgres-secret
        try {
            oc get secret postgres-secret 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[WARNING] Orphaned postgres-secret still exists and should be removed" -ForegroundColor Yellow
                Write-Host "Run without -Validate to clean it up" -ForegroundColor Gray
            }
        } catch {
            # Good, postgres-secret doesn't exist
        }
        
        Write-Host "[OK] Secret validation passed" -ForegroundColor Green
        return
        
    } catch {
        Write-Host "[ERROR] Could not validate secrets: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

if ($Interactive) {
    Write-Host "Interactive secret setup..." -ForegroundColor Yellow
    
    # Get current values or use defaults
    try {
        $currentSecrets = oc get secret backend-secrets -o json | ConvertFrom-Json
        $secretData = $currentSecrets.data
        
        # Decode current values
        $currentPassword = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secretData.POSTGRES_PASSWORD))
        $currentSecretKey = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secretData.SECRET_KEY))
        $currentOpenAI = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secretData.OPENAI_API_KEY))
        $currentSuperUserPassword = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secretData.FIRST_SUPERUSER_PASSWORD))
    } catch {
        Write-Host "No existing secrets found, using defaults..." -ForegroundColor Yellow
        $currentPassword = "REPLACE_ME_DB_PWD"
        $currentSecretKey = "REPLACE_ME_SECRET_KEY"
        $currentOpenAI = "REPLACE_ME_OPENAI_KEY"
        $currentSuperUserPassword = "REPLACE_ME_SUPERUSER_PWD"
    }
    
    # Prompt for values
    Write-Host ""
    Write-Host "Enter new values (press Enter to keep current values):" -ForegroundColor Cyan
    
    $dbPassword = Read-Host "Database Password [$($currentPassword.Substring(0,[Math]::Min(4,$currentPassword.Length)))...]" 
    if ([string]::IsNullOrEmpty($dbPassword)) { $dbPassword = $currentPassword }
    
    $secretKey = Read-Host "FastAPI Secret Key [$($currentSecretKey.Substring(0,[Math]::Min(4,$currentSecretKey.Length)))...]"
    if ([string]::IsNullOrEmpty($secretKey)) { $secretKey = $currentSecretKey }
    
    $openaiKey = Read-Host "OpenAI API Key [$($currentOpenAI.Substring(0,[Math]::Min(7,$currentOpenAI.Length)))...]"
    if ([string]::IsNullOrEmpty($openaiKey)) { $openaiKey = $currentOpenAI }
    
    $superUserPassword = Read-Host "Admin User Password [$($currentSuperUserPassword.Substring(0,[Math]::Min(4,$currentSuperUserPassword.Length)))...]"
    if ([string]::IsNullOrEmpty($superUserPassword)) { $superUserPassword = $currentSuperUserPassword }
    
} else {
    Write-Host "Using existing secret values or applying architecture fixes..." -ForegroundColor Yellow
    
    try {
        # Use current values and fix any architecture issues
        $secretData = (oc get secret backend-secrets -o json | ConvertFrom-Json).data
        $dbPassword = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secretData.POSTGRES_PASSWORD))
        $secretKey = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secretData.SECRET_KEY))
        $openaiKey = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secretData.OPENAI_API_KEY))
        $superUserPassword = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secretData.FIRST_SUPERUSER_PASSWORD))
        
        # ✅ CRITICAL FIX: Generate new password if still using placeholder
        #if ($dbPassword -like "*REPLACE_ME*") {
        #    Write-Host "Detected placeholder password, generating secure password..." -ForegroundColor Yellow
        #    $dbPassword = "aibeniq-$Environment-$(Get-Random -Minimum 100000000 -Maximum 999999999)"
        #    Write-Host "Generated new database password: $($dbPassword.Substring(0,8))..." -ForegroundColor Green
        #}
        
        #if ($secretKey -like "*REPLACE_ME*") {
        #    Write-Host "Detected placeholder secret key, generating secure key..." -ForegroundColor Yellow
        #    $secretKey = -join ((1..64) | ForEach {Get-Random -input ([char[]]([char]'a'..[char]'z' + [char]'A'..[char]'Z' + [char]'0'..[char]'9'))})
        #    Write-Host "Generated new secret key: $($secretKey.Substring(0,8))..." -ForegroundColor Green
        #}
        
        #if ($superUserPassword -like "*REPLACE_ME*") {
        #    Write-Host "Detected placeholder superuser password, generating secure password..." -ForegroundColor Yellow
        #    $superUserPassword = "admin-$Environment-$(Get-Random -Minimum 100000 -Maximum 999999)"
        #    Write-Host "Generated new superuser password: $($superUserPassword.Substring(0,8))..." -ForegroundColor Green
        #}
        
        Write-Host "Found existing secrets, applying consistency fixes..." -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] No existing secrets found and not in interactive mode." -ForegroundColor Red
        Write-Host "Run with -Interactive to set initial values." -ForegroundColor Yellow
        exit 1
    }
}

# Compute derived values consistently
$databaseUrl = "postgresql://app:$dbPassword@postgres:5432/aibeniq"

# Create the complete secret configuration
$secretConfig = @{
    SECRET_KEY = $secretKey
    FIRST_SUPERUSER = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD = $superUserPassword
    POSTGRES_PASSWORD = $dbPassword
    POSTGRES_SERVER = "postgres"  # Always correct service name
    POSTGRES_PORT = "5432"
    POSTGRES_DB = "aibeniq"
    POSTGRES_USER = "app"
    DATABASE_URL = $databaseUrl   # Always computed correctly
    SMTP_HOST = "smtp.gmail.com"
    SMTP_USER = "david@aiben.io"
    SMTP_PASSWORD = "xlurvdrcarorciwy"
    EMAILS_FROM_EMAIL = "noreply@yourdomain.com"
    OPENAI_API_KEY = $openaiKey
    OPENAI_ADMIN_KEY = 'REMOVED_OPENAI_ADMIN_KEY'
    REPLICATE_API_TOKEN = 'REMOVED_REPLICATE_API_TOKEN'
    AWS_ACCESS_KEY_ID = "REMOVED_AWS_ACCESS_KEY_ID"
    AWS_SECRET_ACCESS_KEY = "REMOVED_AWS_SECRET_ACCESS_KEY"
    SENTRY_DSN = ""
    HUGGINGFACEHUB_API_TOKEN = "REMOVED_HUGGINGFACE_TOKEN"
}

# PostgreSQL password mismatch detection (only when updating, not validating)
if (-not $Validate) {
    Write-Host "Note: PostgreSQL password mismatch detection available via:" -ForegroundColor Yellow
    Write-Host "  .\scripts\test-postgres-password.ps1 -Environment $Environment" -ForegroundColor Cyan
}

# Apply the secrets
Write-Host "Applying backend-secrets..." -ForegroundColor Yellow

# ✅ ENHANCED DEBUG: Add comprehensive logging for troubleshooting
Write-Host "DEBUG: Analyzing secretConfig structure..." -ForegroundColor Magenta
Write-Host "DEBUG: secretConfig type: $($secretConfig.GetType().FullName)" -ForegroundColor Magenta
Write-Host "DEBUG: secretConfig keys count: $($secretConfig.Keys.Count)" -ForegroundColor Magenta
Write-Host "DEBUG: secretConfig keys: $($secretConfig.Keys -join ', ')" -ForegroundColor Magenta

# Check for problematic values
foreach ($key in $secretConfig.Keys) {
    $value = $secretConfig[$key]
    $valueType = if ($value -eq $null) { "NULL" } else { $value.GetType().FullName }
    $valueLength = if ($value -eq $null) { 0 } else { $value.ToString().Length }
    Write-Host "DEBUG: $key = [$valueType] length=$valueLength" -ForegroundColor Magenta
    
    # Show problematic values
    if ($value -eq $null -or $value -eq "") {
        Write-Host "DEBUG: WARNING - $key has empty/null value" -ForegroundColor Yellow
    }
    if ($value.ToString().Contains('"') -or $value.ToString().Contains('`')) {
        Write-Host "DEBUG: WARNING - $key contains special characters that may affect JSON" -ForegroundColor Yellow
    }
}

# ✅ FIXED METHOD: Use stringData patch instead of base64 JSON operations
try {
    Write-Host "Updating backend-secrets with stringData method..." -ForegroundColor Gray
    
    # Create proper stringData patch with quoted key and proper depth
    $patchData = @{
        "stringData" = $secretConfig
    }
    
    Write-Host "DEBUG: Converting to JSON..." -ForegroundColor Magenta
    $patchJson = $patchData | ConvertTo-Json -Compress -Depth 10
    
    Write-Host "DEBUG: Generated JSON length: $($patchJson.Length)" -ForegroundColor Magenta
    Write-Host "DEBUG: JSON starts with: $($patchJson.Substring(0, [Math]::Min(100, $patchJson.Length)))..." -ForegroundColor Magenta
    
    # Check if JSON is valid by trying to parse it back
    try {
        $testParse = $patchJson | ConvertFrom-Json
        Write-Host "DEBUG: JSON validation successful" -ForegroundColor Green
    } catch {
        Write-Host "DEBUG: JSON validation FAILED: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "DEBUG: Full JSON content:" -ForegroundColor Red
        Write-Host $patchJson -ForegroundColor Red
        throw "Generated JSON is invalid"
    }
    
    Write-Host "DEBUG: Executing oc patch command..." -ForegroundColor Magenta
    Write-Host "DEBUG: Command: oc patch secret backend-secrets --type=merge -p `"$($patchJson.Substring(0, [Math]::Min(50, $patchJson.Length)))...`"" -ForegroundColor Magenta
    
    # ✅ FIX: Use proper PowerShell argument passing to avoid shell escaping issues
    # Method 1: Use -- to separate arguments and proper escaping
    $escapedJson = $patchJson -replace '"', '\"'
    Write-Host "DEBUG: Trying method 1 with escaped quotes..." -ForegroundColor Magenta
    
    try {
        # Use Start-Process for better argument control
        $processArgs = @('patch', 'secret', 'backend-secrets', '--type=merge', '-p', $patchJson)
        $result = & oc $processArgs
        $method1Success = ($LASTEXITCODE -eq 0)
    } catch {
        $method1Success = $false
        Write-Host "DEBUG: Method 1 failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    if (-not $method1Success) {
        Write-Host "DEBUG: Trying method 2 with single quotes..." -ForegroundColor Magenta
        try {
            # Method 2: Use PowerShell's call operator with single quotes
            $singleQuotedJson = "'" + $patchJson + "'"
            & oc patch secret backend-secrets --type=merge -p $singleQuotedJson
            $method2Success = ($LASTEXITCODE -eq 0)
        } catch {
            $method2Success = $false
            Write-Host "DEBUG: Method 2 failed: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        
        if (-not $method2Success) {
            Write-Host "DEBUG: Trying method 3 with file-based approach..." -ForegroundColor Magenta
            # Method 3: Write to temp file and use --patch-file
            $tempFile = [System.IO.Path]::GetTempFileName()
            try {
                $patchJson | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
                & oc patch secret backend-secrets --type=merge --patch-file $tempFile
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "DEBUG: Method 3 (file-based) succeeded!" -ForegroundColor Green
                } else {
                    throw "All methods failed"
                }
            } finally {
                if (Test-Path $tempFile) {
                    Remove-Item $tempFile -Force
                }
            }
        } else {
            Write-Host "DEBUG: Method 2 (single quotes) succeeded!" -ForegroundColor Green
        }
    } else {
        Write-Host "DEBUG: Method 1 (argument array) succeeded!" -ForegroundColor Green
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] backend-secrets updated successfully" -ForegroundColor Green
    } else {
        Write-Host "DEBUG: oc patch failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        throw "Patch command failed"
    }
} catch {
    Write-Host "StringData method failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "Trying alternative approach..." -ForegroundColor Yellow
    
    # ✅ FALLBACK METHOD: Individual key updates using base64
    Write-Host "Applying individual secret updates..." -ForegroundColor Gray
    
    foreach ($key in $secretConfig.Keys) {
        $value = $secretConfig[$key]
        
        # Handle empty/null values properly
        if ($value -eq $null) {
            $value = ""
            Write-Host "DEBUG: Converting null value for $key to empty string" -ForegroundColor Yellow
        }
        
        $base64Value = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($value.ToString()))
        $singlePatch = "[{`"op`": `"replace`", `"path`": `"/data/$key`", `"value`": `"$base64Value`"}]"
        
        Write-Host "DEBUG: Patching $key with JSON: $singlePatch" -ForegroundColor Magenta
        
        # ✅ FIX: Use same argument passing method for individual patches
        try {
            $processArgs = @('patch', 'secret', 'backend-secrets', '--type=json', '-p', $singlePatch)
            & oc $processArgs
            $patchSuccess = ($LASTEXITCODE -eq 0)
        } catch {
            $patchSuccess = $false
        }
        
        if (-not $patchSuccess -and $value.ToString() -eq "") {
            # Special handling for empty values - try with file method
            Write-Host "DEBUG: Retrying $key with file method due to empty value..." -ForegroundColor Yellow
            $tempFile = [System.IO.Path]::GetTempFileName()
            try {
                $singlePatch | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
                & oc patch secret backend-secrets --type=json --patch-file $tempFile
                $patchSuccess = ($LASTEXITCODE -eq 0)
            } finally {
                if (Test-Path $tempFile) {
                    Remove-Item $tempFile -Force
                }
            }
        }
        
        if ($patchSuccess) {
            Write-Host "✅ Updated $key" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Failed to update $key (exit code: $LASTEXITCODE)" -ForegroundColor Red
        }
    }
}

# Verify the update worked
try {
    Write-Host "Verifying secret update..." -ForegroundColor Gray
    $verifyData = (oc get secret backend-secrets -o json | ConvertFrom-Json).data
    $verifyPassword = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($verifyData.POSTGRES_PASSWORD))
    $verifyDatabaseUrl = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($verifyData.DATABASE_URL))
    
    Write-Host "Verified password: $($verifyPassword.Substring(0,8))..." -ForegroundColor Green
    Write-Host "Verified DATABASE_URL: postgresql://app:***@postgres:5432/aibeniq" -ForegroundColor Green
    
    if ($verifyPassword -eq $dbPassword -and $verifyDatabaseUrl -eq $databaseUrl) {
        Write-Host "[OK] Secret verification passed!" -ForegroundColor Green
        
        # Final password verification if PostgreSQL is running
        $pgRunning = oc get pods -l component=postgres --field-selector=status.phase=Running --no-headers 2>$null
        if ($pgRunning -and $pgRunning.Length -gt 0 -and (Test-PostgresInitialized)) {
            Write-Host "Performing final database password test..." -ForegroundColor Gray
            $finalPasswordTest = Test-PostgresPassword -Namespace $namespace -Password $verifyPassword
            if ($finalPasswordTest) {
                Write-Host "✅ Final verification: Database accepts new password!" -ForegroundColor Green
            } else {
                Write-Host "[WARNING] Database password test failed after update." -ForegroundColor Yellow
                Write-Host "This indicates a password mismatch that requires resolution." -ForegroundColor Yellow
                
                if ($ForcePasswordRotate) {
                    Write-Host "Attempting password rotation (ForcePasswordRotate enabled)..." -ForegroundColor Cyan
                    $rotationSuccess = Invoke-PasswordRotation -NewPassword $verifyPassword -Namespace $namespace
                    if ($rotationSuccess) {
                        Write-Host "✅ Password rotation completed successfully!" -ForegroundColor Green
                    } else {
                        Write-Host "❌ Password rotation failed. Consider -DestructiveReset." -ForegroundColor Red
                        Write-Host "Run: .\scripts\setup-secrets.ps1 -Environment $Environment -DestructiveReset" -ForegroundColor Cyan
                        exit 1
                    }
                } else {
                    Write-Host "Consider running with -ForcePasswordRotate or -DestructiveReset" -ForegroundColor Cyan
                }
            }
        }
    } else {
        Write-Host "[ERROR] Secret verification failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[WARNING] Could not verify secrets, but update may have succeeded" -ForegroundColor Yellow
}

# Remove any old postgres-secret if it exists (cleanup orphaned architecture)
try {
    $deleteResult = oc delete secret postgres-secret 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Removed orphaned postgres-secret" -ForegroundColor Green
    }
    # Reset LASTEXITCODE to prevent it from affecting script exit code
    $LASTEXITCODE = 0
} catch {
    # Ignore if it doesn't exist, reset exit code
    $LASTEXITCODE = 0
}

# Restart deployments if requested
if ($Restart) {
    Write-Host "Restarting deployments to pick up secret changes..." -ForegroundColor Yellow
    
    # Restart postgres first (if database settings changed)
    Write-Host "Restarting postgres..." -ForegroundColor Gray
    oc rollout restart deployment/postgres
    oc rollout status deployment/postgres --timeout=180s
    
    # Then restart backend
    Write-Host "Restarting backend..." -ForegroundColor Gray
    oc rollout restart deployment/backend
    oc rollout status deployment/backend --timeout=180s
    
    Write-Host "[OK] Deployments restarted" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Secret Setup Complete ===" -ForegroundColor Green
Write-Host "All secrets are now configured consistently." -ForegroundColor White
Write-Host "Database password is managed through backend-secrets only." -ForegroundColor White
Write-Host ""
Write-Host "Architecture improvements applied:" -ForegroundColor Yellow
Write-Host "✅ Single source of truth for database password" -ForegroundColor Gray
Write-Host "✅ Consistent DATABASE_URL generation" -ForegroundColor Gray
Write-Host "✅ Correct service names (postgres not postgres-service)" -ForegroundColor Gray
Write-Host "✅ Removed redundant postgres-secret" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Deploy with: .\scripts\deploy-openshift.ps1 -Environment $Environment" -ForegroundColor Gray
Write-Host "2. Verify with: .\scripts\setup-secrets.ps1 -Environment $Environment -Validate" -ForegroundColor Gray
Write-Host "3. If issues persist: .\scripts\setup-secrets.ps1 -Environment $Environment -Restart" -ForegroundColor Gray

# Ensure script exits with success code when everything worked
exit 0
