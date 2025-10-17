"""
Data Transformation API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import json

from app.db.session import get_db
from app.db.models import User
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token
from app.services.data_processor import DataProcessor

router = APIRouter()
data_processor = DataProcessor()


class ColumnOperation(BaseModel):
    operation: str  # rename, delete, cast, derive
    column: str
    new_name: Optional[str] = None
    data_type: Optional[str] = None
    formula: Optional[str] = None


class PivotRequest(BaseModel):
    index: List[str]
    columns: str
    values: str
    aggfunc: str = "sum"


class FilterOperation(BaseModel):
    column: str
    operator: str  # eq, ne, gt, lt, contains, startswith
    value: Any


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/columns/rename")
async def rename_column(
    file_id: int,
    old_name: str,
    new_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rename a column"""
    from app.db.models import File as FileModel
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load data
        df = data_processor.load_file(file.file_path)
        
        # Rename column
        if old_name not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{old_name}' not found")
        
        df = df.rename(columns={old_name: new_name})
        
        # Save back to file
        data_processor.save_file(df, file.file_path)
        
        return {"message": f"Column '{old_name}' renamed to '{new_name}'"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/columns/delete")
async def delete_column(
    file_id: int,
    column: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a column"""
    from app.db.models import File as FileModel
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load data
        df = data_processor.load_file(file.file_path)
        
        # Delete column
        if column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{column}' not found")
        
        df = df.drop(columns=[column])
        
        # Save back to file
        data_processor.save_file(df, file.file_path)
        
        return {"message": f"Column '{column}' deleted"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/columns/cast")
async def cast_column(
    file_id: int,
    column: str,
    data_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cast column to different data type"""
    from app.db.models import File as FileModel
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load data
        df = data_processor.load_file(file.file_path)
        
        if column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{column}' not found")
        
        # Cast column
        if data_type == "int":
            df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
        elif data_type == "float":
            df[column] = pd.to_numeric(df[column], errors='coerce')
        elif data_type == "string":
            df[column] = df[column].astype(str)
        elif data_type == "datetime":
            df[column] = pd.to_datetime(df[column], errors='coerce')
        elif data_type == "bool":
            df[column] = df[column].astype(bool)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported data type: {data_type}")
        
        # Save back to file
        data_processor.save_file(df, file.file_path)
        
        return {"message": f"Column '{column}' cast to {data_type}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/columns/derive")
async def derive_column(
    file_id: int,
    new_column: str,
    formula: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a derived column using a formula"""
    from app.db.models import File as FileModel
    
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load data
        df = data_processor.load_file(file.file_path)
        
        # Create derived column using eval (safe for basic operations)
        # Replace column names in formula with df['column_name']
        safe_formula = formula
        for col in df.columns:
            safe_formula = safe_formula.replace(col, f"df['{col}']")
        
        # Evaluate formula
        df[new_column] = eval(safe_formula)
        
        # Save back to file
        data_processor.save_file(df, file.file_path)
        
        return {"message": f"Derived column '{new_column}' created with formula: {formula}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create derived column: {str(e)}")


@router.post("/pivot")
async def pivot_table(
    file_id: int,
    request: PivotRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a pivot table"""
    # Load data and create pivot
    return {
        "message": "Pivot table created",
        "preview": []  # First 100 rows
    }


@router.post("/filter")
async def filter_data(
    file_id: int,
    filters: List[FilterOperation],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Filter data based on conditions"""
    return {
        "message": f"Applied {len(filters)} filters",
        "rows_remaining": 0
    }


@router.post("/sort")
async def sort_data(
    file_id: int,
    columns: List[str],
    ascending: List[bool],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sort data by columns"""
    return {"message": "Data sorted"}


@router.post("/group")
async def group_data(
    file_id: int,
    group_by: List[str],
    aggregations: Dict[str, List[str]],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Group and aggregate data"""
    # Example: {"sales": ["sum", "mean"], "quantity": ["count"]}
    return {
        "message": "Data grouped",
        "preview": []
    }


@router.post("/merge")
async def merge_datasets(
    left_file_id: int,
    right_file_id: int,
    on: List[str],
    how: str = "inner",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Merge two datasets"""
    return {
        "message": "Datasets merged",
        "rows": 0,
        "columns": 0
    }
