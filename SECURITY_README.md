# 🔒 SPARTA AI Security Documentation

## Quick Start

Run the appropriate script for your operating system:

### Windows (PowerShell)
```powershell
.\quick_critical_fixes.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x quick_critical_fixes.sh
./quick_critical_fixes.sh
```

---

## 📁 Security Files Overview

| File | Purpose | Priority |
|------|---------|----------|
| `SECURITY_AUDIT_COMPLETE.md` | Complete audit report with all findings | 🔴 READ FIRST |
| `SECURITY_FIXES_APPLIED.md` | Tracking document for fixes | 🟡 Reference |
| `SECURITY_CHECKLIST.md` | Pre-deployment checklist | 🔴 CRITICAL |
| `.security.yml` | Security configuration | 🟡 Configure |
| `apply_security_fixes.py` | Automated fix script | 🟢 Run After Review |
| `quick_critical_fixes.sh/ps1` | Quick critical fixes | 🔴 RUN FIRST |

---

## 🚀 Getting Started

### 1. Run Quick Fixes (5 minutes)
```bash
# Windows
.\quick_critical_fixes.ps1

# Linux/Mac
./quick_critical_fixes.sh
```

This will:
- ✅ Check for hardcoded credentials
- ✅ Create .env.example
- ✅ Update .gitignore
- ✅ Create security checklist
- ✅ Set up pre-commit hooks

### 2. Review Audit Report (15 minutes)
Read `SECURITY_AUDIT_COMPLETE.md` to understand:
- What was found
- What was fixed
- What needs attention
- Recommended actions

### 3. Apply Automated Fixes (10 minutes)
```bash
python apply_security_fixes.py
```

This will:
- Sanitize logging
- Fix datetime timezone issues
- Add path validation
- Fix generic exceptions
- Sanitize HTML output

### 4. Manual Fixes (30-60 minutes)
Follow the checklist in `SECURITY_AUDIT_COMPLETE.md` for:
- Moving hardcoded credentials to .env
- Adding file upload validation
- Implementing XSS protection
- Adding specific exception handling

### 5. Test Everything (30 minutes)
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose up -d
# Run your test suite
```

---

## 🎯 Priority Actions

### 🔴 IMMEDIATE (Do Today)

1. **Remove Hardcoded Credentials**
   ```bash
   # Check for hardcoded keys
   grep -r "sk-" backend/app/services/
   
   # Move to .env
   echo "OPENAI_API_KEY=your_key_here" >> backend/.env
   ```

2. **Run Quick Fixes**
   ```bash
   ./quick_critical_fixes.sh  # or .ps1 for Windows
   ```

3. **Update .gitignore**
   ```bash
   # Ensure .env is ignored
   echo ".env" >> .gitignore
   git rm --cached .env  # If already committed
   ```

### 🟠 HIGH (This Week)

4. **Add File Upload Validation**
   ```python
   ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.json'}
   MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
   ```

5. **Sanitize HTML Outputs**
   ```python
   import html
   safe_output = html.escape(user_input)
   ```

6. **Fix Datetime Timezone**
   ```python
   from datetime import datetime, timezone
   now = datetime.now(timezone.utc)
   ```

### 🟡 MEDIUM (This Month)

7. **Add Path Validation**
8. **Implement Specific Exception Handling**
9. **Add Security Monitoring**
10. **Update Dependencies**

---

## 📊 Current Security Status

### ✅ Strengths
- JWT authentication implemented
- CORS protection configured
- Rate limiting active
- Code execution sandboxed
- Security headers enabled
- Input validation with Pydantic

### 🔄 In Progress
- Removing hardcoded credentials
- Adding file upload security
- Implementing XSS protection
- Fixing timezone issues

### ❌ Needs Attention
- Some hardcoded API keys
- Path traversal validation
- HTML sanitization
- Log injection prevention

---

## 🛡️ Security Features

### Authentication & Authorization
- ✅ JWT tokens with expiration
- ✅ Password hashing (bcrypt)
- ✅ Role-based access control
- 🔄 Two-factor authentication (planned)

### Data Protection
- ✅ HTTPS in production
- ✅ Encrypted database connections
- ✅ Secure session management
- 🔄 Data encryption at rest (planned)

### Code Security
- ✅ Sandboxed code execution
- ✅ Whitelist-based imports
- ✅ Resource limits
- ✅ AST validation

### Infrastructure
- ✅ Docker containerization
- ✅ Network isolation
- ✅ Security headers
- 🔄 WAF integration (planned)

---

## 🔍 Security Testing

### Automated Tests
```bash
# Python security scan
bandit -r backend/app/

# Dependency vulnerabilities
pip-audit
npm audit

# Docker security
docker scan sparta-backend:latest

# SAST scanning
# Already done - see Code Issues Panel
```

### Manual Testing
```bash
# Test rate limiting
ab -n 1000 -c 10 http://localhost:8000/api/v1/health

# Test file upload limits
curl -X POST -F "file=@large_file.csv" \
  http://localhost:8000/api/v1/files/upload

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"wrong"}'
```

---

## 📚 Resources

### Internal Documentation
- [Security Audit Report](SECURITY_AUDIT_COMPLETE.md)
- [Security Checklist](SECURITY_CHECKLIST.md)
- [Security Configuration](.security.yml)
- [Fixes Applied](SECURITY_FIXES_APPLIED.md)

### External Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Database](https://cwe.mitre.org/)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [React Security](https://reactjs.org/docs/dom-elements.html#dangerouslysetinnerhtml)

### Tools
- [Bandit](https://github.com/PyCQA/bandit) - Python security linter
- [pip-audit](https://github.com/pypa/pip-audit) - Dependency scanner
- [npm audit](https://docs.npmjs.com/cli/v8/commands/npm-audit) - Node security
- [Docker Scan](https://docs.docker.com/engine/scan/) - Container security
- [OWASP ZAP](https://www.zaproxy.org/) - Web app scanner

---

## 🆘 Emergency Response

### If You Discover a Security Issue

1. **DO NOT** commit the fix immediately
2. **DO NOT** discuss publicly
3. **DO** email security@spartaai.com
4. **DO** document the issue privately
5. **DO** wait for security team response

### If Credentials Are Compromised

1. **Immediately** rotate all affected credentials
2. **Review** access logs for suspicious activity
3. **Notify** security team
4. **Document** the incident
5. **Update** security procedures

### Incident Response Checklist

- [ ] Identify the security issue
- [ ] Assess the impact
- [ ] Contain the threat
- [ ] Eradicate the vulnerability
- [ ] Recover systems
- [ ] Document lessons learned
- [ ] Update security measures

---

## 📞 Contact

### Security Team
- Email: security@spartaai.com
- Emergency: +1-XXX-XXX-XXXX
- Bug Bounty: bugbounty@spartaai.com

### Development Team
- DevOps: devops@spartaai.com
- Backend: backend@spartaai.com
- Frontend: frontend@spartaai.com

---

## 📝 Changelog

### 2025-01-XX - Initial Security Audit
- Completed comprehensive security audit
- Fixed critical code injection vulnerability
- Created security documentation
- Provided automated fix scripts
- Established security procedures

---

## ✅ Next Review

**Scheduled**: April 2025  
**Type**: Comprehensive Security Audit  
**Focus**: Verify all fixes, new vulnerabilities, compliance

---

**Remember**: Security is everyone's responsibility. If you see something, say something!

🔒 **Stay Secure!**
