from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Job schemas
class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    posted_date: Optional[datetime] = None
    job_type: Optional[str] = None
    salary: Optional[str] = None
    experience_level: Optional[str] = None
    industry: Optional[str] = None
    employment_type: Optional[str] = None
    required_skills: Optional[str] = None
    benefits: Optional[str] = None
    raw_content: Optional[str] = None
    source: str

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    scraped_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class JobSearch(BaseModel):
    query: str
    source: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    experience_level: Optional[str] = None

# Scraping job schemas
class ScrapingJobBase(BaseModel):
    source: str
    max_jobs: int = 50

class ScrapingJobCreate(ScrapingJobBase):
    pass

class ScrapingJobResponse(ScrapingJobBase):
    id: int
    status: str
    task_id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    jobs_scraped: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    phone_number: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    profile_picture_url: Optional[str] = None
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# CV schemas
class CVBase(BaseModel):
    user_id: int
    summary: Optional[str] = None
    ocr_text: Optional[str] = None
    cv_source: Optional[str] = None
    original_filename: Optional[str] = None
    cv_url: Optional[str] = None

class CVCreate(CVBase):
    pass

class CVResponse(CVBase):
    id: int
    created_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        # Field mapping từ database columns sang response fields
        alias_generator = lambda string: string.lower() if string != 'Id' else 'id'

class CVUploadRequest(BaseModel):
    user_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    summary: Optional[str] = None
    cv_url: Optional[str] = None

# Job match schemas
class JobMatchBase(BaseModel):
    job_id: int
    cv_id: int
    match_score: Optional[Decimal] = None
    matched_skills: Optional[str] = None

class JobMatchCreate(JobMatchBase):
    pass

class JobMatchResponse(JobMatchBase):
    id: int
    created_date: datetime
    
    class Config:
        from_attributes = True