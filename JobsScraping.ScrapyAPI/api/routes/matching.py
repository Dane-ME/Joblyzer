from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from database.crud import CVCRUD, JobCRUD
from worker.tasks import process_job_matches
from ..schemas import JobMatchResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matching", tags=["job-matching"])

@router.post("/start/{cv_id}")
async def start_job_matching(cv_id: int, background_tasks: BackgroundTasks = None):
    """Start job matching process for CV"""
    try:
        # Start job matching task
        task = process_job_matches.delay(cv_id)
        
        return {
            "status": "success",
            "message": "Job matching started",
            "task_id": task.id,
            "cv_id": cv_id,
            "estimated_completion": "5-10 minutes"
        }
    except Exception as e:
        logger.error(f"Error starting job matching for CV {cv_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{task_id}")
async def get_matching_status(task_id: str):
    """Get status of job matching task"""
    try:
        from celery.result import AsyncResult
        result = AsyncResult(task_id)
        
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

@router.get("/results/{cv_id}", response_model=List[JobMatchResponse])
async def get_job_matches_for_cv(
    cv_id: int,
    min_score: float = Query(0.3, ge=0.0, le=1.0, description="Minimum match score"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results to return"),
    db: Session = Depends(get_db)
):
    """Get job matches for a specific CV"""
    try:
        # Check if CV exists
        cv = CVCRUD.get_cvs_by_user_id(db, cv_id)
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Get job matches from database
        from database.models import JobMatch
        matches = db.query(JobMatch).filter(
            JobMatch.cv_id == cv_id,
            JobMatch.match_score >= min_score
        ).order_by(JobMatch.match_score.desc()).limit(limit).all()
        
        return matches
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job matches for CV {cv_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/jobs/{job_id}/candidates")
async def get_cv_candidates_for_job(
    job_id: int,
    min_score: float = Query(0.3, ge=0.0, le=1.0, description="Minimum match score"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results to return"),
    db: Session = Depends(get_db)
):
    """Get CV candidates for a specific job"""
    try:
        # Check if job exists
        job = db.query(JobCRUD).filter(JobCRUD.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get CV candidates from database
        from database.models import JobMatch
        candidates = db.query(JobMatch).filter(
            JobMatch.job_id == job_id,
            JobMatch.match_score >= min_score
        ).order_by(JobMatch.match_score.desc()).limit(limit).all()
        
        return candidates
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CV candidates for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats/summary")
async def get_matching_stats(db: Session = Depends(get_db)):
    """Get job matching statistics"""
    try:
        from database.models import JobMatch
        
        total_matches = db.query(JobMatch).count()
        
        # Get matches by score range
        high_matches = db.query(JobMatch).filter(JobMatch.match_score >= 0.8).count()
        medium_matches = db.query(JobMatch).filter(
            JobMatch.match_score >= 0.5, 
            JobMatch.match_score < 0.8
        ).count()
        low_matches = db.query(JobMatch).filter(JobMatch.match_score < 0.5).count()
        
        # Get recent matches
        from datetime import datetime, timedelta
        recent_matches = db.query(JobMatch).filter(
            JobMatch.created_date >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            "total_matches": total_matches,
            "high_matches": high_matches,
            "medium_matches": medium_matches,
            "low_matches": low_matches,
            "recent_matches_7_days": recent_matches,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting matching stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/batch/process")
async def process_batch_matching(
    cv_ids: List[int],
    background_tasks: BackgroundTasks = None
):
    """Process job matching for multiple CVs"""
    try:
        if len(cv_ids) > 100:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 100 CVs allowed per batch"
            )
        
        # Start batch processing tasks
        task_ids = []
        for cv_id in cv_ids:
            task = process_job_matches.delay(cv_id)
            task_ids.append(task.id)
        
        return {
            "status": "success",
            "message": f"Batch matching started for {len(cv_ids)} CVs",
            "task_ids": task_ids,
            "cv_ids": cv_ids,
            "estimated_completion": f"{len(cv_ids) * 5}-{len(cv_ids) * 10} minutes"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting batch matching: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from database.crud import CVCRUD, UserCRUD
from ..schemas import CVCreate, CVResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cvs", tags=["cvs"])

@router.post("/", response_model=CVResponse)
async def create_cv(cv: CVCreate, db: Session = Depends(get_db)):
    """Create new CV"""
    try:
        # Check if user exists
        user = UserCRUD.get_user_by_id(db, cv.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user already has a CV
        existing_cv = CVCRUD.get_cvs_by_user_id(db, cv.user_id)
        if existing_cv:
            raise HTTPException(
                status_code=400, 
                detail="User already has a CV"
            )
        
        # Create CV
        cv_data = cv.dict()
        cv_data['created_date'] = datetime.utcnow()
        
        db_cv = CVCRUD.create_cv(db, cv_data)
        return db_cv
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating CV: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[CVResponse])
async def get_cvs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """Get all CVs with optional filtering"""
    try:
        if user_id:
            cv = CVCRUD.get_cvs_by_user_id(db, user_id)
            return [cv] if cv else []
        else:
            cvs = db.query(CVCRUD).offset(skip).limit(limit).all()
            return cvs
    except Exception as e:
        logger.error(f"Error getting CVs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{cv_id}", response_model=CVResponse)
async def get_cv(cv_id: int, db: Session = Depends(get_db)):
    """Get CV by ID"""
    try:
        cv = db.query(CVCRUD).filter(CVCRUD.id == cv_id).first()
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")
        return cv
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CV {cv_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}", response_model=CVResponse)
async def get_cv_by_user_id(user_id: int, db: Session = Depends(get_db)):
    """Get CV by user ID"""
    try:
        cv = CVCRUD.get_cvs_by_user_id(db, user_id)
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found for this user")
        return cv
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CV for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{cv_id}", response_model=CVResponse)
async def update_cv(
    cv_id: int, 
    cv_update: dict, 
    db: Session = Depends(get_db)
):
    """Update CV information"""
    try:
        # Check if CV exists
        existing_cv = db.query(CVCRUD).filter(CVCRUD.id == cv_id).first()
        if not existing_cv:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Update CV
        updated_cv = CVCRUD.update_cv(db, cv_id, cv_update)
        return updated_cv
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating CV {cv_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{cv_id}")
async def delete_cv(cv_id: int, db: Session = Depends(get_db)):
    """Delete CV"""
    try:
        # Check if CV exists
        existing_cv = db.query(CVCRUD).filter(CVCRUD.id == cv_id).first()
        if not existing_cv:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Delete CV
        db.delete(existing_cv)
        db.commit()
        
        return {
            "status": "success",
            "message": f"CV {cv_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting CV {cv_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats/summary")
async def get_cvs_stats(db: Session = Depends(get_db)):
    """Get CVs statistics summary"""
    try:
        total_cvs = db.query(CVCRUD).count()
        
        # Get CVs by creation date (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_cvs = db.query(CVCRUD).filter(
            CVCRUD.created_date >= thirty_days_ago
        ).count()
        
        return {
            "total_cvs": total_cvs,
            "recent_cvs_30_days": recent_cvs,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting CVs stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


