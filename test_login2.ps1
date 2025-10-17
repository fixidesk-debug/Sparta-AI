$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    username = "admin@sparta.ai"
    password = "admin123"
} | ConvertTo-Json

Write-Host "Testing login..."
Write-Host "Body: $body"

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $body -Headers $headers
    Write-Host "✅ Login successful!"
    Write-Host "Token: $($response.access_token.Substring(0, 50))..."
} catch {
    Write-Host "❌ Login failed!"
    Write-Host "Error: $_"
}
