"""
Data Operation History and Undo/Redo
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json

from app.db.session import get_db
from app.db.models import User, File as FileModel
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token
from app.services.undo_redo_service import UndoRedoService

router = APIRouter()

# Using UndoRedoService for operation tracking


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


class Operation(BaseModel):
    operation_type: str
    file_id: int
    parameters: Dict[str, Any]
    timestamp: Optional[str] = None


@router.post("/operations/record")
async def record_operation(
    operation: Operation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a data operation for undo/redo"""
    file = db.query(FileModel).filter(
        FileModel.id == operation.file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        result = UndoRedoService.record_operation(
            user_id=current_user.id,
            file_id=operation.file_id,
            file_path=file.file_path,
            operation_type=operation.operation_type,
            parameters=operation.parameters
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operations/history/{file_id}")
async def get_operation_history(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get operation history for a file"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        history = UndoRedoService.get_history(
            user_id=current_user.id,
            file_id=file_id
        )
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/operations/undo/{file_id}")
async def undo_operation(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Undo the last operation"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        result = UndoRedoService.undo(
            user_id=current_user.id,
            file_id=file_id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/operations/redo/{file_id}")
async def redo_operation(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Redo the last undone operation"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        result = UndoRedoService.redo(
            user_id=current_user.id,
            file_id=file_id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/operations/clear/{file_id}")
async def clear_history(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear operation history"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        result = UndoRedoService.clear_history(
            user_id=current_user.id,
            file_id=file_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
