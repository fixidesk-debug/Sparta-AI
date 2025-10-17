"""
Scheduled Reports API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timezone

from app.db.session import get_db
from app.db.models import User, ScheduledReport, File as FileModel
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token
from app.services.report_scheduler import ReportScheduler

router = APIRouter()


class ReportSchedule(BaseModel):
    name: str
    description: Optional[str] = None
    analysis_id: int
    schedule_type: str  # daily, weekly, monthly
    schedule_time: str  # HH:MM format
    recipients: List[EmailStr]
    format: str = "pdf"  # pdf, html, csv
    is_active: bool = True


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/schedules")
async def create_schedule(
    schedule: ReportSchedule,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a scheduled report"""
    db_schedule = ScheduledReport(
        user_id=current_user.id,
        name=schedule.name,
        description=schedule.description,
        analysis_id=schedule.analysis_id,
        schedule_type=schedule.schedule_type,
        schedule_time=schedule.schedule_time,
        recipients=",".join(schedule.recipients),
        format=schedule.format,
        is_active=schedule.is_active
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule


@router.get("/schedules")
async def list_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all scheduled reports"""
    schedules = db.query(ScheduledReport).filter(
        ScheduledReport.user_id == current_user.id
    ).all()
    
    return schedules


@router.get("/schedules/{schedule_id}")
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific schedule"""
    schedule = db.query(ScheduledReport).filter(
        ScheduledReport.id == schedule_id,
        ScheduledReport.user_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return schedule


@router.put("/schedules/{schedule_id}")
async def update_schedule(
    schedule_id: int,
    schedule: ReportSchedule,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a scheduled report"""
    db_schedule = db.query(ScheduledReport).filter(
        ScheduledReport.id == schedule_id,
        ScheduledReport.user_id == current_user.id
    ).first()
    
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db_schedule.name = schedule.name
    db_schedule.description = schedule.description
    db_schedule.schedule_type = schedule.schedule_type
    db_schedule.schedule_time = schedule.schedule_time
    db_schedule.recipients = ",".join(schedule.recipients)
    db_schedule.format = schedule.format
    db_schedule.is_active = schedule.is_active
    
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a scheduled report"""
    schedule = db.query(ScheduledReport).filter(
        ScheduledReport.id == schedule_id,
        ScheduledReport.user_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    
    return {"message": "Schedule deleted"}


@router.post("/schedules/{schedule_id}/run")
async def run_schedule_now(
    schedule_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger a scheduled report"""
    schedule = db.query(ScheduledReport).filter(
        ScheduledReport.id == schedule_id,
        ScheduledReport.user_id == current_user.id
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Get file for the analysis
    file = db.query(FileModel).filter(
        FileModel.id == schedule.analysis_id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Execute report immediately
        recipients = schedule.recipients.split(',')
        result = ReportScheduler.execute_now(
            file_id=file.id,
            file_path=file.file_path,
            recipients=recipients,
            format=schedule.format,
            email_config=None  # TODO: Add email config from settings
        )
        
        schedule.last_run = datetime.now(timezone.utc)
        db.commit()
        
        return {
            "message": "Report generation completed",
            "success": result.get("success", False),
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
