$body = @{
    username = "admin@sparta.ai"
    password = "admin123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method Post -Body $body -ContentType "application/json"

Write-Host "Login successful!"
Write-Host "Token: $($response.access_token)"
