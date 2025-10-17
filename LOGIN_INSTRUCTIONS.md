# 🔐 Login Instructions - Fix 401 Unauthorized Error

## Problem
You're getting 401 (Unauthorized) errors because you're not logged in.

## Solution - Login First

### Option 1: Use the Login Page (Recommended)

1. **Go to the login page:**
   - Navigate to: http://localhost:3000/login
   - Or http://localhost:3000/auth/login

2. **Login with default credentials:**
   ```
   Email: admin@sparta.ai
   Password: admin123
   ```

3. **After login, you'll be redirected and can use all features**

### Option 2: Get Token via API

If you need to test the API directly:

```bash
# Login and get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@sparta.ai","password":"admin123"}'
```

Response will include a token:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Then use the token in requests:
```bash
curl http://localhost:8000/api/v1/notebooks/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Option 3: Register a New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "yourpassword",
    "full_name": "Your Name"
  }'
```

## Default Admin Account

**Email:** admin@sparta.ai  
**Password:** admin123

This account is created automatically when the database is initialized.

## How Authentication Works

1. **Login** → Get JWT token
2. **Store token** → Frontend stores in localStorage
3. **Use token** → All API requests include: `Authorization: Bearer <token>`
4. **Token expires** → Login again after 7 days

## Frontend Auto-Login

The frontend (`frontend/src/lib/api.ts`) automatically:
- Stores token in localStorage after login
- Adds token to all API requests
- Redirects to login if token is missing/expired

## Quick Fix for Your Current Error

**Just login at:** http://localhost:3000/login

Use:
- Email: `admin@sparta.ai`
- Password: `admin123`

After login, all 401 errors will be resolved! ✅

## Testing Without Frontend

If you want to test the API directly without the frontend:

1. **Get token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@sparta.ai","password":"admin123"}'
```

2. **Copy the access_token from response**

3. **Use in API docs:**
   - Go to http://localhost:8000/docs
   - Click "Authorize" button (top right)
   - Paste token in the value field
   - Click "Authorize"
   - Now you can test all endpoints!

## WebSocket 403 Error

The WebSocket error is also due to authentication. After login, WebSocket connections will work.

## Summary

**Problem:** Not logged in → 401 errors  
**Solution:** Login at http://localhost:3000/login  
**Credentials:** admin@sparta.ai / admin123  
**Result:** All features will work! ✅
