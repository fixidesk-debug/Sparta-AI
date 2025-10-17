# SPARTA AI - Data Analytics Platform

An AI-powered data analytics platform with conversational interface, code execution, and intelligent insights. Built with Next.js, FastAPI, and Python data science stack.

## ✅ Working Features

### Core Data Processing
- **File Upload & Processing**: CSV, Excel, JSON, Parquet support with automatic encoding detection
- **Data Preview**: Load and display data with pagination (up to 1000 rows per page)
- **Column Analysis**: Automatic data type detection, null counts, unique values
- **Data Quality Dashboard**: Visual overview of data completeness and quality

### AI-Powered Analysis
- **Auto-Generated Insights**: 
  - Missing data detection
  - Duplicate row identification
  - Outlier detection using IQR method
  - Skewness analysis
  - Correlation discovery
  - Categorical imbalance detection
- **Smart Chart Suggestions**: AI recommends chart types based on:
  - Time series detection (line charts)
  - Categorical vs numeric (bar charts)
  - Correlation strength (scatter plots)
  - Distribution analysis (pie charts, histograms)
- **Natural Language to Chart**: Parse plain English queries to generate chart configurations
- **Column Type Detection**: Smart suggestions for type conversions (datetime, numeric, boolean)

### Interactive Notebooks
- **Jupyter-style Interface**: Create, edit, and run code cells
- **Python Code Execution**: Safe sandboxed execution with timeout and memory limits
- **Cell Management**: Add, update, move, delete cells
- **Run All**: Execute entire notebook sequentially
- **Persistent Storage**: Save notebooks with metadata

### Statistical Analysis
- **Descriptive Statistics**: Mean, median, mode, std dev, quartiles
- **Hypothesis Testing**: T-tests, chi-square, ANOVA
- **Correlation Analysis**: Pearson, Spearman, Kendall
- **Regression**: Linear and multiple regression
- **Time Series**: Trend analysis, seasonality detection
- **Outlier Detection**: Z-score, IQR, isolation forest methods

### SQL Query Execution (WORKING)
- **DuckDB Integration**: Execute SQL queries on uploaded files
- **In-Memory Processing**: Fast query execution
- **Query Validation**: Syntax checking before execution
- **Results Display**: Query results shown in data table
- **Supports**: SELECT, WHERE, JOIN, GROUP BY, ORDER BY, etc.

### Data Transformations (WORKING)
- **Rename Columns**: Rename columns and persist changes
- **Delete Columns**: Remove columns from dataset
- **Cast Types**: Convert data types (int, float, string, datetime, bool)
- **Derive Columns**: Create calculated columns using formulas
- **File Persistence**: All changes saved back to file

### Interactive Visualizations (WORKING)
- **Chart Rendering**: Real charts with Recharts library
- **Chart Types**: Bar, Line, Scatter, Pie charts
- **Interactive**: Zoom, pan, hover tooltips
- **AI-Powered**: Generate from suggestions or natural language
- **Manual Builder**: Configure charts with drag-and-drop
- **Real Data**: Charts display actual uploaded data

### Real-time Features
- **WebSocket Chat**: Real-time conversational interface
- **Code Execution Streaming**: Live output during code execution
- **Connection Management**: Handle multiple concurrent connections

### Authentication & Security
- **JWT Authentication**: Secure token-based auth
- **User Registration/Login**: Email and password
- **Password Hashing**: Bcrypt with salt
- **Token Refresh**: Automatic token renewal
- **Rate Limiting**: 100 requests per minute
- **CORS Protection**: Configured origins
- **Security Headers**: XSS, clickjacking protection

## ❌ Missing Features (Compared to Julius AI)

### Not Implemented Yet
- **Version Control**: UI exists but no actual file versioning
- **Undo/Redo**: UI exists but no operation history tracking
- **Export Functionality**: No export to PDF, Excel, or images
- **Sharing**: UI exists but no actual sharing mechanism
- **Scheduled Reports**: Endpoint exists but not functional
- **ML Model Training**: Endpoints exist but limited functionality
- **Data Source Connectors**: No database or API connections
- **Collaborative Editing**: No real-time collaboration
- **Dashboard Builder**: No custom dashboard creation
- **Advanced Charts**: No heatmaps, box plots, violin plots, etc.
- **Data Filtering**: UI exists but not fully functional
- **Pivot Tables**: UI exists but not implemented

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **UI Library**: React 18 with TypeScript
- **Styling**: Tailwind CSS + Radix UI components
- **Charts**: Recharts (installed but not integrated)
- **State Management**: Zustand
- **Data Tables**: TanStack Table
- **HTTP Client**: Axios
- **Code Editor**: Monaco Editor
- **WebSocket**: Socket.io-client

