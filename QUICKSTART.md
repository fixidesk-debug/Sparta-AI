# 🚀 SPARTA AI - Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for caching)

## Installation (5 minutes)

### 1. Clone and Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python init_db.py

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## First Steps (2 minutes)

### 1. Create Account
- Go to http://localhost:3000
- Click "Sign Up"
- Enter email and password
- Login with credentials

### 2. Upload Data
- Click "Upload File" button
- Select a CSV, Excel, or JSON file
- Wait for processing (usually <5 seconds)

### 3. Explore Features

#### View Data
- Go to **Analytics** page
- Click **Data Table** tab
- Browse your data with pagination

#### Get AI Insights
- Insights auto-generate after upload
- See missing data warnings
- View outlier detection
- Check correlation findings

#### Run SQL Queries
- Go to **SQL** tab
- Try: `SELECT * FROM data LIMIT 10`
- Click "Run Query"
- See results in table

#### Create Charts
- Go to **Charts** tab
- Click an AI suggestion, or
- Use Chart Builder to configure manually
- Select chart type, X-axis, Y-axis
- Click "Generate Chart"
- See rendered visualization

#### Transform Data
- Go to **Transform** tab
- Rename a column
- Delete a column
- Create derived column
- Changes persist to file

#### Use Notebooks
- Go to **Notebooks** page
- Create new notebook
- Write Python code:
```python
import pandas as pd
df = pd.read_csv('uploads/your_file.csv')
print(df.head())
```
- Click "Run" to execute

## Example Workflows

### Workflow 1: Sales Analysis
```
1. Upload sales.csv
2. View AI insights (check for missing data)
3. SQL: SELECT product, SUM(revenue) FROM data GROUP BY product
4. Create bar chart: product vs revenue
5. Transform: Derive column "profit = revenue - cost"
6. Create scatter plot: revenue vs profit
```

### Workflow 2: Customer Segmentation
```
1. Upload customers.csv
2. Check data quality dashboard
3. SQL: SELECT age_group, COUNT(*) FROM data GROUP BY age_group
4. Create pie chart: customer distribution by age
5. Use notebook for clustering analysis
6. Export results (coming soon)
```

### Workflow 3: Time Series Analysis
```
1. Upload timeseries.csv with date column
2. AI suggests line chart automatically
3. Create line chart: date vs value
4. SQL: SELECT date, AVG(value) FROM data GROUP BY date
5. Check for trends and seasonality
```

## API Examples

### Upload File
```bash
curl -X POST http://localhost:8000/api/v1/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.csv"
```

### Execute SQL Query
```bash
curl -X POST http://localhost:8000/api/v1/sql/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 1,
    "query": "SELECT * FROM data LIMIT 10"
  }'
```

### Get AI Insights
```bash
curl -X POST http://localhost:8000/api/v1/ai/auto-insights/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Transform Data
```bash
curl -X POST http://localhost:8000/api/v1/transform/columns/rename \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": 1,
    "old_name": "col1",
    "new_name": "column_1"
  }'
```

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check if port 8000 is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Mac/Linux

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port 3000 is in use
netstat -ano | findstr :3000  # Windows
lsof -i :3000  # Mac/Linux
```

### Database connection error
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Update .env file with correct credentials
DATABASE_URL=postgresql://user:password@localhost:5432/sparta_ai
```

### File upload fails
```bash
# Check uploads directory exists
mkdir -p uploads

# Check file permissions
chmod 755 uploads

# Check file size (max 100MB by default)
```

### SQL queries fail
```bash
# Install DuckDB
pip install duckdb

# Check file exists
ls uploads/

# Try simple query first
SELECT * FROM data LIMIT 1
```

## Performance Tips

1. **Large Files**: Use SQL queries instead of loading all data
2. **Charts**: Limit data points to 10,000 for smooth rendering
3. **Transformations**: Work on sampled data first, then apply to full dataset
4. **Notebooks**: Use chunked processing for large datasets

## Next Steps

- Read full [README.md](README.md) for detailed features
- Check [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) for technical details
- Explore API docs at http://localhost:8000/docs
- Join community (coming soon)

## Getting Help

- Check API documentation: http://localhost:8000/docs
- Review error logs in `logs/sparta_ai.log`
- Check browser console for frontend errors
- Verify backend logs in terminal

## Common Issues

**Q: Charts not rendering?**  
A: Make sure Recharts is installed: `npm install recharts`

**Q: SQL queries timeout?**  
A: DuckDB is fast, but very large files may take time. Try LIMIT clause.

**Q: Transformations not persisting?**  
A: Check file permissions in uploads/ directory

**Q: AI insights not generating?**  
A: Ensure file has at least 10 rows and valid data types

**Q: WebSocket connection fails?**  
A: Check CORS settings and ensure backend is running

---

**Ready to analyze data!** 🎉

Start with a simple CSV file and explore the features. The platform learns from your usage patterns and provides better suggestions over time.
