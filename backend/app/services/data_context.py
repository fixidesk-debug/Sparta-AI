"""
Data Context Management
Manages data information and context for code generation
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Any
from pathlib import Path
import logging
import json
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DataContext:
    """Manages context information about uploaded data"""
    
    def __init__(self, file_path: str, filename: str):
        """
        Initialize data context
        
        Args:
            file_path: Path to the data file
            filename: Original filename
        """
        # Validate file path to prevent path traversal
        base_dir = Path("uploads").resolve()
        p = Path(file_path)
        try:
            if p.is_absolute():
                # Resolve an absolute path and ensure it is inside uploads
                file_path_obj = p.resolve()
            else:
                # Treat relative paths as relative to the uploads directory
                file_path_obj = (base_dir / p).resolve()
            # Ensure the resolved path is inside the uploads directory
            file_path_obj.relative_to(base_dir)
        except Exception:
            raise ValueError("Access denied: Path outside allowed directory")
        
        self.file_path = file_path_obj
        self.filename = filename
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def load_data(self) -> bool:
        """
        Load data from file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine file type from extension
            ext = self.file_path.suffix.lower()
            
            if ext == '.csv':
                self.df = pd.read_csv(self.file_path)
            elif ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.file_path)
            elif ext == '.json':
                self.df = pd.read_json(self.file_path)
            elif ext == '.parquet':
                self.df = pd.read_parquet(self.file_path)
            else:
                self.logger.error(f"Unsupported file type: {ext}")
                return False
            
            self.logger.info(f"Loaded data: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            self._extract_metadata()
            return True
            
        except Exception as e:
            self.logger.exception(f"Error loading data: {e}")
            return False
    
    def _extract_metadata(self):
        """Extract metadata from dataframe"""
        if self.df is None:
            return
        
        try:
            # Basic information
            self.metadata = {
                'filename': self.filename,
                'rows': len(self.df),
                'columns': len(self.df.columns),
                'column_names': self.df.columns.tolist(),
                'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()},
                'memory_usage_mb': self.df.memory_usage(deep=True).sum() / 1024 / 1024,
                'loaded_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Missing values
            missing = self.df.isnull().sum()
            self.metadata['missing_values'] = {
                col: int(count) for col, count in missing.items() if count > 0
            }
            
            # Numerical columns statistics
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            self.metadata['numeric_columns'] = numeric_cols
            
            # Categorical columns
            categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
            self.metadata['categorical_columns'] = categorical_cols
            
            # Datetime columns
            datetime_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
            self.metadata['datetime_columns'] = datetime_cols
            
            # Unique value counts for categorical columns (limited)
            unique_counts = {}
            for col in categorical_cols[:10]:  # Limit to first 10 categorical columns
                unique_counts[col] = int(self.df[col].nunique())
            self.metadata['unique_value_counts'] = unique_counts
            
        except Exception as e:
            self.logger.exception(f"Error extracting metadata: {e}")
    
    def get_summary(self) -> str:
        """
        Get text summary of data
        
        Returns:
            Formatted summary string
        """
        if self.df is None:
            return "No data loaded"
        
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"Dataset: {self.metadata['filename']}")
        summary_parts.append(f"Shape: {self.metadata['rows']} rows × {self.metadata['columns']} columns")
        summary_parts.append(f"Memory: {self.metadata['memory_usage_mb']:.2f} MB")
        
        # Columns
        summary_parts.append(f"\nColumns ({len(self.metadata['column_names'])}):")
        for col in self.metadata['column_names'][:20]:  # Show first 20
            dtype = self.metadata['dtypes'][col]
            summary_parts.append(f"  - {col} ({dtype})")
        if len(self.metadata['column_names']) > 20:
            summary_parts.append(f"  ... and {len(self.metadata['column_names']) - 20} more")
        
        # Missing values
        if self.metadata['missing_values']:
            summary_parts.append("\nMissing Values:")
            for col, count in list(self.metadata['missing_values'].items())[:10]:
                pct = (count / self.metadata['rows']) * 100
                summary_parts.append(f"  - {col}: {count} ({pct:.1f}%)")
        
        return "\n".join(summary_parts)
    
    def get_sample_data(self, n: int = 5) -> str:
        """
        Get sample data as string
        
        Args:
            n: Number of rows to include
            
        Returns:
            Sample data string
        """
        if self.df is None:
            return "No data available"
        
        return self.df.head(n).to_string()
    
    def get_statistical_summary(self) -> str:
        """
        Get statistical summary of numerical columns
        
        Returns:
            Statistical summary string
        """
        if self.df is None:
            return "No data available"
        
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return "No numerical columns in dataset"
        
        return numeric_df.describe().to_string()
    
    def get_column_info(self, column: str) -> Dict[str, Any]:
        """
        Get detailed information about a column
        
        Args:
            column: Column name
            
        Returns:
            Dictionary with column information
        """
        if self.df is None or column not in self.df.columns:
            return {}
        
        col_data = self.df[column]
        info = {
            'name': column,
            'dtype': str(col_data.dtype),
            'count': int(col_data.count()),
            'missing': int(col_data.isnull().sum()),
            'unique': int(col_data.nunique())
        }
        
        # Numerical column stats
        if pd.api.types.is_numeric_dtype(col_data):
            info['mean'] = float(col_data.mean()) if not col_data.empty else None
            info['std'] = float(col_data.std()) if not col_data.empty else None
            info['min'] = float(col_data.min()) if not col_data.empty else None
            info['max'] = float(col_data.max()) if not col_data.empty else None
            info['median'] = float(col_data.median()) if not col_data.empty else None
        
        # Categorical column stats
        elif pd.api.types.is_object_dtype(col_data) or hasattr(col_data.dtype, 'categories'):
            value_counts = col_data.value_counts().head(10)
            info['top_values'] = {str(k): int(v) for k, v in value_counts.items()}
        
        return info
    
    def get_correlation_matrix(self) -> Optional[pd.DataFrame]:
        """
        Get correlation matrix for numerical columns
        
        Returns:
            Correlation matrix DataFrame or None
        """
        if self.df is None:
            return None
        
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty or len(numeric_df.columns) < 2:
            return None
        
        return numeric_df.corr()
    
    def detect_column_types(self) -> Dict[str, str]:
        """
        Detect semantic types of columns
        
        Returns:
            Dictionary mapping column names to semantic types
        """
        if self.df is None:
            return {}
        
        column_types = {}
        
        for col in self.df.columns:
            col_data = self.df[col]
            
            # Check for datetime
            if pd.api.types.is_datetime64_any_dtype(col_data):
                column_types[col] = 'datetime'
            
            # Check for numerical
            elif pd.api.types.is_numeric_dtype(col_data):
                # Check if it's an ID column
                if col.lower() in ['id', 'index', 'key'] or col.lower().endswith('_id'):
                    column_types[col] = 'identifier'
                # Check if it's a boolean
                elif col_data.nunique() == 2:
                    column_types[col] = 'boolean_numeric'
                else:
                    column_types[col] = 'numeric'
            
            # Check for categorical
            elif pd.api.types.is_object_dtype(col_data):
                unique_ratio = col_data.nunique() / len(col_data)
                if unique_ratio < 0.05:  # Less than 5% unique values
                    column_types[col] = 'categorical'
                elif unique_ratio > 0.95:  # More than 95% unique values
                    column_types[col] = 'identifier'
                else:
                    column_types[col] = 'text'
            
            else:
                column_types[col] = 'unknown'
        
        return column_types
    
    def get_data_quality_report(self) -> Dict[str, Any]:
        """
        Generate data quality report
        
        Returns:
            Dictionary with data quality metrics
        """
        if self.df is None:
            return {}
        
        report = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'duplicate_rows': int(self.df.duplicated().sum()),
            'total_missing_values': int(self.df.isnull().sum().sum()),
            'columns_with_missing': len([col for col in self.df.columns if self.df[col].isnull().any()]),
            'memory_usage_mb': float(self.df.memory_usage(deep=True).sum() / 1024 / 1024)
        }
        
        # Missing value percentage
        missing_pct = (report['total_missing_values'] / (report['total_rows'] * report['total_columns'])) * 100
        report['missing_percentage'] = round(missing_pct, 2)
        
        # Completeness score (0-100)
        report['completeness_score'] = round(100 - missing_pct, 2)
        
        return report
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary
        
        Returns:
            Dictionary representation
        """
        return {
            'file_path': str(self.file_path),
            'filename': self.filename,
            'metadata': self.metadata,
            'summary': self.get_summary(),
            'data_quality': self.get_data_quality_report()
        }
    
    def to_json(self) -> str:
        """
        Convert context to JSON string
        
        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=2, default=str)


