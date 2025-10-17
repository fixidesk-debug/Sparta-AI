"""
Scheduler Service - Scheduled Reports and Tasks
"""
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)


class SchedulerService:
    """Schedule automated reports and tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs = {}
    
    def start(self):
        """Start scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def stop(self):
        """Stop scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
    
    def schedule_report(
        self,
        job_id: str,
        func: Callable,
        schedule: str,
        args: tuple = (),
        kwargs: dict = None
    ) -> str:
        """
        Schedule a report
        
        Args:
            job_id: Unique job identifier
            func: Function to execute
            schedule: Cron expression (e.g., "0 9 * * *" for daily at 9am)
            args: Function arguments
            kwargs: Function keyword arguments
        """
        try:
            trigger = CronTrigger.from_crontab(schedule)
            
            job = self.scheduler.add_job(
                func,
                trigger=trigger,
                args=args,
                kwargs=kwargs or {},
                id=job_id,
                replace_existing=True
            )
            
            self.jobs[job_id] = {
                "schedule": schedule,
                "next_run": job.next_run_time,
                "created_at": datetime.now()
            }
            
            logger.info(f"Scheduled job {job_id}: {schedule}")
            return job_id
            
        except Exception as e:
            logger.error(f"Schedule error: {e}")
            raise
    
    def remove_job(self, job_id: str):
        """Remove scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            logger.info(f"Removed job {job_id}")
        except Exception as e:
            logger.error(f"Remove job error: {e}")
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "next_run": job.next_run_time,
                "trigger": str(job.trigger)
            })
        return jobs
    
    def pause_job(self, job_id: str):
        """Pause a job"""
        self.scheduler.pause_job(job_id)
    
    def resume_job(self, job_id: str):
        """Resume a job"""
        self.scheduler.resume_job(job_id)


# Global scheduler instance
scheduler_service = SchedulerService()