### Backend
- **Framework**: FastAPI 0.115+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **SQL Engine**: DuckDB 0.9+ for in-memory analytics
- **Data Processing**: Pandas 2.2+, NumPy, SciPy
- **Statistics**: Statsmodels, Scikit-learn
- **Authentication**: JWT (python-jose) + Bcrypt
- **Code Execution**: Sandboxed Python execution
- **File Storage**: Local filesystem
- **WebSocket**: Native FastAPI WebSocket

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 14+
- Redis (for background tasks)
- Docker & Docker Compose (optional)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd sparta-ai
```

2. Set up environment variables:
```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env
```

3. Start with Docker Compose:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Installation

#### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
python init_db.py
```

4. Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open http://localhost:3000 in your browser

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/sparta_ai
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=100MB
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 📖 Usage Guide

### 1. Upload Data
- Click "Upload File" on dashboard or analytics page
- Select CSV, Excel, JSON, or Parquet file
- File is processed and stored in `uploads/` directory
- Preview shows first 1000 rows

### 2. View AI Insights (Working)
- After upload, insights are auto-generated
- See warnings for missing data, duplicates
- View outlier detection and correlation findings
- Get chart suggestions based on data types

### 3. Explore Data Table (Working)
- Navigate to Analytics → Data Table tab
- Browse paginated data (1000 rows per page)
- Click columns to see statistics
- View data quality dashboard

### 4. Use Notebooks (Working)
- Go to Notebooks page
- Create new notebook or open existing
- Write Python code in cells
- Execute code with real-time output
- Access uploaded data via pandas

### 5. Statistical Analysis (Working)
- Use API endpoints for:
  - Descriptive statistics
  - Hypothesis testing
  - Correlation analysis
  - Regression models
  - Time series analysis

### 6. Chat Interface (Working)
- Real-time WebSocket chat
- Ask questions about your data
- Get code suggestions
- Execute generated code

### What Doesn't Work Yet
- **Undo/Redo**: Buttons exist but no functionality
- **Export**: No actual export capability
- **Sharing**: UI exists but no backend
- **Version Control**: No file snapshots
- **Advanced Filtering**: Limited filter functionality

## 🔌 API Documentation

### ✅ Working Endpoints

#### Authentication
```bash
POST /api/v1/auth/register      # Create new user
POST /api/v1/auth/login         # Get JWT token
POST /api/v1/auth/refresh       # Refresh token
```

#### File Operations
```bash
POST /api/v1/files/upload                    # Upload file
GET /api/v1/files/{file_id}                  # Get file metadata
DELETE /api/v1/files/{file_id}               # Delete file
GET /api/v1/preview/files/{file_id}/data     # Get actual data (paginated)
GET /api/v1/preview/files/{file_id}/columns  # Get column info
```

#### SQL Queries (NEW - WORKING)
```bash
POST /api/v1/sql/execute                     # Execute SQL query with DuckDB
POST /api/v1/sql/validate                    # Validate SQL syntax
```

#### Data Transformations (NEW - WORKING)
```bash
POST /api/v1/transform/columns/rename        # Rename column
POST /api/v1/transform/columns/delete        # Delete column
POST /api/v1/transform/columns/cast          # Cast data type
POST /api/v1/transform/columns/derive        # Create derived column
```

#### AI Insights
```bash
POST /api/v1/ai/auto-insights/{file_id}      # Generate insights
POST /api/v1/ai/chart-suggestions/{file_id}  # Get chart recommendations
POST /api/v1/ai/detect-types/{file_id}       # Detect column types
POST /api/v1/nl/nl-to-chart                  # Parse natural language
```

#### Notebooks
```bash
POST /api/v1/notebooks/                      # Create notebook
GET /api/v1/notebooks/                       # List notebooks
GET /api/v1/notebooks/{id}                   # Get notebook
PUT /api/v1/notebooks/{id}                   # Update notebook
DELETE /api/v1/notebooks/{id}                # Delete notebook
POST /api/v1/notebooks/{id}/cells/{cell_id}/run  # Execute cell
```

