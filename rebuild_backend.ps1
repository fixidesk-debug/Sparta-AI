# Rebuild Backend with AI Code Generation Integration
# This script rebuilds the backend Docker container with all AI dependencies

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SPARTA AI - Backend Rebuild" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if .env file exists
$envFile = ".\backend\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".\backend\.env.example" $envFile
    Write-Host "✅ .env file created. Please add your OPENAI_API_KEY!" -ForegroundColor Green
    Write-Host "`nEdit backend\.env and add:" -ForegroundColor Yellow
    Write-Host "  OPENAI_API_KEY=sk-your-actual-key-here`n" -ForegroundColor White
}

# Check for OPENAI_API_KEY
$envContent = Get-Content $envFile -Raw
if ($envContent -notmatch 'OPENAI_API_KEY=sk-') {
    Write-Host "⚠️  WARNING: OPENAI_API_KEY not set in .env file" -ForegroundColor Yellow
    Write-Host "   The AI code generation will not work without it!" -ForegroundColor Yellow
    Write-Host "`nPlease edit backend\.env and add:" -ForegroundColor Yellow
    Write-Host "  OPENAI_API_KEY=sk-your-actual-key-here`n" -ForegroundColor White
    
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        Write-Host "❌ Rebuild cancelled" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n📦 Step 1: Stopping containers..." -ForegroundColor Cyan
docker-compose down
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Containers stopped" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error stopping containers (may not be running)" -ForegroundColor Yellow
}

Write-Host "`n🔨 Step 2: Building backend with new dependencies..." -ForegroundColor Cyan
Write-Host "   This may take a few minutes...`n" -ForegroundColor Gray

docker-compose build backend --no-cache
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Backend built successfully" -ForegroundColor Green
} else {
    Write-Host "`n❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n🚀 Step 3: Starting all services..." -ForegroundColor Cyan
docker-compose up -d
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Services started" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to start services!" -ForegroundColor Red
    exit 1
}

Write-Host "`n⏳ Step 4: Waiting for backend to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Check backend health
for ($i = 1; $i -le 5; $i++) {
    try {
        $response = Invoke-RestMethod -Uri 'http://localhost:8000/health' -TimeoutSec 5
        Write-Host "✅ Backend is healthy!" -ForegroundColor Green
        break
    } catch {
        if ($i -eq 5) {
            Write-Host "⚠️  Backend health check failed" -ForegroundColor Yellow
            Write-Host "   Check logs: docker-compose logs backend" -ForegroundColor Gray
        } else {
            Write-Host "   Waiting... (attempt $i/5)" -ForegroundColor Gray
            Start-Sleep -Seconds 5
        }
    }
}

Write-Host "`n✅ Step 5: Verifying AI dependencies..." -ForegroundColor Cyan

# Check anthropic package
try {
    $output = docker exec sparta-backend python -c "import anthropic; print('anthropic ' + anthropic.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $output" -ForegroundColor Green
    } else {
        Write-Host "❌ anthropic package not found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Failed to check anthropic package" -ForegroundColor Red
}

# Check AI code generator
try {
    $output = docker exec sparta-backend python -c "from app.services.ai_code_generator import AICodeGenerator; print('AI Code Generator module loaded')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ AI Code Generator module loaded" -ForegroundColor Green
    } else {
        Write-Host "❌ AI Code Generator module not found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Failed to check AI Code Generator" -ForegroundColor Red
}

# Check AI providers
try {
    $output = docker exec sparta-backend python -c "from app.services.ai_providers import AIProvider; print('AI Providers module loaded')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ AI Providers module loaded" -ForegroundColor Green
    } else {
        Write-Host "❌ AI Providers module not found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Failed to check AI Providers" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✅ Backend Rebuild Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "📊 Container Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`n🧪 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Ensure OPENAI_API_KEY is set in backend\.env" -ForegroundColor White
Write-Host "  2. Run integration tests:" -ForegroundColor White
Write-Host "     docker exec -it sparta-backend python test_integration.py" -ForegroundColor Gray
Write-Host "  3. Test the API at: http://localhost:8000/docs`n" -ForegroundColor White

Write-Host "📝 View Logs:" -ForegroundColor Cyan
Write-Host "  docker-compose logs -f backend`n" -ForegroundColor Gray
