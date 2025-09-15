from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    
    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100))
    Email = Column(String(100), nullable=False, unique=True, index=True)
    Password = Column(String(255))
    PhoneNumber = Column(String(20))
    Address = Column(String(500))
    DateOfBirth = Column(DateTime)
    ProfilePictureUrl = Column(String(500))
    CreatedAt = Column(DateTime, default=func.getutcdate())
    UpdatedAt = Column(DateTime, default=func.getutcdate(), onupdate=func.getutcdate())
    Role = Column(String(50))
    
    # Relationships
    CVs = relationship("CV", back_populates="User")

class CV(Base):
    __tablename__ = "CVs"
    
    Id = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("Users.Id"), nullable=False)
    Summary = Column(String(2000))
    OCRText = Column(Text)  # Lưu kết quả OCR
    CVSource = Column(String(50))  # 'file', 'url', 'manual'
    OriginalFilename = Column(String(255))  # Tên file gốc
    CVUrl = Column(String(500))  # URL của CV nếu có
    CreatedDate = Column(DateTime, default=func.getutcdate())
    
    # Relationships
    User = relationship("User", back_populates="CVs")
    Skills = relationship("CVSkill", back_populates="CV")
    WorkExperiences = relationship("WorkExperience", back_populates="CV")
    Educations = relationship("Education", back_populates="CV")
    JobMatches = relationship("JobMatch", back_populates="CV")

class Skill(Base):
    __tablename__ = "Skills"
    
    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100), nullable=False, unique=True)
    Description = Column(String(500))
    
    # Relationships
    CVSkills = relationship("CVSkill", back_populates="Skill")

class CVSkill(Base):
    __tablename__ = "CVSkill"
    
    CVId = Column(Integer, ForeignKey("CVs.Id"), primary_key=True)
    SkillId = Column(Integer, ForeignKey("Skills.Id"), primary_key=True)
    
    # Relationships
    CV = relationship("CV", back_populates="Skills")
    Skill = relationship("Skill", back_populates="CVSkills")

class WorkExperience(Base):
    __tablename__ = "WorkExperiences"
    
    Id = Column(Integer, primary_key=True, index=True)
    CVId = Column(Integer, ForeignKey("CVs.Id"), nullable=False)
    JobTitle = Column(String(200), nullable=False)
    CompanyName = Column(String(200), nullable=False)
    Description = Column(String(2000))
    StartDate = Column(DateTime)
    EndDate = Column(DateTime)
    
    # Relationships
    CV = relationship("CV", back_populates="WorkExperiences")

class Education(Base):
    __tablename__ = "Education"
    
    Id = Column(Integer, primary_key=True, index=True)
    CVId = Column(Integer, ForeignKey("CVs.Id"), nullable=False)
    Degree = Column(String(200), nullable=False)
    Institution = Column(String(200), nullable=False)
    FieldOfStudy = Column(String(200))
    StartDate = Column(DateTime)
    EndDate = Column(DateTime)
    
    # Relationships
    CV = relationship("CV", back_populates="Educations")

class JobsDes(Base):
    __tablename__ = "JobsDes"
    
    Id = Column(Integer, primary_key=True, index=True)
    Title = Column(String(200), nullable=False)
    Company = Column(String(200), nullable=False)
    Location = Column(String(200))
    Description = Column(String(5000))
    Url = Column(String(500))
    PostedDate = Column(DateTime)
    JobType = Column(String(100))
    Salary = Column(String(100))
    ExperienceLevel = Column(String(100))
    Industry = Column(String(100))
    EmploymentType = Column(String(100))
    RequiredSkills = Column(String(1000))
    Benefits = Column(String(1000))
    Source = Column(String(100))
    RawContent = Column(Text)
    # Relationships
    JobMatches = relationship("JobMatch", back_populates="Job")

class JobMatch(Base):
    __tablename__ = "JobMatch"
    
    Id = Column(Integer, primary_key=True, index=True)
    CVId = Column(Integer, ForeignKey("CVs.Id"))
    JobId = Column(Integer, ForeignKey("JobsDes.Id"))
    MatchScore = Column(DECIMAL(5, 2))
    MatchedSkills = Column(String(1000))
    CreatedDate = Column(DateTime, default=func.getutcdate())
    
    # Relationships
    CV = relationship("CV", back_populates="JobMatches")
    Job = relationship("JobsDes", back_populates="JobMatches")

class ScrapingJob(Base):
    __tablename__ = "ScrapingJobs"
    
    Id = Column(Integer, primary_key=True, index=True)
    Source = Column(String(100), nullable=False)
    Status = Column(String(50), default="pending")  # pending, running, completed, failed
    StartedAt = Column(DateTime)
    CompletedAt = Column(DateTime)
    JobsScraped = Column(Integer, default=0)
    ErrorMessage = Column(Text)
    CreatedAt = Column(DateTime, default=func.getutcdate())