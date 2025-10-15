# Quick Critical Security Fixes for SPARTA AI (PowerShell)
# Run this script to apply immediate critical fixes

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "SPARTA AI - Critical Security Fixes" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "Error: Please run this script from the SPARTA AI root directory" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Checking for hardcoded credentials..." -ForegroundColor Yellow
$hardcodedKeys = Get-ChildItem -Path "backend\app\services" -Recurse -Include *.py | 
    Select-String -Pattern "api_key.*=.*['\`"]sk-" -ErrorAction SilentlyContinue

if ($hardcodedKeys) {
    Write-Host "WARNING: Found hardcoded API keys!" -ForegroundColor Red
    Write-Host "Please move these to environment variables:"
    Write-Host "  1. Add to .env file"
    Write-Host "  2. Use os.getenv('API_KEY')"
    Write-Host "  3. Never commit .env to git"
} else {
    Write-Host "✓ No obvious hardcoded credentials found" -ForegroundColor Green
}
Write-Host ""

Write-Host "Step 2: Checking .env.example exists..." -ForegroundColor Yellow
if (-not (Test-Path "backend\.env.example")) {
    Write-Host "Creating .env.example..."
    @"
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sparta_ai
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-here-change-in-production

# AI Providers (Get your keys from respective providers)
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GROQ_API_KEY=gsk_your-groq-key-here
GOOGLE_API_KEY=your-google-key-here

# Application
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ENVIRONMENT=development

# File Upload
MAX_UPLOAD_SIZE_MB=100
UPLOAD_DIR=uploads

# Code Execution
CODE_EXECUTION_TIMEOUT=30
CODE_EXECUTION_MAX_MEMORY_MB=512
"@ | Out-File -FilePath "backend\.env.example" -Encoding UTF8
    Write-Host "✓ Created .env.example" -ForegroundColor Green
} else {
    Write-Host "✓ .env.example exists" -ForegroundColor Green
}
Write-Host ""

Write-Host "Step 3: Checking .gitignore for sensitive files..." -ForegroundColor Yellow
$gitignoreContent = Get-Content ".gitignore" -ErrorAction SilentlyContinue
if ($gitignoreContent -notmatch "\.env$") {
    Write-Host "Adding .env to .gitignore..."
    @"

# Environment variables
.env
.env.local
.env.*.local
"@ | Add-Content -Path ".gitignore"
    Write-Host "✓ Updated .gitignore" -ForegroundColor Green
} else {
    Write-Host "✓ .env already in .gitignore" -ForegroundColor Green
}
Write-Host ""

Write-Host "Step 4: Creating security checklist..." -ForegroundColor Yellow
@"
# Security Checklist for SPARTA AI

## Before Deployment

### Critical
- [ ] All API keys moved to environment variables
- [ ] .env file NOT committed to git
- [ ] SECRET_KEY changed from default
- [ ] JWT_SECRET_KEY changed from default
- [ ] Database password changed from default
- [ ] HTTPS enabled in production
- [ ] CORS origins restricted to production domains

### High Priority
- [ ] File upload size limits configured
- [ ] File type validation enabled
- [ ] Rate limiting configured
- [ ] Security headers enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (HTML escaping)
- [ ] CSRF protection enabled

### Medium Priority
- [ ] Logging configured (no sensitive data)
- [ ] Error messages don't expose internals
- [ ] Dependencies updated to latest secure versions
- [ ] Docker images scanned for vulnerabilities
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured

### Ongoing
- [ ] Regular security audits scheduled
- [ ] Dependency updates automated
- [ ] Security training for team
- [ ] Incident response plan documented
- [ ] Penetration testing scheduled

## Quick Security Test (PowerShell)

```powershell
# Test 1: Check for exposed secrets
git log --all --full-history --source

# Test 2: Scan Python dependencies
pip-audit

# Test 3: Scan Node dependencies
npm audit

# Test 4: Check Docker security
docker scan sparta-backend:latest

# Test 5: Test rate limiting
# Install: choco install apache-httpd
ab -n 1000 -c 10 http://localhost:8000/api/v1/health
```

## Emergency Contacts

- Security Team: security@spartaai.com
- On-Call: +1-XXX-XXX-XXXX
- Bug Bounty: bugbounty@spartaai.com
"@ | Out-File -FilePath "SECURITY_CHECKLIST.md" -Encoding UTF8
Write-Host "✓ Created SECURITY_CHECKLIST.md" -ForegroundColor Green
Write-Host ""

Write-Host "Step 5: Checking Python dependencies for vulnerabilities..." -ForegroundColor Yellow
if (Get-Command pip-audit -ErrorAction SilentlyContinue) {
    Push-Location backend
    pip-audit --desc 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Install pip-audit: pip install pip-audit" -ForegroundColor Yellow
    }
    Pop-Location
} else {
    Write-Host "pip-audit not installed. Install with: pip install pip-audit" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "Step 6: Creating pre-commit hook..." -ForegroundColor Yellow
$hookDir = ".git\hooks"
if (-not (Test-Path $hookDir)) {
    New-Item -ItemType Directory -Path $hookDir -Force | Out-Null
}

@"
#!/bin/bash
# Pre-commit hook to prevent committing secrets

# Check for common secret patterns
if git diff --cached --name-only | xargs grep -E "(api_key|secret_key|password|token).*=.*['\`"][^'\`"]{20,}" 2>/dev/null; then
    echo "ERROR: Possible secret detected in commit!"
    echo "Please remove secrets and use environment variables instead."
    exit 1
fi

# Check if .env is being committed
if git diff --cached --name-only | grep -q "^\.env$"; then
    echo "ERROR: Attempting to commit .env file!"
    echo "This file contains secrets and should not be committed."
    exit 1
fi

exit 0
"@ | Out-File -FilePath "$hookDir\pre-commit" -Encoding UTF8
Write-Host "✓ Created pre-commit hook" -ForegroundColor Green
Write-Host ""

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Critical fixes applied!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Review SECURITY_CHECKLIST.md"
Write-Host "2. Update .env with your actual credentials"
Write-Host "3. Run: python apply_security_fixes.py"
Write-Host "4. Test the application thoroughly"
Write-Host "5. Review SECURITY_AUDIT_COMPLETE.md"
Write-Host ""
Write-Host "Remember: Security is an ongoing process!" -ForegroundColor Yellow
