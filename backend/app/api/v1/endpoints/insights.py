"""
Insights API Endpoint - Automated Insights Generation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import pandas as pd

from app.db.session import get_db
from app.db.models import File
from app.core.security import get_current_user
from app.services.advanced_insights import AdvancedInsights
from app.services.report_generator import ReportGenerator
from app.services.data_transformation import DataTransformation
from app.services.chart_templates import ChartTemplates

router = APIRouter()


@router.get("/generate/{file_id}")
async def generate_insights(
    file_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate automated insights for a file"""
    
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user["id"]
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = pd.read_csv(file.file_path)
        insights = AdvancedInsights.generate_insights(df)
        
        return {
            "file_id": file_id,
            "insights": insights,
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")


@router.get("/transformations/{file_id}")
async def suggest_transformations(
    file_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transformation suggestions for a file"""
    
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user["id"]
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = pd.read_csv(file.file_path)
        suggestions = DataTransformation.suggest_transformations(df)
        
        return {
            "file_id": file_id,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/transform/{file_id}")
async def apply_transformation(
    file_id: int,
    transformation: Dict[str, Any],
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply a transformation to data"""
    
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user["id"]
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = pd.read_csv(file.file_path)
        df_transformed, message = DataTransformation.apply_transformation(df, transformation)
        
        return {
            "file_id": file_id,
            "message": message,
            "rows": len(df_transformed),
            "columns": len(df_transformed.columns),
            "preview": df_transformed.head(5).to_dict(orient='records')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/auto-clean/{file_id}")
async def auto_clean_data(
    file_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Automatically clean data"""
    
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user["id"]
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = pd.read_csv(file.file_path)
        df_clean, operations = DataTransformation.auto_clean(df)
        
        return {
            "file_id": file_id,
            "operations": operations,
            "before": {"rows": len(df), "columns": len(df.columns)},
            "after": {"rows": len(df_clean), "columns": len(df_clean.columns)},
            "preview": df_clean.head(5).to_dict(orient='records')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/chart-templates/{file_id}")
async def get_chart_templates(
    file_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chart template suggestions"""
    
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user["id"]
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = pd.read_csv(file.file_path)
        suggestions = ChartTemplates.get_template_suggestions(df)
        
        return {
            "file_id": file_id,
            "templates": ChartTemplates.TEMPLATES,
            "suggestions": suggestions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/report/{file_id}")
async def generate_report(
    file_id: int,
    format: str = "markdown",
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate analysis report"""
    
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user["id"]
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = pd.read_csv(file.file_path)
        insights = AdvancedInsights.generate_insights(df)
        
        if format == "markdown":
            report = ReportGenerator.generate_markdown_report(
                title=f"Analysis Report: {file.filename}",
                insights=insights,
                charts=[]
            )
        elif format == "html":
            report = ReportGenerator.generate_html_report(
                title=f"Analysis Report: {file.filename}",
                insights=insights,
                charts=[]
            )
        elif format == "json":
            report = ReportGenerator.generate_json_report(
                title=f"Analysis Report: {file.filename}",
                insights=insights,
                charts=[]
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
        
        return {
            "file_id": file_id,
            "format": format,
            "report": report
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
