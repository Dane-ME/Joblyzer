from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pdf2image import convert_from_path
from sqlalchemy.orm import Session
from typing import List, Optional
from database.db import get_db
from database.crud import CVCRUD, UserCRUD
from database import models
from ..schemas import CVCreate, CVResponse
import logging
from datetime import datetime
import requests
import json
import os
from pathlib import Path
import tempfile
import shutil

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cvs", tags=["cvs"])

# OCR Configuration
OCR_API_URL = os.getenv("OCR_API_URL", "https://api.ocr.space/Parse/Image")
OCR_API_KEY = os.getenv("OCR_API_KEY", "K86575814788957")

class OCRService:
    """Service để xử lý OCR với Optiic API"""
    
    @staticmethod
    async def process_image_file(image_file: UploadFile) -> str:
        try:
            image_file.file.seek(0)
            content = image_file.file.read()

            headers = {
                'apikey': OCR_API_KEY
            }
            files = {
                'file': (image_file.filename, content, image_file.content_type or 'application/octet-stream')
            }
            data = {
                'language': 'eng',             # đổi 'vie' nếu cần
                'isOverlayRequired': 'true'    # như curl mẫu
            }

            resp = requests.post(OCR_API_URL, headers=headers, files=files, data=data, timeout=60)

            if resp.status_code != 200:
                logger.error(f"OCR API non-200: {resp.status_code}, body[:300]={resp.text[:300]}")
                raise HTTPException(status_code=502, detail="OCR provider error")

            try:
                j = resp.json()
            except Exception:
                logger.error(f"OCR API returned non-JSON: {resp.text[:300]}")
                raise HTTPException(status_code=502, detail="OCR provider returned invalid response")

            if j.get('OCRExitCode') != 1 or not j.get('ParsedResults'):
                logger.error(f"OCR API error payload: {j}")
                raise HTTPException(status_code=502, detail="OCR provider returned error")

            pages = j.get('ParsedResults', []) or []
            texts = []

            for page in pages:
                page_text = page.get('ParsedText', '').strip()
                if page_text:
                    # Loại bỏ dấu cách thừa, xuống dòng liên tiếp
                    cleaned_text = ' '.join(page_text.split())
                    texts.append(cleaned_text)

            # Ghép các trang và loại bỏ dấu cách thừa
            text = ' '.join(texts)
            return text

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing image file: {e}")
            raise HTTPException(status_code=500, detail="Image processing failed")

    @staticmethod
    async def process_image_url(image_url: str) -> str:
        try:
            headers = {
                'apikey': OCR_API_KEY
            }
            data = {
                'url': image_url,
                'language': 'eng',
                'isOverlayRequired': 'true'
            }

            resp = requests.post(OCR_API_URL, headers=headers, data=data, timeout=60)

            if resp.status_code != 200:
                logger.error(f"OCR API non-200: {resp.status_code}, body[:300]={resp.text[:300]}")
                raise HTTPException(status_code=502, detail="OCR provider error")

            try:
                j = resp.json()
            except Exception:
                logger.error(f"OCR API returned non-JSON: {resp.text[:300]}")
                raise HTTPException(status_code=502, detail="OCR provider returned invalid response")

            if j.get('OCRExitCode') != 1 or not j.get('ParsedResults'):
                logger.error(f"OCR API error payload: {j}")
                raise HTTPException(status_code=502, detail="OCR provider returned error")

            pages = j.get('ParsedResults', []) or []
            texts = [ (p.get('ParsedText') or '').strip() for p in pages ]
            text = "\n\n".join([t for t in texts if t])
            return text

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing image URL: {e}")
            raise HTTPException(status_code=500, detail="URL processing failed")

