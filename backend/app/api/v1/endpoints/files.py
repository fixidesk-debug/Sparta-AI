from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import aiofiles
import os
from pathlib import Path
from uuid import uuid4
import logging
from datetime import datetime

from app.db.session import get_db
from app.db.models import File as FileModel, User
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token

router = APIRouter()

# Resolve upload directory to an absolute safe path
UPLOAD_DIR = Path("uploads").resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Security config (keep in sync with data endpoint)
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.parquet', '.tsv', '.txt'}
MAX_FILE_SIZE = int(os.getenv('MAX_UPLOAD_SIZE_MB', '100')) * 1024 * 1024

logger = logging.getLogger(__name__)

class FileResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    file_type: str
    upload_time: str
    
    class Config:
        from_attributes = True

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


def _secure_filename(filename: str) -> str:
    """Return a secure filename by stripping path components and keeping a safe subset of chars."""
    if not filename:
        return None
    # Strip any path components
    name = Path(filename).name
    # Very simple sanitization: keep alphanumerics, dot, dash, underscore
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._"
    return ''.join(c for c in name if c in safe_chars) or None


async def _stream_save_upload(upload: UploadFile, dest_path: Path, max_size: int) -> int:
    """Stream an UploadFile to disk while enforcing max size. Returns total bytes written."""
    total = 0
    chunk_size = 1024 * 1024
    async with aiofiles.open(dest_path, 'wb') as out_f:
        while True:
            chunk = await upload.read(chunk_size)
            if not chunk:
                break
            total += len(chunk)
            if total > max_size:
                # remove partial file
                try:
                    await out_f.close()
                except Exception:
                    pass
                if dest_path.exists():
                    dest_path.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                    detail=f"File too large. Max size: {max_size // (1024*1024)}MB")
            await out_f.write(chunk)
    return total

@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Basic filename and extension checks
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

    safe_name = _secure_filename(file.filename)
    if not safe_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")

    ext = Path(safe_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File type {ext} not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    # Create a unique filename to avoid collisions and reveal minimal info
    unique_name = f"{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex}{ext}"
    dest_path = UPLOAD_DIR / unique_name

    try:
        # Stream file to disk with size enforcement
        total_bytes = await _stream_save_upload(file, dest_path, MAX_FILE_SIZE)

        # Extra safeguard: ensure file is inside UPLOAD_DIR
        try:
            resolved = dest_path.resolve()
            resolved.relative_to(UPLOAD_DIR)
        except Exception:
            # Path traversal attempt
            if dest_path.exists():
                dest_path.unlink(missing_ok=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid upload path")

        # Save metadata to DB
        db_file = FileModel(
            user_id=current_user.id,
            filename=safe_name,
            file_path=str(dest_path),
            file_size=total_bytes,
            file_type=(file.content_type or '')
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        logger.info(f"User %s uploaded file %s (%d bytes)", current_user.email, safe_name, total_bytes)

        return db_file
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception("Unexpected error saving uploaded file")
        # Clean up if partially written
        try:
            if dest_path.exists():
                dest_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/list", response_model=List[FileResponse])
def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    files = db.query(FileModel).filter(FileModel.user_id == current_user.id).all()
    return files

@router.get("/{file_id}", response_model=FileResponse)
def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file

@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete file from disk - ensure path is within UPLOAD_DIR
    file_path_str = str(file.file_path)
    try:
        resolved = Path(file_path_str).resolve()
        resolved.relative_to(UPLOAD_DIR)
        if resolved.exists():
            resolved.unlink()
    except Exception:
        # If path is invalid or outside upload dir, just log and continue
        logger.warning("Attempted to delete file outside of uploads dir: %s", file_path_str)
    
    # Delete from database
    db.delete(file)
    db.commit()
    
    return {"message": "File deleted successfully"}
