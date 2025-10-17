"""
AI-Powered Insights and Suggestions
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from pathlib import Path

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


@router.post("/chart-suggestions/{file_id}")
async def suggest_charts(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI-powered chart suggestions based on data characteristics"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Load data
    df = data_processor.load_file(file.file_path)
    
    suggestions = []
    
    # Analyze columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    # Suggest time series if datetime column exists
    if datetime_cols and numeric_cols:
        suggestions.append({
            "chart_type": "line",
            "title": "Time Series Analysis",
            "x_column": datetime_cols[0],
            "y_column": numeric_cols[0],
            "reason": "Detected time-based data - perfect for trend analysis",
            "confidence": 0.95
        })
    
    # Suggest bar chart for categorical + numeric
    if categorical_cols and numeric_cols:
        cat_col = categorical_cols[0]
        unique_count = df[cat_col].nunique()
        
        if unique_count <= 20:
            suggestions.append({
                "chart_type": "bar",
                "title": f"{numeric_cols[0]} by {cat_col}",
                "x_column": cat_col,
                "y_column": numeric_cols[0],
                "reason": f"Compare {numeric_cols[0]} across {unique_count} categories",
                "confidence": 0.9
            })
    
    # Suggest scatter for two numeric columns (correlation)
    if len(numeric_cols) >= 2:
        # Calculate correlation
        corr = df[numeric_cols[:2]].corr().iloc[0, 1]
        if abs(corr) > 0.3:
            suggestions.append({
                "chart_type": "scatter",
                "title": f"Relationship: {numeric_cols[0]} vs {numeric_cols[1]}",
                "x_column": numeric_cols[0],
                "y_column": numeric_cols[1],
                "reason": f"Strong correlation detected ({corr:.2f})",
                "confidence": 0.85
            })
    
    # Suggest pie chart for categorical with few categories
    if categorical_cols:
        cat_col = categorical_cols[0]
        unique_count = df[cat_col].nunique()
        
        if 2 <= unique_count <= 8:
            suggestions.append({
                "chart_type": "pie",
                "title": f"Distribution of {cat_col}",
                "x_column": cat_col,
                "y_column": None,
                "reason": f"Show proportion across {unique_count} categories",
                "confidence": 0.8
            })
    
    # Suggest histogram for numeric distribution
    if numeric_cols:
        suggestions.append({
            "chart_type": "histogram",
            "title": f"Distribution of {numeric_cols[0]}",
            "x_column": numeric_cols[0],
            "y_column": None,
            "reason": "Understand data distribution and identify patterns",
            "confidence": 0.75
        })
    
    return {
        "suggestions": sorted(suggestions, key=lambda x: x["confidence"], reverse=True)[:5],
        "data_summary": {
            "rows": len(df),
            "numeric_columns": len(numeric_cols),
            "categorical_columns": len(categorical_cols),
            "datetime_columns": len(datetime_cols)
        }
    }


@router.post("/auto-insights/{file_id}")
async def generate_insights(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate automatic insights from data"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    df = data_processor.load_file(file.file_path)
    insights = []
    
    # Missing data insights
    missing_pct = (df.isnull().sum() / len(df) * 100)
    for col in missing_pct[missing_pct > 10].index:
        insights.append({
            "type": "warning",
            "title": f"High Missing Data in {col}",
            "description": f"{missing_pct[col]:.1f}% of values are missing",
            "action": "Consider imputation or removal"
        })
    
    # Duplicate rows
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        insights.append({
            "type": "warning",
            "title": "Duplicate Rows Detected",
            "description": f"Found {duplicates} duplicate rows ({duplicates/len(df)*100:.1f}%)",
            "action": "Review and remove duplicates if needed"
        })
    
    # Numeric insights
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        # Outliers
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
        
        if outliers > len(df) * 0.05:
            insights.append({
                "type": "info",
                "title": f"Outliers in {col}",
                "description": f"{outliers} outliers detected ({outliers/len(df)*100:.1f}%)",
                "action": "Investigate unusual values"
            })
        
        # Skewness
        skew = df[col].skew()
        if abs(skew) > 1:
            direction = "right" if skew > 0 else "left"
            insights.append({
                "type": "info",
                "title": f"{col} is Skewed",
                "description": f"Distribution is {direction}-skewed (skewness: {skew:.2f})",
                "action": "Consider log transformation"
            })
    
    # Correlation insights
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        high_corr = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    high_corr.append({
                        "col1": corr_matrix.columns[i],
                        "col2": corr_matrix.columns[j],
                        "correlation": corr_val
                    })
        
        if high_corr:
            for item in high_corr[:3]:
                insights.append({
                    "type": "success",
                    "title": f"Strong Correlation Found",
                    "description": f"{item['col1']} and {item['col2']} are highly correlated ({item['correlation']:.2f})",
                    "action": "Explore relationship with scatter plot"
                })
    
    # Categorical insights
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        unique_count = df[col].nunique()
        
        if unique_count == len(df):
            insights.append({
                "type": "info",
                "title": f"{col} is Unique Identifier",
                "description": "Every value is unique - likely an ID column",
                "action": "Consider removing from analysis"
            })
        elif unique_count <= 10:
            top_value = df[col].value_counts().iloc[0]
            top_pct = top_value / len(df) * 100
            
            if top_pct > 50:
                insights.append({
                    "type": "info",
                    "title": f"{col} is Imbalanced",
                    "description": f"Top category represents {top_pct:.1f}% of data",
                    "action": "Consider stratified sampling"
                })
    
    return {
        "insights": insights[:10],
        "total_insights": len(insights)
    }


@router.post("/detect-types/{file_id}")
async def detect_column_types(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Smart detection of column data types"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    df = data_processor.load_file(file.file_path)
    
    type_suggestions = {}
    
    for col in df.columns:
        current_type = str(df[col].dtype)
        suggested_type = current_type
        confidence = 1.0
        
        # Try to detect better types
        sample = df[col].dropna().head(100)
        
        if current_type == 'object':
            # Try datetime
            try:
                pd.to_datetime(sample)
                suggested_type = 'datetime'
                confidence = 0.9
            except:
                # Try numeric
                try:
                    pd.to_numeric(sample)
                    suggested_type = 'numeric'
                    confidence = 0.85
                except:
                    # Try boolean
                    unique_vals = set(sample.str.lower())
                    if unique_vals.issubset({'true', 'false', 'yes', 'no', '1', '0', 't', 'f'}):
                        suggested_type = 'boolean'
                        confidence = 0.95
        
        type_suggestions[col] = {
            "current_type": current_type,
            "suggested_type": suggested_type,
            "confidence": confidence,
            "should_convert": suggested_type != current_type
        }
    
    return {"type_suggestions": type_suggestions}


@router.post("/sample-data/{file_id}")
async def sample_large_dataset(
    file_id: int,
    sample_size: int = 10000,
    method: str = "random",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sample large datasets for faster analysis"""
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    df = data_processor.load_file(file.file_path)
    
    original_size = len(df)
    
    if original_size <= sample_size:
        return {
            "sampled": False,
            "original_size": original_size,
            "sample_size": original_size,
            "message": "Dataset is small enough, no sampling needed"
        }
    
    if method == "random":
        sampled_df = df.sample(n=sample_size, random_state=42)
    elif method == "stratified":
        # Stratified sampling on first categorical column
        cat_cols = df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            sampled_df = df.groupby(cat_cols[0], group_keys=False).apply(
                lambda x: x.sample(min(len(x), sample_size // df[cat_cols[0]].nunique()))
            )
        else:
            sampled_df = df.sample(n=sample_size, random_state=42)
    else:
        sampled_df = df.head(sample_size)
    
    # Save sampled data
    sample_path = Path(file.file_path).parent / f"sample_{Path(file.file_path).name}"
    sampled_df.to_csv(sample_path, index=False)
    
    return {
        "sampled": True,
        "original_size": original_size,
        "sample_size": len(sampled_df),
        "sample_path": str(sample_path),
        "reduction_pct": (1 - len(sampled_df) / original_size) * 100
    }
