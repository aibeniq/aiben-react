#!/usr/bin/env pwsh
# Simple test script

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod")]
    [string]$Environment
)

Write-Host "=== Test Script ($Environment) ===" -ForegroundColor Green

# Test the problematic section
$secretConfig = @{
    SECRET_KEY = "test-secret"
    OPENAI_ADMIN_KEY = 'REMOVED_OPENAI_ADMIN_KEY'
    REPLICATE_API_TOKEN = 'REMOVED_REPLICATE_API_TOKEN'
}

Write-Host "Hash table created successfully" -ForegroundColor Green
Write-Host "Test completed!" -ForegroundColor Green
