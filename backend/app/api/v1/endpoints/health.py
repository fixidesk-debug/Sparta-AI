"""
Health check endpoints with dependency checking
"""
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Dict, Optional
import logging
from datetime import datetime, timezone

from app.db.session import get_db
from app.db.redis import get_redis

router = APIRouter()
logger = logging.getLogger(__name__)


class HealthStatus(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"
    dependencies: Optional[Dict[str, str]] = None


class DependencyStatus(BaseModel):
    database: str
    redis: str
    storage: str


@router.get("/health", response_model=HealthStatus, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint
    Returns 200 if service is running
    """
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get("/health/detailed", response_model=HealthStatus)
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with dependency status
    Checks database, Redis, and other services
    """
    dependencies = {
        "database": "unknown",
        "redis": "unknown",
        "storage": "unknown"
    }
    
    overall_status = "healthy"
    
    # Check database connection
    try:
        db.execute(text("SELECT 1"))
        dependencies["database"] = "healthy"
        logger.debug("Database health check: OK")
    except Exception as e:
        dependencies["database"] = "unhealthy"
        overall_status = "degraded"
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis connection
    try:
        redis_client = get_redis()
        redis_client.ping()
        dependencies["redis"] = "healthy"
        logger.debug("Redis health check: OK")
    except Exception as e:
        dependencies["redis"] = "unhealthy"
        overall_status = "degraded"
        logger.error(f"Redis health check failed: {e}")
    
    # Check file storage
    try:
        from pathlib import Path
        upload_dir = Path("uploads")
        if upload_dir.exists() and upload_dir.is_dir():
            dependencies["storage"] = "healthy"
        else:
            dependencies["storage"] = "unhealthy"
            overall_status = "degraded"
    except Exception as e:
        dependencies["storage"] = "unhealthy"
        overall_status = "degraded"
        logger.error(f"Storage health check failed: {e}")
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        dependencies=dependencies
    )


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe
    Returns 200 if the application is alive
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe
    Returns 200 if the application is ready to serve traffic
    """
    try:
        # Check if database is accessible
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not ready", "error": str(e)}