class DataContextManager:
    """Manages multiple data contexts"""
    
    def __init__(self):
        """Initialize data context manager"""
        self.contexts: Dict[int, DataContext] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_context(self, file_id: int, file_path: str, filename: str) -> Optional[DataContext]:
        """
        Create new data context
        
        Args:
            file_id: File ID
            file_path: Path to file
            filename: Original filename
            
        Returns:
            DataContext instance or None if failed
        """
        try:
            context = DataContext(file_path, filename)
            if context.load_data():
                self.contexts[file_id] = context
                self.logger.info(f"Created context for file {file_id}: {filename}")
                return context
            return None
        except Exception as e:
            self.logger.exception(f"Error creating context: {e}")
            return None
    
    def get_context(self, file_id: int) -> Optional[DataContext]:
        """
        Get existing data context
        
        Args:
            file_id: File ID
            
        Returns:
            DataContext instance or None
        """
        return self.contexts.get(file_id)
    
    def remove_context(self, file_id: int):
        """
        Remove data context
        
        Args:
            file_id: File ID
        """
        if file_id in self.contexts:
            del self.contexts[file_id]
            self.logger.info(f"Removed context for file {file_id}")
    
    def clear_all(self):
        """Clear all contexts"""
        self.contexts.clear()
        self.logger.info("Cleared all data contexts")


# Global context manager instance
data_context_manager = DataContextManager()