#### Statistics
```bash
POST /api/v1/statistics/descriptive          # Basic stats
POST /api/v1/statistics/correlation          # Correlation matrix
POST /api/v1/statistics/hypothesis/ttest     # T-test
POST /api/v1/statistics/regression/linear    # Linear regression
POST /api/v1/statistics/outliers             # Detect outliers
```

#### WebSocket
```bash
WS /api/v1/ws/chat/{user_id}                 # Real-time chat
```

### ❌ Non-Functional Endpoints (Stubs Only)

```bash
POST /api/v1/history/*                       # Stub only
POST /api/v1/versions/*                      # Stub only
POST /api/v1/sharing/*                       # Stub only
POST /api/v1/reports/*                       # Stub only
```

Full API documentation: http://localhost:8000/docs

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚢 Deployment

### Production Build

#### Frontend
```bash
cd frontend
npm run build
npm start
```

#### Backend
```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Performance & Limitations

### Current Capabilities
- Handles files up to 100MB (configurable)
- Processes datasets with 1M+ rows using pandas
- Pagination: 1000 rows per page in UI
- Code execution: 30 second timeout, 512MB memory limit
- Chunked file reading for large CSVs (50,000 row chunks)
- Memory optimization with dtype downcasting

### Known Limitations
- No SQL query execution (DuckDB not integrated)
- Charts configured but not rendered
- Transformations don't persist to files
- No actual data versioning
- Single-user file storage (no multi-tenancy isolation)
- No distributed processing
- Limited to local file system storage

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- SQL injection prevention
- CORS configuration
- Rate limiting on API endpoints
- File upload validation
- Secure file storage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Documentation: [Link to docs]
- Issues: [GitHub Issues]
- Email: support@sparta-ai.com
- Discord: [Community Server]

## 🗺️ Roadmap - What Needs to Be Built

### High Priority (Core Functionality)
- [ ] **Chart Rendering**: Create ChartRenderer component to actually display charts
- [ ] **SQL Execution**: Integrate DuckDB for real SQL queries
- [ ] **Data Transformations**: Implement actual file modifications (rename, delete, derive columns)
- [ ] **Export**: Add PDF, Excel, PNG export functionality
- [ ] **Version Control**: Implement file versioning and snapshots
- [ ] **Undo/Redo**: Build operation history and rollback

### Medium Priority (Enhanced Features)
- [ ] **Sharing**: Implement share links and permissions
- [ ] **Scheduled Reports**: Build report generation and email delivery
- [ ] **Advanced Charts**: Add heatmaps, box plots, violin plots
- [ ] **Data Connectors**: PostgreSQL, MySQL, MongoDB connections
- [ ] **Dashboard Builder**: Custom dashboard creation
- [ ] **Collaborative Editing**: Real-time multi-user editing

### Low Priority (Nice to Have)
- [ ] **ML Model Training**: Full AutoML pipeline
- [ ] **Cloud Storage**: S3, GCS integration
- [ ] **Mobile App**: iOS/Android apps
- [ ] **Enterprise SSO**: SAML, OAuth integration
- [ ] **Data Pipeline**: ETL automation
- [ ] **Advanced Security**: Row-level security, audit logs

## 👥 Team

Built with ❤️ by the SPARTA AI team

## 🎯 Project Status

**Current State**: Fully functional MVP with data processing, SQL queries, visualizations, transformations, AI insights, and notebook execution all working with real data.

**Production Ready**: Partially - Core features work but missing collaboration, versioning, and export capabilities.

**Best For**: 
- Personal data analysis projects
- Learning full-stack data analytics architecture
- Prototyping data analysis workflows
- Educational purposes
- Building upon existing foundation

**Not Suitable For**:
- Enterprise production use (missing collaboration, audit logs)
- Teams needing real-time collaboration
- Users requiring advanced export formats
- Large-scale data processing (>100MB files)

## 🙏 Acknowledgments

- FastAPI for the Python framework
- Next.js and React teams
- Pandas, NumPy, SciPy for data processing
- Radix UI for component primitives
- TanStack Table for data tables
- All open-source contributors

---

**SPARTA AI** - An honest work-in-progress data analytics platform
