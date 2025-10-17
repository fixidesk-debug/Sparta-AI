"""
Natural Language to Chart Generation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import re

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


class NLChartRequest(BaseModel):
    file_id: int
    query: str


@router.post("/nl-to-chart")
async def natural_language_to_chart(
    request: NLChartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convert natural language to chart configuration"""
    file = db.query(FileModel).filter(
        FileModel.id == request.file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    df = data_processor.load_file(file.file_path)
    columns = df.columns.tolist()
    
    query = request.query.lower()
    
    # Detect chart type
    chart_type = "bar"
    if any(word in query for word in ["line", "trend", "over time", "timeline"]):
        chart_type = "line"
    elif any(word in query for word in ["scatter", "relationship", "correlation", "vs"]):
        chart_type = "scatter"
    elif any(word in query for word in ["pie", "proportion", "percentage", "distribution of"]):
        chart_type = "pie"
    elif any(word in query for word in ["histogram", "frequency"]):
        chart_type = "histogram"
    elif any(word in query for word in ["area", "cumulative"]):
        chart_type = "area"
    
    # Extract columns from query
    x_column = None
    y_column = None
    
    # Try to match column names in query
    for col in columns:
        col_lower = col.lower()
        if col_lower in query:
            if not x_column:
                x_column = col
            elif not y_column:
                y_column = col
    
    # If no columns found, use smart defaults
    if not x_column:
        # Use first categorical or datetime column for x
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        if datetime_cols:
            x_column = datetime_cols[0]
            chart_type = "line"
        elif cat_cols:
            x_column = cat_cols[0]
    
    if not y_column:
        # Use first numeric column for y
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        if num_cols:
            y_column = num_cols[0]
    
    # Generate title from query
    title = request.query.capitalize()
    if len(title) > 50:
        title = title[:50] + "..."
    
    return {
        "chart_type": chart_type,
        "x_column": x_column,
        "y_column": y_column,
        "title": title,
        "query": request.query,
        "confidence": 0.85,
        "explanation": f"Detected {chart_type} chart with {x_column} on x-axis and {y_column} on y-axis"
    }
