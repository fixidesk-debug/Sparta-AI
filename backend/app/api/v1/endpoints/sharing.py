"""
Sharing and Collaboration API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import secrets

from app.db.session import get_db
from app.db.models import User, SharedAnalysis, AnalysisComment
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token

router = APIRouter()


class ShareRequest(BaseModel):
    analysis_id: int
    share_type: str  # "public", "private", "team"
    expires_at: Optional[str] = None
    permissions: List[str] = ["view"]  # view, edit, comment


class CommentRequest(BaseModel):
    analysis_id: int
    content: str
    parent_id: Optional[int] = None


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/share")
async def create_share_link(
    request: ShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a shareable link for an analysis"""
    share_token = secrets.token_urlsafe(32)
    
    shared_analysis = SharedAnalysis(
        user_id=current_user.id,
        analysis_id=request.analysis_id,
        share_token=share_token,
        share_type=request.share_type,
        permissions=",".join(request.permissions),
        expires_at=request.expires_at
    )
    
    db.add(shared_analysis)
    db.commit()
    db.refresh(shared_analysis)
    
    return {
        "share_url": f"/shared/{share_token}",
        "share_token": share_token,
        "expires_at": request.expires_at
    }


@router.get("/shared/{share_token}")
async def get_shared_analysis(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Access a shared analysis"""
    shared = db.query(SharedAnalysis).filter(
        SharedAnalysis.share_token == share_token
    ).first()
    
    if not shared:
        raise HTTPException(status_code=404, detail="Shared analysis not found")
    
    if shared.expires_at and datetime.fromisoformat(shared.expires_at) < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Share link has expired")
    
    return {
        "analysis_id": shared.analysis_id,
        "permissions": shared.permissions.split(","),
        "created_at": shared.created_at
    }


@router.post("/comments")
async def add_comment(
    request: CommentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to an analysis"""
    comment = AnalysisComment(
        user_id=current_user.id,
        analysis_id=request.analysis_id,
        content=request.content,
        parent_id=request.parent_id
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment


@router.get("/comments/{analysis_id}")
async def get_comments(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """Get all comments for an analysis"""
    comments = db.query(AnalysisComment).filter(
        AnalysisComment.analysis_id == analysis_id
    ).order_by(AnalysisComment.created_at.asc()).all()
    
    return comments


@router.delete("/share/{share_token}")
async def revoke_share_link(
    share_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a share link"""
    shared = db.query(SharedAnalysis).filter(
        SharedAnalysis.share_token == share_token,
        SharedAnalysis.user_id == current_user.id
    ).first()
    
    if not shared:
        raise HTTPException(status_code=404, detail="Share link not found")
    
    db.delete(shared)
    db.commit()
    
    return {"message": "Share link revoked"}
