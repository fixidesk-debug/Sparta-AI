# 🚀 START HERE - SPARTA AI Quick Launch

## ✅ Everything is Ready!

All issues have been fixed:
- ✅ Database initialized (SQLite)
- ✅ Groq API configured and tested
- ✅ Uploads directory created
- ✅ All dependencies installed
- ✅ Admin account created
- ✅ Test data prepared

## 🎯 Launch in 3 Steps

### Step 1: Start Backend (Terminal 1)

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Or double-click:** `START_BACKEND.bat`

**Wait for:**
```
INFO:     Application startup complete.
```

### Step 2: Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

**Or double-click:** `START_FRONTEND.bat`

**Wait for:**
```
✓ Ready in 2.3s
Local: http://localhost:3000
```

### Step 3: Open Browser

Go to: **http://localhost:3000**

## 🔐 Login

**Admin Credentials:**
- Email: `admin@spartaai.com`
- Password: `admin123`

## 🧪 Test Everything (5 minutes)

### 1. Upload Test File
- Click "Upload File"
- Select `backend/test_data.csv`
- Wait for success message

### 2. View AI Insights
- Insights auto-generate after upload
- See warnings, outliers, correlations
- Check data quality dashboard

### 3. Generate Charts
- Go to **Analytics** → **Charts** tab
- Click an AI suggestion (e.g., "Sales by Region")
- See rendered bar chart with real data

### 4. Run SQL Query
- Go to **SQL** tab
- Try: `SELECT product, SUM(sales) as total FROM data GROUP BY product`
- Click "Run Query"
- See aggregated results

### 5. Transform Data
- Go to **Transform** tab
- Rename a column (e.g., "sales" → "revenue")
- Changes persist to file

### 6. Use Notebooks
- Go to **Notebooks** page
- Create new notebook
- Write code:
```python
import pandas as pd
df = pd.read_csv('uploads/test_data.csv')
print(df.describe())
```
- Click "Run"
- See output

## 📊 Sample Queries to Try

### SQL Queries:
```sql
-- Total sales by region
SELECT region, SUM(sales) as total_sales 
FROM data 
GROUP BY region 
ORDER BY total_sales DESC;

-- Average quantity by product
SELECT product, AVG(quantity) as avg_qty 
FROM data 
GROUP BY product;

-- Sales over time
SELECT date, SUM(sales) as daily_sales 
FROM data 
GROUP BY date 
ORDER BY date;
```

### Natural Language:
- "show sales by product as a bar chart"
- "create a line chart of sales over time"
- "display quantity by region as a pie chart"

## 🎨 Features to Explore

### Data Analysis
- ✅ Upload CSV, Excel, JSON files
- ✅ View data in interactive tables
- ✅ Check data quality metrics
- ✅ Get AI-powered insights

### Visualizations
- ✅ Bar, Line, Scatter, Pie charts
- ✅ AI chart suggestions
- ✅ Natural language to chart
- ✅ Interactive chart builder

### Data Manipulation
- ✅ SQL queries with DuckDB
- ✅ Column transformations
- ✅ Data type conversions
- ✅ Derived columns

### Advanced Features
- ✅ Python notebooks
- ✅ Statistical analysis
- ✅ Real-time chat
- ✅ Code execution

## 🔧 Quick Commands

### Verify Setup:
```bash
cd backend
python test_setup.py
```

### Check Backend Status:
```bash
curl http://localhost:8000/health
```

### Check Frontend Status:
```bash
curl http://localhost:3000
```

### View Logs:
```bash
type backend\logs\sparta_ai.log
```

## 📚 Documentation

- **Full README**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Fixed Issues**: [FIXED_ISSUES.md](FIXED_ISSUES.md)
- **Test Guide**: [TEST_UPLOAD.md](TEST_UPLOAD.md)
- **Implementation**: [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

## 🆘 Troubleshooting

### Backend Issues:
```bash
# Port already in use
netstat -ano | findstr :8000

# Restart backend
# Press Ctrl+C, then run again
```

### Frontend Issues:
```bash
# Port already in use
netstat -ano | findstr :3000

# Clear cache and restart
cd frontend
rm -rf .next
npm run dev
```

### Database Issues:
```bash
cd backend
python init_db.py
```

### Upload Issues:
```bash
# Check directory exists
dir backend\uploads

# Create if missing
mkdir backend\uploads
```

## ✨ What Makes SPARTA AI Special

1. **Real AI Integration** - Groq API for fast, intelligent analysis
2. **SQL on Files** - Query CSV/Excel with DuckDB (no database needed)
3. **Live Charts** - Recharts renders beautiful, interactive visualizations
4. **Smart Insights** - Auto-detect patterns, outliers, correlations
5. **Natural Language** - Ask questions in plain English
6. **Python Notebooks** - Execute code with real-time output
7. **Data Transformations** - Modify files directly
8. **No Mock Data** - Everything uses real data and APIs

## 🎉 You're All Set!

SPARTA AI is fully configured and ready to analyze your data.

**Start both servers and begin exploring!**

---

**Questions?** Check the documentation files or API docs at http://localhost:8000/docs
