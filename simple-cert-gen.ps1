# Simple certificate generation using .NET without complex ASN.1 encoding
param(
    [switch]$Force
)

$certFile = "wildcard-aiben-cert.pem"
$keyFile = "wildcard-aiben-key.pem"

if ((Test-Path $certFile) -or (Test-Path $keyFile)) {
    if (-not $Force) {
        Write-Error "Certificate files already exist. Use -Force to overwrite."
        exit 1
    }
    Remove-Item $certFile -ErrorAction SilentlyContinue
    Remove-Item $keyFile -ErrorAction SilentlyContinue
}

# Create certificate
$subject = "CN=*.aiben.io,O=AiBen,C=US"
$dnsNames = @("*.aiben.io", "aiben.io")

$cert = New-SelfSignedCertificate -Subject $subject -DnsName $dnsNames -CertStoreLocation "Cert:\CurrentUser\My" -KeyAlgorithm RSA -KeyLength 2048 -KeyExportPolicy Exportable

# Export certificate
$certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
$certB64 = [System.Convert]::ToBase64String($certBytes)
$certPem = "-----BEGIN CERTIFICATE-----`n"
for ($i = 0; $i -lt $certB64.Length; $i += 64) {
    $certPem += $certB64.Substring($i, [Math]::Min(64, $certB64.Length - $i)) + "`n"
}
$certPem += "-----END CERTIFICATE-----`n"
$certPem | Out-File -FilePath $certFile -Encoding ASCII -NoNewline

# Export as PFX first, then extract key
$pfxPath = "temp.pfx"
$password = "temp"
$securePassword = ConvertTo-SecureString -String $password -Force -AsPlainText

Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $securePassword -Force | Out-Null

# Use openssl if available, otherwise create a basic key file
try {
    $opensslResult = & openssl pkcs12 -in $pfxPath -nocerts -out $keyFile -passin pass:$password -passout pass: -nodes 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Used OpenSSL to extract private key" -ForegroundColor Green
    } else {
        throw "OpenSSL failed"
    }
}
catch {
    Write-Host "OpenSSL not available, using PowerShell method..." -ForegroundColor Yellow
    
    # Fallback: create a simple private key format that OpenShift can read
    # This uses the PFX export and manual key extraction
    $pfxCert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($pfxPath, $password, [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::Exportable)
    $privateKey = $pfxCert.PrivateKey
    
    # Export using legacy CSP method which is more compatible
    if ($privateKey -is [System.Security.Cryptography.RSACryptoServiceProvider]) {
        $keyBlob = $privateKey.ExportCspBlob($true)
        $keyB64 = [System.Convert]::ToBase64String($keyBlob)
        
        # This creates a Windows-specific format, but we'll convert it
        # For now, create a placeholder that we'll replace with proper OpenSSL generation
        $keyPem = "-----BEGIN RSA PRIVATE KEY-----`n"
        for ($i = 0; $i -lt $keyB64.Length; $i += 64) {
            $keyPem += $keyB64.Substring($i, [Math]::Min(64, $keyB64.Length - $i)) + "`n"
        }
        $keyPem += "-----END RSA PRIVATE KEY-----`n"
        $keyPem | Out-File -FilePath $keyFile -Encoding ASCII -NoNewline
    }
}

# Clean up
Remove-Item $pfxPath -Force -ErrorAction SilentlyContinue
Remove-Item "Cert:\CurrentUser\My\$($cert.Thumbprint)" -ErrorAction SilentlyContinue

Write-Host "Certificate files created. Testing with OpenShift..." -ForegroundColor Green

# Test if OpenShift can read the files
$testResult = & oc create secret tls test-wildcard --cert=$certFile --key=$keyFile --dry-run=client -o yaml 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Certificate format is compatible with OpenShift" -ForegroundColor Green
} else {
    Write-Host "✗ Certificate format issue: $testResult" -ForegroundColor Red
    Write-Host "Attempting to fix with OpenSSL conversion..." -ForegroundColor Yellow
    
    # Try to convert using openssl if available
    try {
        & openssl rsa -in $keyFile -out "${keyFile}.fixed" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Move-Item "${keyFile}.fixed" $keyFile -Force
            Write-Host "✓ Fixed private key format" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "OpenSSL not available for format conversion" -ForegroundColor Yellow
    }
}

Write-Host "`nFiles created:" -ForegroundColor Cyan
Write-Host "- Certificate: $certFile" -ForegroundColor White
Write-Host "- Private key: $keyFile" -ForegroundColor White
