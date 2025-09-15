from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from database.crud import JobCRUD
from ..schemas import JobResponse, JobSearch, JobCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    source: Optional[str] = Query(None, description="Filter by job source"),
    location: Optional[str] = Query(None, description="Filter by job location"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    db: Session = Depends(get_db)
):
    """Get all jobs with optional filtering and pagination"""
    try:
        if source:
            jobs = JobCRUD.get_jobs_by_source(db, source, limit)
        else:
            # Get jobs with filters
            jobs = db.query(JobCRUD).offset(skip).limit(limit).all()
            
            # Apply additional filters if provided
            if location:
                jobs = [job for job in jobs if job.location and location.lower() in job.location.lower()]
            if industry:
                jobs = [job for job in jobs if job.industry and industry.lower() in job.industry.lower()]
        
        return jobs
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search", response_model=List[JobResponse])
async def search_jobs(
    query: str = Query(..., description="Search query"),
    source: Optional[str] = Query(None, description="Filter by job source"),
    location: Optional[str] = Query(None, description="Filter by location"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    experience_level: Optional[str] = Query(None, description="Filter by experience level"),
    db: Session = Depends(get_db)
):
    """Search jobs by query with optional filters"""
    try:
        jobs = JobCRUD.search_jobs(db, query, source)
        
        # Apply additional filters
        if location:
            jobs = [job for job in jobs if job.location and location.lower() in job.location.lower()]
        if industry:
            jobs = [job for job in jobs if job.industry and industry.lower() in job.industry.lower()]
        if experience_level:
            jobs = [job for job in jobs if job.experience_level and experience_level.lower() in job.experience_level.lower()]
        
        return jobs
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job by ID"""
    try:
        job = db.query(JobCRUD).filter(JobCRUD.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/source/{source}", response_model=List[JobResponse])
async def get_jobs_by_source(
    source: str,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get jobs by specific source"""
    try:
        jobs = JobCRUD.get_jobs_by_source(db, source, limit)
        return jobs
    except Exception as e:
        logger.error(f"Error getting jobs from source {source}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/recent/latest", response_model=List[JobResponse])
async def get_recent_jobs(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get most recent jobs within specified hours"""
    try:
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_jobs = db.query(JobCRUD).filter(
            JobCRUD.scraped_date >= cutoff_time
        ).order_by(JobCRUD.scraped_date.desc()).limit(limit).all()
        
        return recent_jobs
    except Exception as e:
        logger.error(f"Error getting recent jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats/summary")
async def get_jobs_stats(db: Session = Depends(get_db)):
    """Get jobs statistics summary"""
    try:
        total_jobs = db.query(JobCRUD).count()
        active_jobs = db.query(JobCRUD).filter(JobCRUD.is_active == True).count()
        
        # Get jobs by source
        sources = db.query(JobCRUD.source).distinct().all()
        source_stats = {}
        for source in sources:
            count = db.query(JobCRUD).filter(JobCRUD.source == source[0]).count()
            source_stats[source[0]] = count
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "sources": source_stats,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting jobs stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")