@router.post("/upload-with-ocr", response_model=CVResponse)
async def create_cv_with_ocr(
    user_id: int = Form(...),
    summary: Optional[str] = Form(None),
    cv_file: Optional[UploadFile] = File(None),
    cv_url: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Tạo CV mới với OCR tự động từ file hoặc URL"""
    try:
        # Kiểm tra user tồn tại
        user = UserCRUD.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Xử lý OCR nếu có file hoặc URL
        ocr_text = ""
        if cv_file:
            # Kiểm tra file type
            allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf'}
            file_extension = Path(cv_file.filename).suffix.lower()
            
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail="File type not supported. Only PNG, JPG, JPEG, PDF files are allowed."
                )
            
            # Xử lý OCR với file
            ocr_text = await OCRService.process_image_file(cv_file)
            logger.info(f"OCR processed file {cv_file.filename} for user {user_id}")
            
        elif cv_url:
            # Xử lý OCR với URL
            ocr_text = await OCRService.process_image_url(cv_url)
            logger.info(f"OCR processed URL {cv_url} for user {user_id}")
        
        # Tạo CV data
        cv_data = {
            'UserId': user_id,
            'Summary': summary,
            'CreatedDate': datetime.utcnow(),
            'OCRText': ocr_text,  # Lưu kết quả OCR
            'CVSource': 'file' if cv_file else 'url' if cv_url else 'manual',
            'OriginalFilename': cv_file.filename if cv_file else None,
            'CVUrl': cv_url
        }
        
        # Tạo CV trong database
        db_cv = CVCRUD.create_cv(db, cv_data)
        
        # Trả về response với thông tin OCR
        response_data = {
            'id': db_cv.Id,
            'user_id': db_cv.UserId,
            'summary': db_cv.Summary,
            'ocr_text': ocr_text,
            'cv_source': cv_data['CVSource'],
            'original_filename': cv_data['OriginalFilename'],
            'cv_url': cv_data['CVUrl']
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating CV with OCR: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
        # Map field names to database column names
        cv_data = {
            'UserId': cv_data['user_id'],
            'Name': cv_data['name'],
            'Email': cv_data['email'],
            'PhoneNumber': cv_data['phone_number'],
            'Address': cv_data['address'],
            'Summary': cv_data['summary'],
            'CreatedDate': datetime.utcnow()
        }
        
        db_cv = CVCRUD.create_cv(db, cv_data)
        return db_cv
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating CV: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/ocr-only")
async def process_ocr_only(
    cv_file: Optional[UploadFile] = File(None),
    cv_url: Optional[str] = Form(None)
):
    """Chỉ xử lý OCR mà không lưu CV"""
    try:
        ocr_text = ""
        
        if cv_file:
            # Kiểm tra file type
            allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf'}
            file_extension = Path(cv_file.filename).suffix.lower()
            
            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail="File type not supported. Only PNG, JPG, JPEG, PDF files are allowed."
                )
            
            ocr_text = await OCRService.process_image_file(cv_file)
            
        elif cv_url:
            ocr_text = await OCRService.process_image_url(cv_url)
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either cv_file or cv_url must be provided"
            )
        
        return {
            "ocr_text": ocr_text,
            "processed_at": datetime.utcnow().isoformat(),
            "source": "file" if cv_file else "url"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing OCR only: {e}")
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
            cvs = db.query(models.CV).offset(skip).limit(limit).all()
            return cvs
    except Exception as e:
        logger.error(f"Error getting CVs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{cv_id}", response_model=CVResponse)
async def get_cv(cv_id: int, db: Session = Depends(get_db)):
    """Get CV by ID"""
    try:
        cv = CVCRUD.get_cv_by_id(db, cv_id)
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")
        return cv
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CV {cv_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}", response_model=List[CVResponse])
async def get_cv_by_user_id(user_id: int, db: Session = Depends(get_db)):
    """Get CV by user ID"""
    try:
        cvs = CVCRUD.get_cvs_by_user_id(db, user_id)
        if not cvs:
            raise HTTPException(status_code=404, detail="CV not found for this user")
        return cvs
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
        existing_cv = CVCRUD.get_cv_by_id(db, cv_id)
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
        existing_cv = CVCRUD.get_cv_by_id(db, cv_id)
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
        stats = CVCRUD.get_cv_stats(db)
        
        return {
            "total_cvs": stats["total_cvs"],
            "recent_cvs_30_days": stats["recent_cvs_30_days"],
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting CVs stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")