"""
Analysis Templates API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.db.session import get_db
from app.db.models import User, AnalysisTemplate
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token

router = APIRouter()


class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    config: Dict[str, Any]
    is_public: bool = False


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


# Pre-built templates
BUILTIN_TEMPLATES = [
    {
        "id": "sales_analysis",
        "name": "Sales Analysis",
        "description": "Analyze sales trends, top products, and revenue patterns",
        "category": "business",
        "config": {
            "charts": ["line", "bar", "pie"],
            "metrics": ["total_sales", "avg_order_value", "conversion_rate"],
            "time_grouping": "monthly"
        }
    },
    {
        "id": "customer_segmentation",
        "name": "Customer Segmentation",
        "description": "Segment customers using RFM analysis and clustering",
        "category": "marketing",
        "config": {
            "algorithm": "kmeans",
            "features": ["recency", "frequency", "monetary"],
            "n_clusters": 4
        }
    },
    {
        "id": "time_series_forecast",
        "name": "Time Series Forecasting",
        "description": "Forecast future values using ARIMA or Prophet",
        "category": "forecasting",
        "config": {
            "model": "arima",
            "forecast_periods": 12,
            "confidence_interval": 0.95
        }
    },
    {
        "id": "ab_test",
        "name": "A/B Test Analysis",
        "description": "Statistical analysis of A/B test results",
        "category": "experimentation",
        "config": {
            "test_type": "t_test",
            "metrics": ["conversion_rate", "revenue_per_user"],
            "confidence_level": 0.95
        }
    },
    {
        "id": "cohort_analysis",
        "name": "Cohort Analysis",
        "description": "Analyze user retention and behavior over time",
        "category": "analytics",
        "config": {
            "cohort_type": "acquisition",
            "time_period": "weekly",
            "metrics": ["retention_rate", "ltv"]
        }
    },
    {
        "id": "correlation_matrix",
        "name": "Correlation Analysis",
        "description": "Find correlations between variables",
        "category": "statistics",
        "config": {
            "method": "pearson",
            "visualization": "heatmap",
            "threshold": 0.5
        }
    }
]


@router.get("/templates")
async def list_templates(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all available templates"""
    templates = BUILTIN_TEMPLATES.copy()
    
    # Add user's custom templates
    user_templates = db.query(AnalysisTemplate).filter(
        (AnalysisTemplate.user_id == current_user.id) | (AnalysisTemplate.is_public == True)
    ).all()
    
    for template in user_templates:
        templates.append({
            "id": str(template.id),
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "config": template.config,
            "is_custom": True
        })
    
    if category:
        templates = [t for t in templates if t["category"] == category]
    
    return {"templates": templates}


@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific template"""
    # Check built-in templates
    builtin = next((t for t in BUILTIN_TEMPLATES if t["id"] == template_id), None)
    if builtin:
        return builtin
    
    # Check custom templates
    template = db.query(AnalysisTemplate).filter(
        AnalysisTemplate.id == int(template_id)
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "id": str(template.id),
        "name": template.name,
        "description": template.description,
        "category": template.category,
        "config": template.config
    }


@router.post("/templates")
async def create_template(
    template: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a custom template"""
    db_template = AnalysisTemplate(
        user_id=current_user.id,
        name=template.name,
        description=template.description,
        category=template.category,
        config=template.config,
        is_public=template.is_public
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template


@router.post("/templates/{template_id}/apply")
async def apply_template(
    template_id: str,
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply a template to a dataset"""
    # Get template
    template = await get_template(template_id, current_user, db)
    
    # TODO: Apply template configuration to the dataset
    # This would trigger the appropriate analysis based on template config
    
    return {
        "message": "Template applied successfully",
        "template_id": template_id,
        "file_id": file_id,
        "config": template["config"]
    }
