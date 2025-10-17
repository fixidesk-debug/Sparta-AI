"""
Export API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from io import BytesIO

from app.db.session import get_db
from app.db.models import File
from app.core.security import get_current_user
from app.services.export_service import ExportService
from app.services.report_generator import ReportGenerator
from app.services.advanced_insights import AdvancedInsights
import pandas as pd

router = APIRouter()


@router.post("/pdf/{file_id}")
async def export_pdf(
    file_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export analysis to PDF"""
    file = db.query(File).filter(File.id == file_id, File.user_id == current_user["id"]).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = pd.read_csv(file.file_path)
        insights = AdvancedInsights.generate_insights(df)
        
        content = ReportGenerator.generate_markdown_report(
            title=f"Analysis: {file.filename}",
            insights=insights,
            charts=[]
        )
        
        pdf_bytes = ExportService.export_to_pdf(f"Analysis: {file.filename}", content)
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=analysis_{file_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/powerpoint/{file_id}")
async def export_powerpoint(
    file_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export analysis to PowerPoint"""
    file = db.query(File).filter(File.id == file_id, File.user_id == current_user["id"]).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = pd.read_csv(file.file_path)
        insights = AdvancedInsights.generate_insights(df)
        
        slides = [
            {"title": "Overview", "content": f"Dataset: {file.filename}\nRows: {len(df)}\nColumns: {len(df.columns)}"},
            {"title": "Key Findings", "content": "\n".join(insights.get("key_findings", []))},
            {"title": "Recommendations", "content": "\n".join(insights.get("recommendations", []))}
        ]
        
        pptx_bytes = ExportService.export_to_powerpoint(f"Analysis: {file.filename}", slides)
        
        return StreamingResponse(
            BytesIO(pptx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename=analysis_{file_id}.pptx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/word/{file_id}")
async def export_word(
    file_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export analysis to Word"""
    file = db.query(File).filter(File.id == file_id, File.user_id == current_user["id"]).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = pd.read_csv(file.file_path)
        insights = AdvancedInsights.generate_insights(df)
        
        content = ReportGenerator.generate_markdown_report(
            title=f"Analysis: {file.filename}",
            insights=insights,
            charts=[]
        )
        
        docx_bytes = ExportService.export_to_word(f"Analysis: {file.filename}", content)
        
        return StreamingResponse(
            BytesIO(docx_bytes),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=analysis_{file_id}.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/excel/{file_id}")
async def export_excel(
    file_id: int,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export data to Excel with formatting"""
    file = db.query(File).filter(File.id == file_id, File.user_id == current_user["id"]).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = pd.read_csv(file.file_path)
        
        # Create Excel file with formatting
        excel_bytes = ExportService.export_to_excel(df, file.filename)
        
        return StreamingResponse(
            BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={file.filename.replace('.csv', '.xlsx')}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/png/chart")
async def export_chart_png(
    chart_config: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Export chart as PNG image"""
    try:
        png_bytes = ExportService.export_chart_to_png(chart_config)
        
        return StreamingResponse(
            BytesIO(png_bytes),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=chart.png"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
