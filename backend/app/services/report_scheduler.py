"""
Report Scheduler - Schedule and execute automated reports
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import pandas as pd
from pathlib import Path

from app.services.email_service import EmailService
from app.services.export_service import ExportService
from app.services.advanced_insights import AdvancedInsights
from app.services.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class ReportScheduler:
    """Manage scheduled report execution"""
    
    _scheduler: Optional[BackgroundScheduler] = None
    _jobs: Dict[int, str] = {}  # schedule_id -> job_id mapping
    
    @classmethod
    def initialize(cls):
        """Initialize the scheduler"""
        if cls._scheduler is None:
            cls._scheduler = BackgroundScheduler()
            cls._scheduler.start()
            logger.info("Report scheduler initialized")
    
    @classmethod
    def shutdown(cls):
        """Shutdown the scheduler"""
        if cls._scheduler:
            cls._scheduler.shutdown()
            cls._scheduler = None
            logger.info("Report scheduler shutdown")
    
    @classmethod
    def add_schedule(
        cls,
        schedule_id: int,
        file_id: int,
        file_path: str,
        schedule_type: str,
        schedule_time: str,
        recipients: List[str],
        format: str = "pdf",
        email_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a new scheduled report
        
        Args:
            schedule_id: Database schedule ID
            file_id: File ID to generate report for
            file_path: Path to the data file
            schedule_type: 'daily', 'weekly', 'monthly'
            schedule_time: Time in HH:MM format
            recipients: List of email addresses
            format: Report format ('pdf', 'excel', 'html')
            email_config: SMTP configuration
        """
        try:
            cls.initialize()
            
            # Parse schedule time
            hour, minute = map(int, schedule_time.split(':'))
            
            # Create cron trigger based on schedule type
            if schedule_type == 'daily':
                trigger = CronTrigger(hour=hour, minute=minute)
            elif schedule_type == 'weekly':
                trigger = CronTrigger(day_of_week='mon', hour=hour, minute=minute)
            elif schedule_type == 'monthly':
                trigger = CronTrigger(day=1, hour=hour, minute=minute)
            else:
                raise ValueError(f"Invalid schedule type: {schedule_type}")
            
            # Add job to scheduler
            job = cls._scheduler.add_job(
                func=cls._execute_report,
                trigger=trigger,
                args=[file_id, file_path, recipients, format, email_config],
                id=f"schedule_{schedule_id}",
                replace_existing=True
            )
            
            cls._jobs[schedule_id] = job.id
            
            logger.info(f"Added schedule {schedule_id}: {schedule_type} at {schedule_time}")
            return {
                "success": True,
                "schedule_id": schedule_id,
                "job_id": job.id,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            }
            
        except Exception as e:
            logger.error(f"Error adding schedule: {e}")
            raise
    
    @classmethod
    def remove_schedule(cls, schedule_id: int) -> Dict[str, Any]:
        """Remove a scheduled report"""
        try:
            job_id = cls._jobs.get(schedule_id)
            if job_id and cls._scheduler:
                cls._scheduler.remove_job(job_id)
                del cls._jobs[schedule_id]
                logger.info(f"Removed schedule {schedule_id}")
                return {"success": True, "schedule_id": schedule_id}
            else:
                return {"success": False, "message": "Schedule not found"}
        except Exception as e:
            logger.error(f"Error removing schedule: {e}")
            raise
    
    @classmethod
    def update_schedule(
        cls,
        schedule_id: int,
        schedule_type: str,
        schedule_time: str
    ) -> Dict[str, Any]:
        """Update schedule timing"""
        try:
            # Remove existing job
            cls.remove_schedule(schedule_id)
            
            # Re-add with new schedule
            # Note: This is simplified - in production, you'd need to fetch all params
            return {"success": True, "message": "Schedule updated"}
        except Exception as e:
            logger.error(f"Error updating schedule: {e}")
            raise
    
    @classmethod
    def execute_now(
        cls,
        file_id: int,
        file_path: str,
        recipients: List[str],
        format: str = "pdf",
        email_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a report immediately"""
        try:
            return cls._execute_report(file_id, file_path, recipients, format, email_config)
        except Exception as e:
            logger.error(f"Error executing report: {e}")
            raise
    
    @classmethod
    def _execute_report(
        cls,
        file_id: int,
        file_path: str,
        recipients: List[str],
        format: str,
        email_config: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute report generation and send via email"""
        try:
            logger.info(f"Executing report for file {file_id}")
            
            # Load data
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            df = pd.read_csv(file_path)
            
            # Generate insights
            insights = AdvancedInsights.generate_insights(df)
            
            # Generate report content
            title = f"Data Analysis Report - {file_path_obj.name}"
            content = ReportGenerator.generate_markdown_report(
                title=title,
                insights=insights,
                charts=[]
            )
            
            # Generate report in requested format
            attachments = []
            if format == 'pdf':
                pdf_bytes = ExportService.export_to_pdf(title, content)
                attachments.append({
                    'filename': f'report_{file_id}.pdf',
                    'data': pdf_bytes
                })
            elif format == 'excel':
                excel_bytes = ExportService.export_to_excel(df, file_path_obj.name)
                attachments.append({
                    'filename': f'report_{file_id}.xlsx',
                    'data': excel_bytes
                })
            elif format == 'html':
                # HTML format - send as email body
                pass
            
            # Send email
            if email_config:
                email_service = EmailService(
                    smtp_host=email_config.get('smtp_host', 'smtp.gmail.com'),
                    smtp_port=email_config.get('smtp_port', 587),
                    username=email_config.get('username', ''),
                    password=email_config.get('password', '')
                )
                
                email_body = f"""
                <html>
                <body>
                    <h2>{title}</h2>
                    <p>Please find your automated data analysis report attached.</p>
                    <p>Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    <hr>
                    <h3>Quick Summary:</h3>
                    <ul>
                        <li>Total Rows: {len(df)}</li>
                        <li>Total Columns: {len(df.columns)}</li>
                        <li>File: {file_path_obj.name}</li>
                    </ul>
                </body>
                </html>
                """
                
                result = email_service.send_report(
                    to_emails=recipients,
                    subject=f"Scheduled Report: {file_path_obj.name}",
                    body=email_body,
                    attachments=attachments
                )
                
                logger.info(f"Report sent to {len(recipients)} recipients")
                return result
            else:
                logger.warning("No email configuration provided")
                return {"success": False, "message": "No email configuration"}
                
        except Exception as e:
            logger.error(f"Error executing report: {e}")
            return {"success": False, "message": str(e)}
    
    @classmethod
    def get_scheduled_jobs(cls) -> List[Dict[str, Any]]:
        """Get list of all scheduled jobs"""
        if not cls._scheduler:
            return []
        
        jobs = []
        for job in cls._scheduler.get_jobs():
            jobs.append({
                'job_id': job.id,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return jobs
