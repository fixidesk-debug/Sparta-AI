# Sparta AI - Service Status Check & Fix

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Sparta AI - Service Status Check" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Check Backend
Write-Host "1. Checking Backend API..." -ForegroundColor Yellow
try {
    $backendTest = Invoke-RestMethod -Uri 'http://localhost:8000/health' -TimeoutSec 5
    Write-Host "   ✅ Backend is RUNNING on http://localhost:8000" -ForegroundColor Green
    Write-Host "   Status: $($backendTest.status)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Backend is NOT responding on http://localhost:8000" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    
    # Try 127.0.0.1
    try {
        Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 5 | Out-Null
        Write-Host "   ⚠️  Backend is running on http://127.0.0.1:8000 instead" -ForegroundColor Yellow
        Write-Host "   This might cause CORS issues with frontend!" -ForegroundColor Yellow
    } catch {
        Write-Host "   ❌ Backend is not running at all!" -ForegroundColor Red
    }
}

# 2. Check Frontend
Write-Host "`n2. Checking Frontend..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 5 | Out-Null
    Write-Host "   ✅ Frontend is RUNNING on http://localhost:3000" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Frontend is NOT responding on http://localhost:3000" -ForegroundColor Red
}

# 3. Check Database
Write-Host "`n3. Checking Database..." -ForegroundColor Yellow
$dbCheck = docker ps --filter "name=sparta-db" --format "{{.Status}}"
if ($dbCheck -match "Up") {
    Write-Host "   ✅ PostgreSQL is RUNNING" -ForegroundColor Green
    Write-Host "   Status: $dbCheck" -ForegroundColor Cyan
} else {
    Write-Host "   ❌ PostgreSQL is NOT running" -ForegroundColor Red
}

# 4. Check Redis
Write-Host "`n4. Checking Redis..." -ForegroundColor Yellow
$redisCheck = docker ps --filter "name=sparta-redis" --format "{{.Status}}"
if ($redisCheck -match "Up") {
    Write-Host "   ✅ Redis is RUNNING" -ForegroundColor Green
    Write-Host "   Status: $redisCheck" -ForegroundColor Cyan
} else {
    Write-Host "   ❌ Redis is NOT running" -ForegroundColor Red
}

# 5. Test Registration Endpoint
Write-Host "`n5. Testing Registration Endpoint..." -ForegroundColor Yellow
$testEmail = "test$(Get-Random)@example.com"
$regBody = @{
    email = $testEmail
    password = 'test123'
    full_name = 'Test User'
} | ConvertTo-Json

try {
    $regResponse = Invoke-RestMethod `
        -Uri 'http://localhost:8000/api/v1/auth/register' `
        -Method POST `
        -Body $regBody `
        -ContentType 'application/json' `
        -TimeoutSec 10
    
    Write-Host "   ✅ Registration endpoint is WORKING" -ForegroundColor Green
    Write-Host "   Created user: $($regResponse.email)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Registration endpoint FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
}

# 6. Check Port Bindings
Write-Host "`n6. Checking Port Bindings..." -ForegroundColor Yellow
$port8000 = netstat -ano | findstr ":8000.*LISTENING"
$port3000 = netstat -ano | findstr ":3000.*LISTENING"

if ($port8000) {
    Write-Host "   ✅ Port 8000 is LISTENING" -ForegroundColor Green
    Write-Host "   $port8000" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Port 8000 is NOT listening" -ForegroundColor Red
}

if ($port3000) {
    Write-Host "   ✅ Port 3000 is LISTENING" -ForegroundColor Green
    Write-Host "   $port3000" -ForegroundColor Gray
} else {
    Write-Host "   ❌ Port 3000 is NOT listening" -ForegroundColor Red
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Summary & Next Steps" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "✅ = Working | ❌ = Not Working | ⚠️ = Needs Attention`n" -ForegroundColor Gray

Write-Host "If backend is not on localhost:8000, restart it with:" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor Cyan
Write-Host "  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`n" -ForegroundColor Cyan

Write-Host "If frontend has issues, check browser console for CORS errors." -ForegroundColor Yellow
Write-Host "Frontend should be accessible at: http://localhost:3000/login`n" -ForegroundColor Cyan
