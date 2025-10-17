# 🔧 Quick Fix for 401 Unauthorized Error

## The Problem
You're seeing these errors:
```
GET http://localhost:8000/api/v1/notebooks/ 401 (Unauthorized)
WebSocket connection failed: 403
```

## The Solution (30 seconds)

### Step 1: Open Login Page
Go to: **http://localhost:3000/auth/login**

### Step 2: Login
```
Email: admin@sparta.ai
Password: admin123
```

### Step 3: Done!
All 401 errors will disappear. All features will work.

---

## Why This Happens

The frontend is trying to access protected API endpoints without authentication. You need to login first to get a JWT token.

## What Happens After Login

1. ✅ Token stored in browser localStorage
2. ✅ All API requests include the token
3. ✅ All features work
4. ✅ WebSocket connections work
5. ✅ No more 401 errors

---

## Alternative: Test API Directly

If you want to test the backend API without the frontend:

### 1. Get Token via curl:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin@sparta.ai\",\"password\":\"admin123\"}"
```

### 2. Use Token in API Docs:
1. Go to http://localhost:8000/docs
2. Click "Authorize" button (🔒 icon, top right)
3. Paste the token from step 1
4. Click "Authorize"
5. Test all endpoints!

---

## Summary

**Problem:** Not logged in  
**Fix:** Login at http://localhost:3000/auth/login  
**Credentials:** admin@sparta.ai / admin123  
**Time:** 30 seconds  
**Result:** Everything works! ✅

---

## After Login, You Can Test:

✅ All 9 new features:
1. Version Control
2. Undo/Redo
3. Export (5 formats)
4. Scheduled Reports
5. Advanced Charts
6. Data Source Connectors
7. Dashboard Builder
8. Collaborative Editing
9. Sharing

✅ All existing features:
- File upload
- Data analysis
- Visualizations
- Natural language queries
- SQL execution
- Transformations
- Statistics
- Notebooks

**Just login and start testing!** 🚀
