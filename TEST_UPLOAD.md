# Testing Upload and AI Features

## Issue Found and Fixed

### Problem:
1. **Upload not working**: Uploads directory might not exist
2. **AI not working**: `GROQ_API_KEY` not defined in config.py

### Solution Applied:
1. ✅ Created `uploads` directory
2. ✅ Added `GROQ_API_KEY` to config.py
3. ✅ Set default AI provider to "groq"

## How to Test

### 1. Restart Backend
The config changes require a backend restart:

```bash
# Stop current backend (Ctrl+C)
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test File Upload

**Via UI:**
1. Go to http://localhost:3000
2. Login with: `admin@spartaai.com` / `admin123`
3. Click "Upload File" button
4. Select a CSV file
5. Should see success message

**Via API:**
```bash
# Get token first
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@spartaai.com","password":"admin123"}'

# Upload file (replace YOUR_TOKEN)
curl -X POST http://localhost:8000/api/v1/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@yourfile.csv"
```

### 3. Test AI Features

**Test AI Insights:**
```bash
# After uploading a file (replace file_id and token)
curl -X POST http://localhost:8000/api/v1/ai/auto-insights/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Test Chart Suggestions:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/chart-suggestions/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Test Natural Language:**
```bash
curl -X POST http://localhost:8000/api/v1/nl/nl-to-chart \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 1,
    "query": "show sales by region as a bar chart"
  }'
```

## Expected Results

### Upload Success:
```json
{
  "id": 1,
  "filename": "data.csv",
  "file_size": 12345,
  "file_type": "text/csv",
  "upload_time": "2025-01-16T10:30:00"
}
```

### AI Insights Success:
```json
{
  "insights": [
    {
      "type": "warning",
      "title": "High Missing Data in column_name",
      "description": "15.5% of values are missing",
      "action": "Consider imputation or removal"
    }
  ],
  "total_insights": 5
}
```

### Chart Suggestions Success:
```json
{
  "suggestions": [
    {
      "chart_type": "bar",
      "title": "Sales by Region",
      "x_column": "region",
      "y_column": "sales",
      "reason": "Compare sales across 5 categories",
      "confidence": 0.9
    }
  ]
}
```

## Troubleshooting

### Upload Still Fails

**Check uploads directory:**
```bash
cd backend
dir uploads
```

**Check file permissions:**
```bash
# Windows
icacls uploads
```

**Check backend logs:**
```bash
type logs\sparta_ai.log
```

### AI Still Not Working

**Verify Groq API key in .env:**
```bash
cd backend
type .env | findstr GROQ
```

Should show:
```
GROQ_API_KEY=your_api_key_here
```

**Test Groq API directly:**
```python
# test_groq.py
import os
from groq import Groq

client = Groq(api_key="your_groq_api_key_here")

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say hello"}]
)

print(response.choices[0].message.content)
```

Run: `python test_groq.py`

### Common Errors

**"Invalid token"**
- Login again to get fresh token
- Token expires after 30 minutes

**"File not found"**
- Check file_id is correct
- Verify file belongs to logged-in user

**"GROQ_API_KEY not configured"**
- Restart backend after adding to .env
- Verify .env file is in backend directory

**"Connection refused"**
- Backend not running
- Check port 8000 is not blocked

## Next Steps

Once upload and AI work:
1. Upload a CSV file with data
2. Go to Analytics page
3. See AI insights auto-generate
4. Try SQL queries
5. Generate charts
6. Transform data

All features should now work! 🎉
