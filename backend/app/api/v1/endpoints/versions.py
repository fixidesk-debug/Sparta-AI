"""
Data Versioning System
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from pathlib import Path
import shutil

from app.db.session import get_db
from app.db.models import User, File as FileModel
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token
from app.services.version_control import VersionControl

router = APIRouter()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/files/{file_id}/versions/create")
async def create_version(
    file_id: int,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new version of the file"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        metadata = VersionControl.create_file_version(
            file_path=file.file_path,
            file_id=file_id,
            description=description,
            user_id=current_user.id
        )
        
        return {
            "version_created": True,
            "version_name": metadata["version_name"],
            "version_path": metadata["version_path"],
            "file_hash": metadata["file_hash"],
            "file_size": metadata["file_size"],
            "created_at": metadata["created_at"],
            "description": metadata["description"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/{file_id}/versions")
async def list_versions(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all versions of a file"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        versions = VersionControl.list_file_versions(
            file_id=file_id,
            file_path=file.file_path
        )
        
        return {
            "versions": versions,
            "total": len(versions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/{file_id}/versions/restore")
async def restore_version(
    file_id: int,
    version_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restore a previous version"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        result = VersionControl.restore_file_version(
            file_id=file_id,
            file_path=file.file_path,
            version_name=version_name,
            create_backup=True
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/{file_id}/versions/compare")
async def compare_versions(
    file_id: int,
    version1_name: str,
    version2_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Compare two file versions"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        result = VersionControl.compare_file_versions(
            file_id=file_id,
            file_path=file.file_path,
            version1_name=version1_name,
            version2_name=version2_name
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/{file_id}/versions/{version_name}")
async def delete_version(
    file_id: int,
    version_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific version"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        result = VersionControl.delete_file_version(
            file_id=file_id,
            file_path=file.file_path,
            version_name=version_name
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
