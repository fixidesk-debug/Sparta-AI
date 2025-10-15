# Sparta AI - Complete Startup Script
# Run this after Docker Desktop is started

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Sparta AI - Complete Startup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Start Database Services
Write-Host "1. Starting Docker services..." -ForegroundColor Yellow
Set-Location "C:\Users\viren\Desktop\SPARTA AI"
docker-compose up -d db redis

Start-Sleep -Seconds 5

# Step 2: Start Backend
Write-Host "`n2. Starting Backend API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'C:\Users\viren\Desktop\SPARTA AI\backend'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 3

# Step 3: Start Frontend
Write-Host "`n3. Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'C:\Users\viren\Desktop\SPARTA AI\frontend'; npm start"

Start-Sleep -Seconds 5

# Step 4: Verify
Write-Host "`n4. Verifying services..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    Invoke-RestMethod -Uri 'http://localhost:8000/health' -TimeoutSec 5 | Out-Null
    Write-Host "   ✅ Backend: RUNNING" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Backend: Starting up..." -ForegroundColor Yellow
}

try {
    Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 5 | Out-Null
    Write-Host "   ✅ Frontend: RUNNING" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Frontend: Starting up..." -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Sparta AI is Starting!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`n✅ Test Account:" -ForegroundColor Yellow
Write-Host "   Email: test@example.com" -ForegroundColor Cyan
Write-Host "   Password: testpassword123`n" -ForegroundColor Cyan

Write-Host "Services are starting in separate windows. Please wait 30 seconds for everything to be ready.`n" -ForegroundColor Gray