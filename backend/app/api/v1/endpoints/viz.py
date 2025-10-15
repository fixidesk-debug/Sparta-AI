from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.db.session import get_db
from app.db.models import User
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token
from app.services.viz import generate_visualization

router = APIRouter()

class VizRequest(BaseModel):
    file_id: int
    viz_type: str  # bar, line, scatter, pie, etc.
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class VizResponse(BaseModel):
    visualization_data: dict
    chart_type: str

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email: Optional[str] = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.post("/generate", response_model=VizResponse)
async def create_visualization(
    viz_request: VizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Generate visualization
    # At runtime, current_user.id is an int, but type stubs show Column[int]
    user_id: int = current_user.id  # type: ignore
    viz_data = await generate_visualization(
        file_id=viz_request.file_id,
        viz_type=viz_request.viz_type,
        x_column=viz_request.x_column,
        y_column=viz_request.y_column,
        parameters=viz_request.parameters or {},
        user_id=user_id,
        db=db
    )
    
    return {
        "visualization_data": viz_data,
        "chart_type": viz_request.viz_type
    }
