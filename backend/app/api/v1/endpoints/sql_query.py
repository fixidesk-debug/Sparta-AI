"""
SQL Query Execution Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.db.models import User, File as FileModel
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token
from app.services.sql_executor import sql_executor

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


class SQLQueryRequest(BaseModel):
    file_id: int
    query: str


class SQLValidateRequest(BaseModel):
    query: str


@router.post("/execute")
async def execute_sql_query(
    request: SQLQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute SQL query on file data"""
    file = db.query(FileModel).filter(
        FileModel.id == request.file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Execute query
    result = sql_executor.execute_query(file.file_path, request.query)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/validate")
async def validate_sql_query(
    request: SQLValidateRequest,
    current_user: User = Depends(get_current_user)
):
    """Validate SQL query syntax"""
    result = sql_executor.validate_query(request.query)
    return result
