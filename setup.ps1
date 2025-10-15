# Sparta AI Setup Script for Windows PowerShell

Write-Host "🚀 Setting up Sparta AI..." -ForegroundColor Cyan

# Create environment files
Write-Host "`n📝 Creating environment files..." -ForegroundColor Yellow

if (!(Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "✓ Created backend\.env" -ForegroundColor Green
} else {
    Write-Host "⚠ backend\.env already exists, skipping..." -ForegroundColor Yellow
}

if (!(Test-Path "frontend\.env")) {
    Copy-Item "frontend\.env.example" "frontend\.env"
    Write-Host "✓ Created frontend\.env" -ForegroundColor Green
} else {
    Write-Host "⚠ frontend\.env already exists, skipping..." -ForegroundColor Yellow
}

if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created root .env" -ForegroundColor Green
} else {
    Write-Host "⚠ .env already exists, skipping..." -ForegroundColor Yellow
}

# Create uploads directory
if (!(Test-Path "backend\uploads")) {
    New-Item -ItemType Directory -Path "backend\uploads" | Out-Null
    Write-Host "✓ Created uploads directory" -ForegroundColor Green
}

Write-Host "`n✨ Setup complete!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit backend\.env and add your API keys (especially OPENAI_API_KEY)" -ForegroundColor White
Write-Host "2. Run: docker-compose up -d" -ForegroundColor White
Write-Host "3. Access the app at: http://localhost:3000" -ForegroundColor White
Write-Host "4. API docs at: http://localhost:8000/docs" -ForegroundColor White

Write-Host "`n🐳 To start with Docker:" -ForegroundColor Cyan
Write-Host "   docker-compose up -d" -ForegroundColor White

Write-Host "`n🛠 To start in development mode:" -ForegroundColor Cyan
Write-Host "   Backend:  cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "   Frontend: cd frontend && npm install && npm start" -ForegroundColor White
