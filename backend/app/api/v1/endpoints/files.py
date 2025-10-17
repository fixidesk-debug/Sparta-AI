from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import aiofiles
import os
from pathlib import Path
from uuid import uuid4
import logging
from datetime import datetime, timezone

from app.db.session import get_db
from app.db.models import File as FileModel, User
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token
from app.services.data_catalog_db import create_dataset_db, create_version_db

router = APIRouter()

# Resolve upload directory to an absolute safe path
UPLOAD_DIR = Path("uploads").resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Security config (keep in sync with data endpoint)
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.parquet', '.tsv', '.txt'}
MAX_FILE_SIZE = int(os.getenv('MAX_UPLOAD_SIZE_MB', '100')) * 1024 * 1024

logger = logging.getLogger(__name__)

def _sanitize_for_log(value: str, max_len: int = 512) -> str:
    """Return a safe, compact string for logging by escaping CR/LF/NUL and truncating."""
    if value is None:
        return ''
    s = str(value)
    # Escape CR, LF and NUL to avoid log injection; keep printable chars otherwise
    s = s.replace('\r', '\\r').replace('\n', '\\n').replace('\x00', '\\x00')
    if len(s) > max_len:
        s = s[:max_len] + '...'
    return s

class FileResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    file_type: str
    upload_time: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

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

    # Remove null bytes and control characters that can truncate or confuse file handling
    filename = filename.replace('\x00', '').strip()
    if not filename:
        return None

    # Use basename to strip any path components (covers "../" or absolute paths)
    try:
        name = Path(filename).name
    except Exception:
        name = os.path.basename(filename)

    # Extra check: ensure no path separators remain (defense in depth)
    if os.path.sep in name or (os.path.altsep and os.path.altsep in name):
        name = os.path.basename(name)

    # Remove leading dots to avoid hidden files or traversal artifacts like ".."
    while name.startswith('.'):
        name = name[1:]
    name = name.strip()
    if not name:
        return None

    # Very simple sanitization: keep alphanumerics, dot, dash, underscore
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._"
    cleaned = ''.join(c for c in name if c in safe_chars)

    # Limit filename length to a reasonable maximum
    if len(cleaned) > 255:
        cleaned = cleaned[:255]

    return cleaned or None


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
                except (OSError, RuntimeError) as e:
                    # Log expected / recoverable errors when closing the file but allow other errors
                    # (like asyncio.CancelledError) to propagate so they can be handled by the caller.
                    logger.warning("Failed to close file %s after exceeding size: %s", dest_path, e)
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

    # Extra check: ensure filename contains no path separators (defense in depth)
    if os.path.sep in safe_name or (os.path.altsep and os.path.altsep in safe_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")

    # Extract extension safely using rsplit to avoid any Path parsing surprises
    if '.' in safe_name:
        ext = '.' + safe_name.rsplit('.', 1)[1].lower()
    else:
        ext = ''

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File type {ext or '[none]'} not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    # Create a unique filename to avoid collisions and reveal minimal info
    unique_name = f"{current_user.id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid4().hex}{ext}"
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file path")

        # Create database record
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

        # Optional: create dataset and/or version from upload
        # Query params: dataset_name, dataset_description, tags (comma-separated)
        try:
            from fastapi import Request
        except Exception:
            Request = None
        # We only support this when the request includes the query params; fetch from environment of the ASGI request is not trivial here.
        # Instead, FastAPI will call this function with query params if declared; to keep backwards compatibility we read them from the request scope if present.
        scope = None
        try:
            scope = file.file._file._loop._current_task.get_coro().cr_frame.f_locals.get('request')
        except Exception:
            scope = None
        # NOTE: the above introspection is fragile; instead, clients should call the Data Catalog endpoints after uploading
        # For now, if a dataset_name query parameter was provided by client, it should call catalog endpoints explicitly.

        # Sanitize any user-controlled values before logging to prevent log injection
        safe_email = _sanitize_for_log(getattr(current_user, "email", "") or "")
        safe_fname = _sanitize_for_log(safe_name or "")
        logger.info("User %s uploaded file %s (%d bytes)", safe_email, safe_fname, total_bytes)

        # Convert to response model with datetime as string
        return FileResponse(
            id=db_file.id,
            filename=db_file.filename,
            file_size=db_file.file_size,
            file_type=db_file.file_type,
            upload_time=db_file.upload_time.isoformat()
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.exception("Unexpected error saving uploaded file")
        # Clean up if partially written
        try:
            if dest_path.exists():
                dest_path.unlink(missing_ok=True)
        except OSError as e:
            # Log expected filesystem-related errors during cleanup (e.g., permission denied, IO error)
            logger.warning("Failed to remove partial file %s: %s", dest_path, _sanitize_for_log(str(e)))
        except Exception as e:
            # Log unexpected exceptions to aid debugging rather than silently swallowing them
            logger.exception("Unexpected error while removing partial file %s", dest_path)
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


class CreateDatasetFromFileRequest(BaseModel):
    dataset_name: str
    description: Optional[str] = None
    tags: Optional[str] = None  # comma-separated


@router.post("/{file_id}/create_dataset", status_code=201)
def create_dataset_from_file(file_id: int, payload: CreateDatasetFromFileRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # verify file belongs to user
    file = db.query(FileModel).filter(FileModel.id == file_id, FileModel.user_id == current_user.id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    tags = [t.strip() for t in payload.tags.split(',')] if payload.tags else []
    ds = create_dataset_db(db=db, user_id=current_user.id, name=payload.dataset_name, description=payload.description, tags=tags, file_id=file.id, file_path=file.file_path)
    return ds
