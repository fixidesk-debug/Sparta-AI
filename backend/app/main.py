"""
Sparta AI - Production-Ready FastAPI Application
A conversational data analysis platform with real-time chat, 
file processing, and code execution capabilities.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from typing import cast, Any
import logging

from app.api.v1.endpoints import auth, files, query, viz, exec, health, websocket, data, statistics, insights, export, datasources, ml_models, widgets
from app.api.v1.endpoints import validation
from app.api.v1.endpoints import notebooks
from app.api.v1.endpoints import data_catalog
from app.api.v1.endpoints import scheduled_reports, transformations, sharing, templates, ai_insights, nl_chart, history, versions, data_preview, sql_query
from app.api.v1.endpoints import enhanced_datasources
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.middleware import LoggingMiddleware, SecurityHeadersMiddleware, RateLimitMiddleware
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from app.db.session import engine
from app.db.models import Base
from app.services.websocket_manager import ws_manager

# Setup logging
import os
import sys
is_testing = "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv) or "PYTEST_CURRENT_TEST" in os.environ
setup_logging(log_level="INFO", log_file="logs/sparta_ai.log", enable_file_logging=not is_testing)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Sparta AI API...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Create upload directory
    from pathlib import Path
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    logger.info(f"Upload directory ensured: {upload_dir}")
    
    # Start WebSocket background tasks
    try:
        await ws_manager.start_background_tasks()
        logger.info("WebSocket background tasks started")
    except Exception as e:
        logger.error(f"Error starting WebSocket tasks: {e}")
    
    logger.info("Sparta AI API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sparta AI API...")
    
    # Stop WebSocket background tasks
    try:
        await ws_manager.stop_background_tasks()
        logger.info("WebSocket background tasks stopped")
    except Exception as e:
        logger.error(f"Error stopping WebSocket tasks: {e}")
    
    logger.info("Sparta AI API shutdown complete")


# Initialize FastAPI application
app = FastAPI(
    title="Sparta AI API",
    description="""
    ## Production-Ready Conversational Data Analysis Platform
    
    ### Features:
    - **Authentication**: JWT-based user authentication and authorization
    - **File Management**: Upload and manage CSV, Excel, and JSON files
    - **Natural Language Queries**: Ask questions about your data in plain English
    - **Code Generation**: Automatically generate Python code for data analysis
    - **Real-time Chat**: WebSocket-based chat interface for interactive analysis
    - **Visualizations**: Generate charts and graphs from your data
    - **Code Execution**: Safely execute generated Python code
    
    ### Security:
    - JWT token authentication
    - Rate limiting
    - CORS protection
    - Security headers
    - Input validation
    
    ### Architecture:
    - FastAPI for high-performance API
    - PostgreSQL for persistent storage
    - Redis for caching and session management
    - WebSocket for real-time communication
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware - must be added before other middleware
# Allow frontend to access backend API
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]
# Allow root-hosted frontend (nginx serving on default HTTP port)
allowed_origins.extend([
    "http://localhost",
    "http://127.0.0.1",
])
if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
    allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Custom middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# Exception handlers
app.add_exception_handler(AppException, cast(Any, app_exception_handler))
app.add_exception_handler(RequestValidationError, cast(Any, validation_exception_handler))
app.add_exception_handler(Exception, cast(Any, generic_exception_handler))

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(query.router, prefix="/api/v1/query", tags=["Query"])
app.include_router(viz.router, prefix="/api/v1/viz", tags=["Visualization"])
app.include_router(exec.router, prefix="/api/v1/exec", tags=["Execution"])
app.include_router(data.router, prefix="/api/v1/data", tags=["Data Processing"])
app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["Statistical Analysis"])
app.include_router(insights.router, prefix="/api/v1/insights", tags=["AI Insights"])
app.include_router(export.router, prefix="/api/v1/export", tags=["Export"])
app.include_router(datasources.router, prefix="/api/v1/datasources", tags=["Data Sources"])
app.include_router(enhanced_datasources.router, prefix="/api/v1/connectors", tags=["Enhanced Data Connectors"])
app.include_router(websocket.router, prefix="/api/v1/ws", tags=["WebSocket"])
app.include_router(ml_models.router, prefix="/api/v1/ml", tags=["ML Models"])
app.include_router(validation.router, prefix="/api/v1/validation", tags=["Validation"])
app.include_router(widgets.router, prefix="/api/v1/widgets", tags=["Widgets"])
app.include_router(data_catalog.router, prefix="/api/v1/catalog", tags=["Data Catalog"])
app.include_router(notebooks.router, prefix="/api/v1/notebooks", tags=["Notebooks"])
app.include_router(scheduled_reports.router, prefix="/api/v1/reports", tags=["Scheduled Reports"])
app.include_router(transformations.router, prefix="/api/v1/transform", tags=["Data Transformations"])
app.include_router(sharing.router, prefix="/api/v1/sharing", tags=["Sharing & Collaboration"])
app.include_router(templates.router, prefix="/api/v1/templates", tags=["Analysis Templates"])
app.include_router(ai_insights.router, prefix="/api/v1/ai", tags=["AI Insights"])
app.include_router(nl_chart.router, prefix="/api/v1/nl", tags=["Natural Language"])
app.include_router(history.router, prefix="/api/v1/history", tags=["Operation History"])
app.include_router(versions.router, prefix="/api/v1/versions", tags=["Data Versioning"])
app.include_router(data_preview.router, prefix="/api/v1/preview", tags=["Data Preview"])
app.include_router(sql_query.router, prefix="/api/v1/sql", tags=["SQL Execution"])

# API endpoint paths
DOCS_PATH = app.docs_url or "/docs"
HEALTH_PATH = "/health"


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Sparta AI API",
        "version": app.version,
        "docs": DOCS_PATH,
        "health": HEALTH_PATH
    }


@app.get("/api/v1/info")
async def api_info():
    """API information and capabilities"""
    # Use a configurable API base path to avoid hardcoded endpoint strings.
    base_path = getattr(settings, "API_V1_PREFIX", "/api/v1")
    endpoints = {
        "auth": f"{base_path}/auth",
        "files": f"{base_path}/files",
        "query": f"{base_path}/query",
        "chat": f"{base_path}/ws/chat",
        "health": "/health",
    }
    return {
        "name": "Sparta AI",
        "version": app.version,
        "description": "Conversational Data Analysis Platform",
        "features": [
            "User Authentication",
            "File Upload (CSV, Excel, JSON)",
            "Natural Language Queries",
            "Code Generation & Execution",
            "Real-time WebSocket Chat",
            "Data Visualization",
            "Redis Caching"
        ],
        "endpoints": endpoints
    }
