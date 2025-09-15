from celery import current_task
from worker.celery_app import celery_app
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='worker.tasks.scrape_jobs')
def scrape_jobs(self, source: str, max_jobs: int = 50) -> Dict[str, Any]:
    """
    Scrape jobs from specified source using Scrapy
    """
    try:
        # Update task status
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': max_jobs, 'status': 'Starting scraping...'}
        )
        
        # Get absolute project path - FIX HERE
        current_file = os.path.abspath(__file__)  # worker/tasks.py
        worker_dir = os.path.dirname(current_file)  # worker/
        project_path = os.path.dirname(worker_dir)  # JobsScraping.ScrapyAPI/
        
        # Create output directory
        output_dir = os.path.join(project_path, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        
        # Build Scrapy command
        output_file = os.path.join(output_dir, f'{source}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        
        cmd = [
            sys.executable, '-m', 'scrapy', 'crawl', source,
            '-s', f'CLOSESPIDER_ITEMCOUNT={max_jobs}',
            '-s', 'LOG_LEVEL=INFO',
            '-o', output_file,
            '--nolog'
        ]
        
        logger.info(f"Starting Scrapy crawl for {source}")
        logger.info(f"Command: {' '.join(cmd)}")
        logger.info(f"Working directory: {project_path}")
        logger.info(f"Output file: {output_file}")
        
        # Execute Scrapy command
        process = subprocess.Popen(
            cmd,
            cwd=project_path,  # Set working directory to project root
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False
        )
        
        # Wait for process to complete
        stdout, stderr = process.communicate()
        return_code = process.returncode
        
        logger.info(f"Scrapy stdout: {stdout}")
        logger.info(f"Scrapy stderr: {stderr}")
        logger.info(f"Scrapy return code: {return_code}")
        
        if return_code == 0:
            logger.info(f"Successfully scraped jobs from {source}")
            return {
                'status': 'success',
                'source': source,
                'jobs_scraped': max_jobs,
                'completed_at': datetime.utcnow().isoformat()
            }
        else:
            error_msg = f"Scrapy failed with return code {return_code}. Stderr: {stderr}"
            logger.error(error_msg)
            raise Exception(error_msg)
            
    except Exception as e:
        logger.error(f"Error in scrape_jobs task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='worker.tasks.process_job_matches')
def process_job_matches(self, cv_id: int) -> Dict[str, Any]:
    """
    Process job matches for a specific CV
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Processing job matches...'}
        )
        
        # Import here to avoid circular imports
        from database.db import get_db_context
        from database.crud import JobCRUD, CVCRUD
        
        with get_db_context() as db:
            # Get CV
            cv = CVCRUD.get_cvs_by_user_id(db, cv_id)
            if not cv:
                raise Exception(f"CV not found for user {cv_id}")
            
            # Get all active jobs
            jobs = JobCRUD.search_jobs(db, "", limit=1000)
            
            # Calculate match scores
            matches = []
            for job in jobs:
                match_score = calculate_match_score(cv, job)
                if match_score > 0.3:  # Only include matches > 30%
                    matches.append({
                        'job_id': job.id,
                        'cv_id': cv.id,
                        'match_score': match_score,
                        'matched_skills': get_matched_skills(cv, job),
                        'matched_experience': get_matched_experience(cv, job)
                    })
            
            # Sort by match score
            matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            logger.info(f"Found {len(matches)} job matches for CV {cv_id}")
            
            return {
                'status': 'success',
                'cv_id': cv_id,
                'matches_found': len(matches),
                'top_matches': matches[:10]  # Return top 10 matches
            }
            
    except Exception as e:
        logger.error(f"Error in process_job_matches task: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name='worker.tasks.schedule_scraping')
def schedule_scraping(self) -> Dict[str, Any]:
    """
    Schedule scraping jobs for all sources
    """
    try:
        sources = ['topdev', 'vietnamwork', 'topcv', 'linkedin']
        scheduled_tasks = []
        
        for source in sources:
            # Schedule scraping task
            task = scrape_jobs.delay(source, max_jobs=50)
            scheduled_tasks.append({
                'source': source,
                'task_id': task.id,
                'status': 'scheduled'
            })
        
        logger.info(f"Scheduled {len(scheduled_tasks)} scraping tasks")
        
        return {
            'status': 'success',
            'tasks_scheduled': len(scheduled_tasks),
            'scheduled_tasks': scheduled_tasks
        }
        
    except Exception as e:
        logger.error(f"Error in schedule_scraping task: {e}")
        raise

def calculate_match_score(cv, job) -> float:
    """Calculate match score between CV and job"""
    score = 0.0
    total_criteria = 0
    
    # Skill match (40% weight)
    if cv.skills and job.required_skills:
        skill_match = len(set(skill.name.lower() for skill in cv.skills) & 
                         set(job.required_skills.lower().split(',')))
        total_skills = len(job.required_skills.split(','))
        if total_skills > 0:
            score += (skill_match / total_skills) * 0.4
        total_criteria += 1
    
    # Experience match (30% weight)
    if cv.work_experiences and job.experience_level:
        # Add experience matching logic
        score += 0.3
        total_criteria += 1
    
    # Location match (20% weight)
    if cv.address and job.location:
        if cv.address.lower() in job.location.lower() or job.location.lower() in cv.address.lower():
            score += 0.2
        total_criteria += 1
    
    # Industry match (10% weight)
    # Add industry matching logic
    score += 0.1
    total_criteria += 1
    
    return score / total_criteria if total_criteria > 0 else 0.0

def get_matched_skills(cv, job) -> str:
    """Get matched skills between CV and job"""
    if not cv.skills or not job.required_skills:
        return ""
    
    cv_skills = set(skill.name.lower() for skill in cv.skills)
    job_skills = set(skill.strip().lower() for skill in job.required_skills.split(','))
    matched = cv_skills & job_skills
    
    return ", ".join(matched)

def get_matched_experience(cv, job) -> str:
    """Get matched experience between CV and job"""
    # Add experience matching logic
    return "Experience matching logic to be implemented"