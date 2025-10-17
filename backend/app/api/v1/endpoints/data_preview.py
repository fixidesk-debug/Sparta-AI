"""
Data Preview and Loading Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd

from app.db.session import get_db
from app.db.models import User, File as FileModel
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token
from app.services.data_processor import DataProcessor

router = APIRouter()
data_processor = DataProcessor()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.get("/files/{file_id}/data")
async def get_file_data(
    file_id: int,
    limit: Optional[int] = 1000,
    offset: Optional[int] = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get actual data from uploaded file"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load data
        df = data_processor.load_file(file.file_path)
        
        # Get total count
        total_rows = len(df)
        
        # Apply pagination
        df_page = df.iloc[offset:offset + limit]
        
        # Convert to records
        data = df_page.to_dict(orient='records')
        
        # Get column info
        columns = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            columns.append({
                "name": col,
                "type": dtype,
                "nullable": df[col].isnull().any(),
                "unique_count": int(df[col].nunique())
            })
        
        return {
            "data": data,
            "columns": columns,
            "total_rows": total_rows,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total_rows
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data: {str(e)}")


@router.get("/files/{file_id}/columns")
async def get_file_columns(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get column information from file"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        df = data_processor.load_file(file.file_path)
        
        columns = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            sample_values = df[col].dropna().head(5).tolist()
            
            columns.append({
                "name": col,
                "type": dtype,
                "nullable": bool(df[col].isnull().any()),
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique()),
                "sample_values": sample_values
            })
        
        return {
            "columns": columns,
            "total_columns": len(columns),
            "total_rows": len(df)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get columns: {str(e)}")
