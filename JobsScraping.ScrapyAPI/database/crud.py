from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional
from . import models
from datetime import datetime, timedelta

# Job CRUD operations
class JobCRUD:
    @staticmethod
    def create_job(db: Session, job_data: dict) -> models.JobsDes:
        db_job = models.JobsDes(**job_data)
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job
    
    @staticmethod
    def get_job_by_url(db: Session, url: str) -> Optional[models.JobsDes]:
        return db.query(models.JobsDes).filter(models.JobsDes.Url == url).first()
    
    @staticmethod
    def get_jobs_by_source(db: Session, source: str, limit: int = 100) -> List[models.JobsDes]:
        return db.query(models.JobsDes).filter(
            models.JobsDes.Source == source
        ).order_by(desc(models.JobsDes.PostedDate)).limit(limit).all()
    
    @staticmethod
    def search_jobs(db: Session, query: str, source: Optional[str] = None) -> List[models.JobsDes]:
        filters = [
            or_(
                models.JobsDes.Title.ilike(f"%{query}%"),
                models.JobsDes.Description.ilike(f"%{query}%"),
                models.JobsDes.Company.ilike(f"%{query}%"),
                models.JobsDes.RequiredSkills.ilike(f"%{query}%")
            )
        ]
        
        if source:
            filters.append(models.JobsDes.Source == source)
        
        return db.query(models.JobsDes).filter(and_(*filters)).order_by(desc(models.JobsDes.PostedDate)).all()
    
    @staticmethod
    def update_job(db: Session, job_id: int, job_data: dict) -> Optional[models.JobsDes]:
        db_job = db.query(models.JobsDes).filter(models.JobsDes.Id == job_id).first()
        if db_job:
            for key, value in job_data.items():
                setattr(db_job, key, value)
            db.commit()
            db.refresh(db_job)
        return db_job

# ScrapingJob CRUD operations
class ScrapingJobCRUD:
    @staticmethod
    def create_scraping_job(db: Session, source: str) -> models.ScrapingJob:
        db_job = models.ScrapingJob(Source=source, Status="pending")
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return db_job
    
    @staticmethod
    def update_scraping_job_status(db: Session, job_id: int, status: str, **kwargs) -> Optional[models.ScrapingJob]:
        db_job = db.query(models.ScrapingJob).filter(models.ScrapingJob.Id == job_id).first()
        if db_job:
            db_job.Status = status
            for key, value in kwargs.items():
                setattr(db_job, key, value)
            db.commit()
            db.refresh(db_job)
        return db_job
    
    @staticmethod
    def get_recent_scraping_jobs(db: Session, source: str, hours: int = 24) -> List[models.ScrapingJob]:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(models.ScrapingJob).filter(
            models.ScrapingJob.Source == source,
            models.ScrapingJob.CreatedAt >= cutoff_time
        ).order_by(desc(models.ScrapingJob.CreatedAt)).all()

# CV and User CRUD operations
class CVCRUD:
    @staticmethod
    def create_cv(db: Session, cv_data: dict) -> models.CV:
        db_cv = models.CV(**cv_data)
        db.add(db_cv)
        db.commit()
        db.refresh(db_cv)
        return db_cv
    
    @staticmethod
    def get_cvs_by_user_id(db: Session, user_id: int) -> Optional[models.CV]:
        return db.query(models.CV).where(models.CV.UserId == user_id).all()
    
    @staticmethod
    def update_cv(db: Session, cv_id: int, cv_data: dict) -> Optional[models.CV]:
        db_cv = db.query(models.CV).filter(models.CV.Id == cv_id).first()
        if db_cv:
            for key, value in cv_data.items():
                setattr(db_cv, key, value)
            db.commit()
            db.refresh(db_cv)
        return db_cv
    @staticmethod
    def get_cv_with_ocr(db: Session, cv_id: int) -> Optional[models.CV]:
        """Lấy CV với thông tin OCR"""
        return db.query(models.CV).filter(models.CV.Id == cv_id).first()
    
    @staticmethod
    def get_cv_by_id(db: Session, cv_id: int) -> Optional[models.CV]:
        """Lấy CV theo ID"""
        return db.query(models.CV).filter(models.CV.Id == cv_id).first()
    
    @staticmethod
    def get_cv_stats(db: Session) -> dict:
        """Lấy thống kê CV"""
        total_cvs = db.query(models.CV).count()
        
        # Get CVs by creation date (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_cvs = db.query(models.CV).filter(
            models.CV.CreatedDate >= thirty_days_ago
        ).count()
        
        return {
            "total_cvs": total_cvs,
            "recent_cvs_30_days": recent_cvs
        }

class UserCRUD:
    @staticmethod
    def create_user(db: Session, user_data: dict) -> models.User:
        db_user = models.User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.Email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.Id == user_id).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: dict) -> Optional[models.User]:
        db_user = db.query(models.User).filter(models.User.Id == user_id).first()
        if db_user:
            for key, value in user_data.items():
                setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
        return db_user