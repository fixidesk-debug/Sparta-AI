from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import File
import pandas as pd
import plotly.express as px
import json

async def generate_visualization(
    file_id: int,
    viz_type: str,
    x_column: Optional[str],
    y_column: Optional[str],
    parameters: Dict[str, Any],
    user_id: int,
    db: Session
) -> dict:
    """
    Generate visualization data from uploaded files.
    """
    
    try:
        # Get file from database
        file = db.query(File).filter(
            File.id == file_id,
            File.user_id == user_id
        ).first()
        
        if not file:
            raise ValueError("File not found")
        
        # Load data
        file_path: str = str(file.file_path)  # type: ignore
        df = pd.read_csv(file_path)
        
        # Generate visualization based on type
        if viz_type == "bar":
            fig = px.bar(df, x=x_column, y=y_column, **parameters)
        elif viz_type == "line":
            fig = px.line(df, x=x_column, y=y_column, **parameters)
        elif viz_type == "scatter":
            fig = px.scatter(df, x=x_column, y=y_column, **parameters)
        elif viz_type == "pie":
            fig = px.pie(df, names=x_column, values=y_column, **parameters)
        elif viz_type == "histogram":
            fig = px.histogram(df, x=x_column, **parameters)
        else:
            raise ValueError(f"Unsupported visualization type: {viz_type}")
        
        # Convert to JSON
        fig_json = fig.to_json()
        if fig_json is None:
            raise ValueError("Failed to serialize visualization")
        viz_json = json.loads(fig_json)
        
        return viz_json
        
    except Exception as e:
        raise ValueError(f"Error generating visualization: {str(e)}")
