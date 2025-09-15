from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from database.crud import UserCRUD
from ..schemas import UserCreate, UserResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create new user"""
    try:
        # Check if user already exists
        existing_user = UserCRUD.get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="User with this email already exists"
            )
        
        # Hash password (you should implement proper password hashing)
        user_data = user.dict()
        # user_data['password'] = hash_password(user_data['password'])
        
        # Create user
        db_user = UserCRUD.create_user(db, user_data)
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None, description="Filter by user role"),
    db: Session = Depends(get_db)
):
    """Get all users with optional filtering"""
    try:
        users = db.query(UserCRUD).offset(skip).limit(limit).all()
        
        # Apply role filter if provided
        if role:
            users = [user for user in users if user.role == role]
        
        return users
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    try:
        user = UserCRUD.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """Get user by email"""
    try:
        user = UserCRUD.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by email {email}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    user_update: dict, 
    db: Session = Depends(get_db)
):
    """Update user information"""
    try:
        # Check if user exists
        existing_user = UserCRUD.get_user_by_id(db, user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user
        user_data = user_update.copy()
        user_data['updated_at'] = datetime.utcnow()
        
        updated_user = UserCRUD.update_user(db, user_id, user_data)
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user (soft delete)"""
    try:
        # Check if user exists
        existing_user = UserCRUD.get_user_by_id(db, user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Soft delete - update status instead of actually deleting
        user_data = {'is_active': False, 'updated_at': datetime.utcnow()}
        UserCRUD.update_user(db, user_id, user_data)
        
        return {
            "status": "success",
            "message": f"User {user_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats/summary")
async def get_users_stats(db: Session = Depends(get_db)):
    """Get users statistics summary"""
    try:
        total_users = db.query(UserCRUD).count()
        active_users = db.query(UserCRUD).filter(UserCRUD.is_active == True).count()
        
        # Get users by role
        roles = db.query(UserCRUD.role).distinct().all()
        role_stats = {}
        for role in roles:
            if role[0]:  # Check if role is not None
                count = db.query(UserCRUD).filter(UserCRUD.role == role[0]).count()
                role_stats[role[0]] = count
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "roles": role_stats,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting users stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")