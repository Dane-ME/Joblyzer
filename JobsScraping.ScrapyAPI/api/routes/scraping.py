from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from typing import List, Optional
from worker.tasks import scrape_jobs, schedule_scraping
from ..schemas import ScrapingJobCreate, ScrapingJobResponse
from database.db import get_db
from database.crud import ScrapingJobCRUD
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scraping", tags=["scraping"])

@router.post("/start", response_model=ScrapingJobResponse)
async def start_scraping(
    source: str = Query(..., description="Source to scrape from"),
    max_jobs: int = Query(50, ge=1, le=500, description="Maximum jobs to scrape"),
    background_tasks: BackgroundTasks = None
):
    """Start scraping jobs from specified source"""
    try:
        # Validate source
        valid_sources = ['topdev', 'vietnamwork', 'topcv', 'linkedin']
        if source not in valid_sources:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid source. Must be one of: {', '.join(valid_sources)}"
            )
        
        # Start scraping task
        task = scrape_jobs.delay(source, max_jobs)
        
        return {
            "id": 0,  # Will be updated when stored in DB
            "source": source,
            "status": "started",
            "task_id": task.id,
            "max_jobs": max_jobs,
            "started_at": None,
            "completed_at": None,
            "jobs_scraped": 0,
            "error_message": None,
            "created_at": "2024-01-01T00:00:00Z"  # Placeholder
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting scraping for {source}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/schedule")
async def schedule_scraping_jobs():
    """Schedule scraping for all sources"""
    try:
        task = schedule_scraping.delay()
        return {
            "status": "success",
            "message": "Scraping jobs scheduled for all sources",
            "task_id": task.id,
            "scheduled_sources": ['topdev', 'vietnamwork', 'topcv', 'linkedin']
        }
    except Exception as e:
        logger.error(f"Error scheduling scraping: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{task_id}")
async def get_scraping_status(task_id: str):
    """Get status of scraping task"""
    try:
        from celery.result import AsyncResult
        result = AsyncResult(task_id)
        
        # Get additional task info
        task_info = {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None,
            "date_done": result.date_done.isoformat() if result.date_done else None,
            "traceback": result.traceback if result.failed() else None
        }
        
        return task_info
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/jobs/history", response_model=List[ScrapingJobResponse])
async def get_scraping_history(
    source: Optional[str] = Query(None, description="Filter by source"),
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    db: Session = Depends(get_db)
):
    """Get scraping job history"""
    try:
        if source:
            jobs = ScrapingJobCRUD.get_recent_scraping_jobs(db, source, hours)
        else:
            # Get all recent scraping jobs
            from datetime import datetime, timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            jobs = db.query(ScrapingJobCRUD).filter(
                ScrapingJobCRUD.created_at >= cutoff_time
            ).order_by(ScrapingJobCRUD.created_at.desc()).all()
        
        return jobs
    except Exception as e:
        logger.error(f"Error getting scraping history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/sources/status")
async def get_sources_status():
    """Get current status of all scraping sources"""
    try:
        sources = ['topdev', 'vietnamwork', 'topcv', 'linkedin']
        status_info = {}
        
        for source in sources:
            # Check if there's an active scraping job
            from worker.celery_app import celery_app
            active_tasks = celery_app.control.inspect().active()
            
            source_status = "idle"
            if active_tasks:
                for worker, tasks in active_tasks.items():
                    for task in tasks:
                        if task['name'] == 'worker.tasks.scrape_jobs' and source in str(task['args']):
                            source_status = "running"
                            break
            
            status_info[source] = {
                "status": source_status,
                "last_scraped": "2024-01-01T00:00:00Z",  # Placeholder
                "jobs_count": 0  # Placeholder
            }
        
        return {
            "sources": status_info,
            "last_updated": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error getting sources status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/cancel/{task_id}")
async def cancel_scraping_task(task_id: str):
    """Cancel a running scraping task"""
    try:
        from worker.celery_app import celery_app
        celery_app.control.revoke(task_id, terminate=True)
        
        return {
            "status": "success",
            "message": f"Task {task_id} cancelled successfully"
        }
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/cancel/all")
async def cancel_all_scraping_tasks():
    """Cancel all running scraping tasks"""
    try:
        from worker.celery_app import celery_app
        
        # Lấy tất cả task đang hoạt động
        active_tasks = celery_app.control.inspect().active()
        
        cancelled_tasks = []
        if active_tasks:
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    if task['name'] == 'worker.tasks.scrape_jobs':
                        # Tắt task
                        celery_app.control.revoke(task['id'], terminate=True)
                        cancelled_tasks.append(task['id'])
        
        return {
            "status": "success",
            "message": f"Cancelled {len(cancelled_tasks)} active scraping tasks",
            "cancelled_task_ids": cancelled_tasks,
            "total_cancelled": len(cancelled_tasks)
        }
    except Exception as e:
        logger.error(f"Error cancelling all tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")