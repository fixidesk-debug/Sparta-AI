# 🚀 SPARTA AI - Start Instructions

## ✅ Setup Complete!

Your database has been initialized successfully with:
- **Database**: SQLite (no PostgreSQL needed)
- **Admin Account**: 
  - Email: `admin@spartaai.com`
  - Password: `admin123`

## 🎯 How to Start SPARTA AI

### Step 1: Start Backend Server

Open a **new terminal** and run:

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or simply double-click: **`START_BACKEND.bat`**

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Start Frontend Server

Open **another terminal** and run:

```bash
cd frontend
npm run dev
```

Or simply double-click: **`START_FRONTEND.bat`**

You should see:
```
  ▲ Next.js 14.2.5
  - Local:        http://localhost:3000
  - Ready in 2.3s
```

### Step 3: Access the Application

Open your browser and go to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Step 4: Login

Use the default admin credentials:
- **Email**: `admin@spartaai.com`
- **Password**: `admin123`

## 📝 Quick Test

1. **Login** with admin credentials
2. **Upload a CSV file** (any CSV with data)
3. **Go to Analytics** page
4. **View AI Insights** (auto-generated)
5. **Try SQL Query**: `SELECT * FROM data LIMIT 10`
6. **Generate a Chart** from AI suggestions
7. **Transform Data** (rename/delete columns)

## 🔧 Configuration

### Database
Currently using **SQLite** (file: `backend/sparta_ai.db`)

To switch to PostgreSQL:
1. Install and start PostgreSQL
2. Edit `backend/.env`:
```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/sparta_db
```
3. Run `python init_db.py` again

### Groq API Key
Already configured in `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
```

This enables:
- AI chat responses
- Natural language queries
- Code generation
- Chart suggestions

## 🐛 Troubleshooting

### Backend won't start
```bash
# Make sure you're in the backend directory
cd backend

# Check if port 8000 is already in use
netstat -ano | findstr :8000

# If port is in use, kill the process or use different port:
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend won't start
```bash
# Make sure you're in the frontend directory
cd frontend

# Reinstall dependencies if needed
npm install

# Check if port 3000 is in use
netstat -ano | findstr :3000
```

### Database errors
```bash
# Reinitialize database
cd backend
python init_db.py
```

### File upload fails
```bash
# Create uploads directory
mkdir backend\uploads
```

## 📚 Next Steps

- Read [README.md](README.md) for full feature list
- Check [QUICKSTART.md](QUICKSTART.md) for usage examples
- Explore API docs at http://localhost:8000/docs
- Try uploading different file types (CSV, Excel, JSON)

## 🎉 You're Ready!

SPARTA AI is now fully configured and ready to use. Start both servers and begin analyzing your data!

---

**Need Help?**
- Check logs in `backend/logs/sparta_ai.log`
- Review browser console for frontend errors
- Verify both servers are running
