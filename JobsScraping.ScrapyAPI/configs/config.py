import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database Configuration
DATABASE_CONFIG = {
    "default": {
        "url": "mssql+pyodbc://dang:dangevil4@localhost/JobsScrapingDB?driver=ODBC+Driver+17+for+SQL+Server",
        "echo": True,  # Set to False in production
        "pool_pre_ping": True,
        "pool_recycle": 300
    }
}

# Redis Configuration
REDIS_CONFIG = {
    "url": "redis://localhost:6379/0",
    "host": "localhost",
    "port": 6379,
    "db": 0
}

# Celery Configuration
CELERY_CONFIG = {
    "broker_url": "redis://localhost:6379/0",
    "result_backend": "redis://localhost:6379/0",
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_time_limit": 30 * 60,
    "task_soft_time_limit": 25 * 60,
    "worker_prefetch_multiplier": 1,
    "worker_max_tasks_per_child": 1000
}

# API Configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": True,
    "title": "JobsScraping API",
    "description": "API for scraping and managing job data",
    "version": "1.0.0"
}

# Scraping Configuration
SCRAPING_CONFIG = {
    "max_jobs_per_source": 50,
    "interval_hours": 24,
    "sources": ["topdev", "vietnamwork", "topcv", "linkedin"],
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        },
    }
}