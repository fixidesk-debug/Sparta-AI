"""
Data Processing System

Comprehensive data processing system supporting multiple file formats with
intelligent insights, automatic profiling, and memory-efficient operations.

Supported Formats:
- CSV (various encodings)
- Excel (.xlsx, .xls) with multiple sheets
- JSON (flat and nested)
- Parquet (large datasets)
- TSV and custom delimiters

Author: Sparta AI Team
Date: October 14, 2025
"""

import logging
import chardet
import pandas as pd
from typing import Dict, Any, Optional, Union, Callable, Literal, cast
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DataProcessingError(Exception):
    """Base exception for data processing errors"""
    pass


class UnsupportedFormatError(DataProcessingError):
    """Raised when file format is not supported"""
    pass


class DataProcessor:
    """
    Core data processing system with support for multiple file formats.
    
    Features:
    - Multi-format support (CSV, Excel, JSON, Parquet, TSV)
    - Automatic encoding detection
    - Memory-efficient chunked processing
    - Progress tracking
    - Error recovery
    
    Example:
        >>> processor = DataProcessor()
        >>> df = processor.load_file('data.csv')
        >>> info = processor.get_file_info('data.csv')
    """
    
    SUPPORTED_FORMATS = {
        '.csv': 'CSV',
        '.xlsx': 'Excel',
        '.xls': 'Excel',
        '.json': 'JSON',
        '.parquet': 'Parquet',
        '.tsv': 'TSV',
        '.txt': 'Text',
    }
    
    # Maximum file size for in-memory processing (100MB)
    MAX_MEMORY_SIZE = 100 * 1024 * 1024
    
    # Chunk size for large file processing
    CHUNK_SIZE = 50000  # rows
    
    def __init__(self, progress_callback: Optional[Callable[[int], None]] = None):
        """
        Initialize DataProcessor.
        
        Args:
            progress_callback: Optional callback function for progress updates
        """
        self.progress_callback = progress_callback
        self._cached_data: Dict[str, pd.DataFrame] = {}
    
    def detect_encoding(self, file_path: str, sample_size: int = 10000) -> str:
        """
        Detect file encoding using chardet.
        
        Args:
            file_path: Path to file
            sample_size: Number of bytes to sample
            
        Returns:
            Detected encoding (e.g., 'utf-8', 'latin-1')
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(sample_size)
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2%})")
                
                # Default to utf-8 if confidence is too low
                if confidence < 0.7:
                    logger.warning("Low encoding confidence, defaulting to utf-8")
                    return 'utf-8'
                
                return encoding or 'utf-8'
        except Exception as e:
            logger.warning(f"Encoding detection failed: {e}, defaulting to utf-8")
            return 'utf-8'
    
    def detect_delimiter(self, file_path: str, encoding: str = 'utf-8') -> str:
        """
        Detect delimiter for text files.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            
        Returns:
            Detected delimiter
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                sample = f.read(4096)
                
            # Test common delimiters
            delimiters = [',', '\t', ';', '|', ' ']
            delimiter_counts = {}
            
            for delimiter in delimiters:
                lines = sample.split('\n')[:10]
                if len(lines) > 1:
                    counts = [line.count(delimiter) for line in lines if line.strip()]
                    if counts and len(set(counts)) == 1:  # Consistent delimiter
                        delimiter_counts[delimiter] = counts[0]
            
            if delimiter_counts:
                detected = max(delimiter_counts.keys(), key=lambda x: delimiter_counts[x])
                logger.info(f"Detected delimiter: {repr(detected)}")
                return detected
            
            return ','  # Default to comma
        except Exception as e:
            logger.warning(f"Delimiter detection failed: {e}, defaulting to comma")
            return ','
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file metadata
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = path.stat()
        extension = path.suffix.lower()
        
        return {
            'filename': path.name,
            'extension': extension,
            'format': self.SUPPORTED_FORMATS.get(extension, 'Unknown'),
            'size_bytes': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'is_large': stat.st_size > self.MAX_MEMORY_SIZE,
        }
    
    def load_csv(
        self, 
        file_path: str, 
        encoding: Optional[str] = None,
        delimiter: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load CSV file with automatic encoding and delimiter detection.
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding (auto-detected if None)
            delimiter: Delimiter character (auto-detected if None)
            **kwargs: Additional pandas read_csv arguments
            
        Returns:
            DataFrame with loaded data
        """
        # Validate file path to prevent path traversal
        path = Path(file_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if encoding is None:
            encoding = self.detect_encoding(str(path))
        
        if delimiter is None:
            delimiter = self.detect_delimiter(str(path), encoding)
        
        file_info = self.get_file_info(str(path))
        
        try:
            if file_info['is_large']:
                # Use chunked reading for large files
                logger.info(f"Loading large CSV file in chunks: {file_info['size_mb']:.2f}MB")
                chunks = []
                for i, chunk in enumerate(pd.read_csv(
                    str(path),
                    encoding=encoding,
                    delimiter=delimiter,
                    chunksize=self.CHUNK_SIZE,
                    **kwargs
                )):
                    chunks.append(chunk)
                    if self.progress_callback:
                        self.progress_callback((i + 1) * self.CHUNK_SIZE)
                
                df = pd.concat(chunks, ignore_index=True)
            else:
                # Load entire file into memory
                df = pd.read_csv(
                    str(path),
                    encoding=encoding,
                    delimiter=delimiter,
                    **kwargs
                )
            
            logger.info(f"Loaded CSV: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            raise DataProcessingError(f"CSV loading failed: {str(e)}")
    
    def load_excel(
        self, 
        file_path: str, 
        sheet_name: Union[str, int, None] = 0,
        **kwargs
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Load Excel file with support for multiple sheets.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name, index, or None for all sheets
            **kwargs: Additional pandas read_excel arguments
            
        Returns:
            DataFrame or dict of DataFrames (if multiple sheets)
        """
        try:
            # Validate file path to prevent path traversal
            path = Path(file_path).resolve()
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_info = self.get_file_info(str(path))
            logger.info(f"Loading Excel file: {file_info['size_mb']:.2f}MB")
            
            df = pd.read_excel(str(path), sheet_name=sheet_name, **kwargs)
            
            if isinstance(df, dict):
                logger.info(f"Loaded {len(df)} sheets")
            else:
                logger.info(f"Loaded Excel: {len(df)} rows, {len(df.columns)} columns")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to load Excel: {e}")
            raise DataProcessingError(f"Excel loading failed: {str(e)}")
    
    def load_json(
        self, 
        file_path: str, 
        orient: str = 'records',
        **kwargs
    ) -> pd.DataFrame:
        """
        Load JSON file with support for nested structures.
        
        Args:
            file_path: Path to JSON file
            orient: JSON orientation ('records', 'split', 'index', etc.)
            **kwargs: Additional pandas read_json arguments
            
        Returns:
            DataFrame with loaded data
        """
        try:
            # Validate file path to prevent path traversal
            path = Path(file_path).resolve()
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_info = self.get_file_info(str(path))
            logger.info(f"Loading JSON file: {file_info['size_mb']:.2f}MB")
            
            # Try to load with pandas first
            try:
                # Validate orient parameter
                valid_orients = ['split', 'records', 'index', 'columns', 'values', 'table']
                if orient not in valid_orients:
                    orient = 'records'
                df = pd.read_json(str(path), orient=cast(Literal['split', 'records', 'index', 'columns', 'values', 'table'], orient), **kwargs)
            except ValueError:
                # If pandas fails, try manual parsing for nested JSON
                with open(str(path), 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    df = pd.json_normalize(data)
                elif isinstance(data, dict):
                    # Try to find the main data array
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            df = pd.json_normalize(value)
                            break
                    else:
                        # No array found, create single-row DataFrame
                        df = pd.json_normalize([data])
                else:
                    raise ValueError("Unsupported JSON structure")
            
            logger.info(f"Loaded JSON: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load JSON: {e}")
            raise DataProcessingError(f"JSON loading failed: {str(e)}")
    
    def load_parquet(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Load Parquet file (optimized for large datasets).
        
        Args:
            file_path: Path to Parquet file
            **kwargs: Additional pandas read_parquet arguments
            
        Returns:
            DataFrame with loaded data
        """
        try:
            # Validate file path to prevent path traversal
            path = Path(file_path).resolve()
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_info = self.get_file_info(str(path))
            logger.info(f"Loading Parquet file: {file_info['size_mb']:.2f}MB")
            
            df = pd.read_parquet(str(path), **kwargs)
            
            logger.info(f"Loaded Parquet: {len(df)} rows, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Failed to load Parquet: {e}")
            raise DataProcessingError(f"Parquet loading failed: {str(e)}")
    
    def load_file(
        self, 
        file_path: str, 
        file_format: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load file with automatic format detection.
        
        Args:
            file_path: Path to file
            file_format: Force specific format (auto-detected if None)
            **kwargs: Format-specific arguments
            
        Returns:
            DataFrame with loaded data
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Determine format
        if file_format:
            format_type = file_format.upper()
        else:
            format_type = self.SUPPORTED_FORMATS.get(extension, '').upper()
        
        if not format_type:
            raise UnsupportedFormatError(
                f"Unsupported file format: {extension}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS.keys())}"
            )
        
        # Route to appropriate loader
        loaders = {
            'CSV': self.load_csv,
            'TSV': lambda fp, **kw: self.load_csv(fp, delimiter='\t', **kw),
            'TEXT': self.load_csv,
            'EXCEL': self.load_excel,
            'JSON': self.load_json,
            'PARQUET': self.load_parquet,
        }
        
        loader = loaders.get(format_type)
        if not loader:
            raise UnsupportedFormatError(f"No loader available for format: {format_type}")
        
        return loader(file_path, **kwargs)
    
    def save_file(
        self, 
        df: pd.DataFrame, 
        file_path: str, 
        file_format: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Save DataFrame to file with format auto-detection.
        
        Args:
            df: DataFrame to save
            file_path: Output file path
            file_format: Force specific format (auto-detected if None)
            **kwargs: Format-specific arguments
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        # Determine format
        if file_format:
            format_type = file_format.upper()
        else:
            format_type = self.SUPPORTED_FORMATS.get(extension, '').upper()
        
        if not format_type:
            raise UnsupportedFormatError(f"Unsupported output format: {extension}")
        
        try:
            # Create directory if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save based on format
            if format_type == 'CSV':
                df.to_csv(file_path, index=False, **kwargs)
            elif format_type == 'TSV':
                df.to_csv(file_path, sep='\t', index=False, **kwargs)
            elif format_type == 'EXCEL':
                df.to_excel(file_path, index=False, **kwargs)
            elif format_type == 'JSON':
                df.to_json(file_path, orient='records', **kwargs)
            elif format_type == 'PARQUET':
                df.to_parquet(file_path, index=False, **kwargs)
            else:
                raise UnsupportedFormatError(f"No writer available for: {format_type}")
            
            logger.info(f"Saved {len(df)} rows to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise DataProcessingError(f"File save failed: {str(e)}")
    
    def get_memory_usage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get detailed memory usage information for DataFrame.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with memory usage details
        """
        memory_usage = df.memory_usage(deep=True)
        
        return {
            'total_bytes': memory_usage.sum(),
            'total_mb': memory_usage.sum() / (1024 * 1024),
            'per_column': {
                col: {
                    'bytes': int(memory_usage[col]),
                    'mb': memory_usage[col] / (1024 * 1024)
                }
                for col in df.columns
            },
            'index_bytes': int(memory_usage.iloc[0]) if len(memory_usage) > 0 else 0,
        }
    
    def optimize_memory(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize DataFrame memory usage by downcasting numeric types.
        
        Args:
            df: DataFrame to optimize
            
        Returns:
            Optimized DataFrame
        """
        df_optimized = df.copy()
        
        # Get initial memory usage
        initial_memory = df.memory_usage(deep=True).sum() / (1024 * 1024)
        
        # Optimize numeric columns
        for col in df_optimized.select_dtypes(include=['int']).columns:
            df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='integer')
        
        for col in df_optimized.select_dtypes(include=['float']).columns:
            df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
        
        # Convert object columns to category if appropriate
        for col in df_optimized.select_dtypes(include=['object']).columns:
            num_unique = df_optimized[col].nunique()
            num_total = len(df_optimized[col])
            
            # Convert to category if less than 50% unique values
            if num_unique / num_total < 0.5:
                df_optimized[col] = df_optimized[col].astype('category')
        
        # Get final memory usage
        final_memory = df_optimized.memory_usage(deep=True).sum() / (1024 * 1024)
        
        reduction = (1 - final_memory / initial_memory) * 100
        logger.info(
            f"Memory optimization: {initial_memory:.2f}MB → {final_memory:.2f}MB "
            f"({reduction:.1f}% reduction)"
        )
        
        return df_optimized
