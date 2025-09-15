from fastapi import APIRouter
from .jobs import router as jobs_router
from .scraping import router as scraping_router
from .users import router as users_router
from .cvs import router as cvs_router
from .matching import router as matching_router

# Create main router
main_router = APIRouter()

# Include all route modules
main_router.include_router(jobs_router)
main_router.include_router(scraping_router)
main_router.include_router(users_router)
main_router.include_router(cvs_router)
main_router.include_router(matching_router)