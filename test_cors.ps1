Write-Host "Testing CORS..."

# Test OPTIONS preflight
$headers = @{
    "Origin" = "http://localhost:3000"
    "Access-Control-Request-Method" = "POST"
    "Access-Control-Request-Headers" = "content-type,authorization"
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/files/upload" -Method OPTIONS -Headers $headers -UseBasicParsing
    Write-Host "✅ OPTIONS request successful"
    Write-Host "CORS Headers:"
    $response.Headers.GetEnumerator() | Where-Object { $_.Key -like "*Access-Control*" } | ForEach-Object {
        Write-Host "  $($_.Key): $($_.Value)"
    }
} catch {
    Write-Host "❌ OPTIONS request failed"
    Write-Host "Error: $_"
}

# Test if server is responding
Write-Host "`nTesting health endpoint..."
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "✅ Server is running: $($health.status)"
} catch {
    Write-Host "❌ Server not responding"
}
