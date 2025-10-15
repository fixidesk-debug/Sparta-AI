#!/bin/bash
# Quick Critical Security Fixes for SPARTA AI
# Run this script to apply immediate critical fixes

echo "=================================="
echo "SPARTA AI - Critical Security Fixes"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: Please run this script from the SPARTA AI root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking for hardcoded credentials...${NC}"
if grep -r "api_key.*=.*['\"]sk-" backend/app/services/ 2>/dev/null; then
    echo -e "${RED}WARNING: Found hardcoded API keys!${NC}"
    echo "Please move these to environment variables:"
    echo "  1. Add to .env file"
    echo "  2. Use os.getenv('API_KEY')"
    echo "  3. Never commit .env to git"
else
    echo -e "${GREEN}✓ No obvious hardcoded credentials found${NC}"
fi
echo ""

echo -e "${YELLOW}Step 2: Checking .env.example exists...${NC}"
if [ ! -f "backend/.env.example" ]; then
    echo "Creating .env.example..."
    cat > backend/.env.example << 'EOF'
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
EOF
    echo -e "${GREEN}✓ Created .env.example${NC}"
else
    echo -e "${GREEN}✓ .env.example exists${NC}"
fi
echo ""

echo -e "${YELLOW}Step 3: Checking .gitignore for sensitive files...${NC}"
if ! grep -q "\.env$" .gitignore 2>/dev/null; then
    echo "Adding .env to .gitignore..."
    echo "" >> .gitignore
    echo "# Environment variables" >> .gitignore
    echo ".env" >> .gitignore
    echo ".env.local" >> .gitignore
    echo ".env.*.local" >> .gitignore
    echo -e "${GREEN}✓ Updated .gitignore${NC}"
else
    echo -e "${GREEN}✓ .env already in .gitignore${NC}"
fi
echo ""

echo -e "${YELLOW}Step 4: Creating security checklist...${NC}"
cat > SECURITY_CHECKLIST.md << 'EOF'
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

## Quick Security Test

```bash
# Test 1: Check for exposed secrets
git log --all --full-history --source --find-object=<secret>

# Test 2: Scan dependencies
pip-audit  # Python
npm audit  # Node.js

# Test 3: Check Docker security
docker scan sparta-backend:latest

# Test 4: Test rate limiting
ab -n 1000 -c 10 http://localhost:8000/api/v1/health

# Test 5: Test file upload limits
curl -X POST -F "file=@large_file.csv" http://localhost:8000/api/v1/files/upload
```

## Emergency Contacts

- Security Team: security@spartaai.com
- On-Call: +1-XXX-XXX-XXXX
- Bug Bounty: bugbounty@spartaai.com
EOF
echo -e "${GREEN}✓ Created SECURITY_CHECKLIST.md${NC}"
echo ""

echo -e "${YELLOW}Step 5: Checking Python dependencies for vulnerabilities...${NC}"
if command -v pip-audit &> /dev/null; then
    cd backend
    pip-audit --desc 2>/dev/null || echo -e "${YELLOW}Install pip-audit: pip install pip-audit${NC}"
    cd ..
else
    echo -e "${YELLOW}pip-audit not installed. Install with: pip install pip-audit${NC}"
fi
echo ""

echo -e "${YELLOW}Step 6: Creating pre-commit hook...${NC}"
mkdir -p .git/hooks
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to prevent committing secrets

# Check for common secret patterns
if git diff --cached --name-only | xargs grep -E "(api_key|secret_key|password|token).*=.*['\"][^'\"]{20,}" 2>/dev/null; then
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
EOF
chmod +x .git/hooks/pre-commit
echo -e "${GREEN}✓ Created pre-commit hook${NC}"
echo ""

echo "=================================="
echo -e "${GREEN}Critical fixes applied!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Review SECURITY_CHECKLIST.md"
echo "2. Update .env with your actual credentials"
echo "3. Run: python apply_security_fixes.py"
echo "4. Test the application thoroughly"
echo "5. Review SECURITY_AUDIT_COMPLETE.md"
echo ""
echo -e "${YELLOW}Remember: Security is an ongoing process!${NC}"
