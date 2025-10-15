"""
Data Helper Services

Helper classes for data validation, metadata extraction, and recommendations.

Author: Sparta AI Team
Date: October 14, 2025
"""

import pandas as pd
import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class FileValidator:
    """Validates uploaded files and DataFrames"""
    
    def __init__(self, max_size_mb: int = 500):
        self.max_size_mb = max_size_mb
        self.supported_extensions = ['.csv', '.xlsx', '.xls', '.json', '.parquet', '.tsv', '.txt']
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate a file for processing.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "is_valid": False,
                    "errors": ["File does not exist"],
                    "warnings": []
                }
            
            # Check file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            warnings = []
            if file_size_mb > self.max_size_mb:
                warnings.append(f"File size ({file_size_mb:.2f} MB) exceeds recommended maximum ({self.max_size_mb} MB)")
            
            # Check file extension
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in self.supported_extensions:
                return {
                    "is_valid": False,
                    "errors": [f"Unsupported file extension: {ext}"],
                    "warnings": warnings
                }
            
            return {
                "is_valid": True,
                "errors": [],
                "warnings": warnings,
                "file_size_mb": file_size_mb,
                "extension": ext
            }
            
        except Exception as e:
            logger.error(f"Error validating file: {str(e)}")
            return {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate a DataFrame for processing.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            errors = []
            warnings = []
            
            # Check if DataFrame is empty
            if df.empty:
                errors.append("DataFrame is empty")
            
            # Check for minimum rows
            if len(df) < 2:
                warnings.append("DataFrame has very few rows (< 2)")
            
            # Check for minimum columns
            if len(df.columns) < 1:
                errors.append("DataFrame has no columns")
            
            # Check for duplicate column names
            if len(df.columns) != len(set(df.columns)):
                warnings.append("DataFrame contains duplicate column names")
            
            # Check memory usage
            memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            if memory_mb > 100:
                warnings.append(f"DataFrame uses significant memory: {memory_mb:.2f} MB")
            
            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "rows": len(df),
                "columns": len(df.columns),
                "memory_mb": memory_mb
            }
            
        except Exception as e:
            logger.error(f"Error validating DataFrame: {str(e)}")
            return {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }


class MetadataExtractor:
    """Extracts metadata from files and DataFrames"""
    
    def extract_metadata(self, df: pd.DataFrame, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from a DataFrame.
        
        Args:
            df: DataFrame to extract metadata from
            file_path: Optional path to the source file
            
        Returns:
            Dictionary with metadata information
        """
        try:
            metadata = {
                "shape": {
                    "rows": len(df),
                    "columns": len(df.columns)
                },
                "columns": list(df.columns),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024),
                "missing_values": df.isnull().sum().to_dict(),
                "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
            }
            
            # Add file information if available
            if file_path and os.path.exists(file_path):
                metadata["file"] = {
                    "name": os.path.basename(file_path),
                    "size_mb": os.path.getsize(file_path) / (1024 * 1024),
                    "extension": os.path.splitext(file_path)[1]
                }
            
            # Categorize columns by data type
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            metadata["column_types"] = {
                "numeric": numeric_cols,
                "categorical": categorical_cols,
                "datetime": datetime_cols,
                "count": {
                    "numeric": len(numeric_cols),
                    "categorical": len(categorical_cols),
                    "datetime": len(datetime_cols)
                }
            }
            
            # Add data quality metrics
            metadata["data_quality"] = {
                "completeness": (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                "duplicate_rows": df.duplicated().sum(),
                "duplicate_percentage": (df.duplicated().sum() / len(df) * 100) if len(df) > 0 else 0
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {"error": str(e)}


class RecommendationEngine:
    """Provides intelligent recommendations for data analysis"""
    
    def get_quick_insights(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate quick insights about the dataset.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        try:
            # Dataset size insights
            rows, cols = df.shape
            insights.append({
                "type": "dataset_size",
                "message": f"Dataset contains {rows:,} rows and {cols} columns",
                "severity": "info"
            })
            
            # Missing data insights
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if missing_pct > 20:
                insights.append({
                    "type": "data_quality",
                    "message": f"Dataset has {missing_pct:.1f}% missing values. Consider data cleaning.",
                    "severity": "warning"
                })
            elif missing_pct > 0:
                insights.append({
                    "type": "data_quality",
                    "message": f"Dataset has {missing_pct:.1f}% missing values",
                    "severity": "info"
                })
            
            # Duplicate rows
            dup_count = df.duplicated().sum()
            if dup_count > 0:
                dup_pct = (dup_count / len(df)) * 100
                insights.append({
                    "type": "data_quality",
                    "message": f"Found {dup_count} duplicate rows ({dup_pct:.1f}%)",
                    "severity": "warning" if dup_pct > 5 else "info"
                })
            
            # Column type insights
            numeric_cols = len(df.select_dtypes(include=['number']).columns)
            if numeric_cols > 0:
                insights.append({
                    "type": "column_types",
                    "message": f"Dataset has {numeric_cols} numeric columns suitable for statistical analysis",
                    "severity": "info"
                })
            
            # Memory usage
            memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            if memory_mb > 100:
                insights.append({
                    "type": "performance",
                    "message": f"Dataset uses {memory_mb:.1f} MB of memory. Consider optimization.",
                    "severity": "warning"
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating quick insights: {str(e)}")
            return [{
                "type": "error",
                "message": f"Error generating insights: {str(e)}",
                "severity": "error"
            }]
    
    def get_recommendations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive recommendations for data analysis.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with categorized recommendations
        """
        recommendations = {
            "cleaning": [],
            "analysis": [],
            "visualization": [],
            "modeling": []
        }
        
        try:
            # Cleaning recommendations
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            if missing_pct > 0:
                recommendations["cleaning"].append({
                    "action": "handle_missing_values",
                    "description": f"Handle {missing_pct:.1f}% missing values in dataset",
                    "priority": "high" if missing_pct > 10 else "medium",
                    "methods": ["drop", "fill_mean", "fill_median", "forward_fill"]
                })
            
            dup_count = df.duplicated().sum()
            if dup_count > 0:
                recommendations["cleaning"].append({
                    "action": "remove_duplicates",
                    "description": f"Remove {dup_count} duplicate rows",
                    "priority": "high" if (dup_count / len(df)) > 0.05 else "medium"
                })
            
            # Analysis recommendations
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                recommendations["analysis"].append({
                    "action": "statistical_analysis",
                    "description": f"Perform statistical analysis on {len(numeric_cols)} numeric columns",
                    "priority": "high",
                    "suggested_methods": ["describe", "correlation", "distribution_analysis"]
                })
            
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            if categorical_cols:
                recommendations["analysis"].append({
                    "action": "categorical_analysis",
                    "description": f"Analyze {len(categorical_cols)} categorical columns",
                    "priority": "medium",
                    "suggested_methods": ["value_counts", "unique_values", "frequency_analysis"]
                })
            
            # Visualization recommendations
            if len(numeric_cols) >= 2:
                recommendations["visualization"].append({
                    "action": "correlation_heatmap",
                    "description": "Create correlation heatmap for numeric features",
                    "priority": "high"
                })
                
                recommendations["visualization"].append({
                    "action": "scatter_plots",
                    "description": "Create scatter plots to visualize relationships",
                    "priority": "medium"
                })
            
            if numeric_cols:
                recommendations["visualization"].append({
                    "action": "distribution_plots",
                    "description": "Create histograms and box plots for numeric features",
                    "priority": "medium"
                })
            
            if categorical_cols:
                recommendations["visualization"].append({
                    "action": "bar_charts",
                    "description": "Create bar charts for categorical features",
                    "priority": "medium"
                })
            
            # Modeling recommendations
            if len(df) >= 100 and len(numeric_cols) >= 2:
                recommendations["modeling"].append({
                    "action": "predictive_modeling",
                    "description": "Dataset suitable for predictive modeling",
                    "priority": "medium",
                    "suggested_models": ["linear_regression", "random_forest", "gradient_boosting"]
                })
            
            if len(numeric_cols) >= 3:
                recommendations["modeling"].append({
                    "action": "clustering",
                    "description": "Dataset suitable for clustering analysis",
                    "priority": "low",
                    "suggested_methods": ["kmeans", "hierarchical", "dbscan"]
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {
                "error": str(e),
                "cleaning": [],
                "analysis": [],
                "visualization": [],
                "modeling": []
            }
