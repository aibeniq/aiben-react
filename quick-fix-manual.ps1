# Essential fix commands - run each line manually if needed
Write-Host "Fixing database connection..."

# Get current password
$DB_PASSWORD = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((oc get secret backend-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}')))
$DATABASE_URL = "postgresql://app:$DB_PASSWORD@postgres:5432/aibeniq"

# Fix POSTGRES_SERVER
$POSTGRES_SERVER_B64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("postgres"))
Write-Host "Updating POSTGRES_SERVER..."
oc patch secret backend-secrets --type=json -p="[{`"op`": `"replace`", `"path`": `"/data/POSTGRES_SERVER`", `"value`": `"$POSTGRES_SERVER_B64`"}]"

# Fix DATABASE_URL
$DATABASE_URL_B64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($DATABASE_URL))
Write-Host "Updating DATABASE_URL..."
oc patch secret backend-secrets --type=json -p="[{`"op`": `"replace`", `"path`": `"/data/DATABASE_URL`", `"value`": `"$DATABASE_URL_B64`"}]"

# Restart backend
Write-Host "Restarting backend..."
oc rollout restart deployment/backend
oc rollout status deployment/backend --timeout=180s

Write-Host "Done!"
