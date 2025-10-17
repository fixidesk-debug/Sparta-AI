"""
Data Processing API Endpoints

REST API endpoints for data processing operations.

Author: Sparta AI Team
Date: October 14, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import json
import logging
import os

from app.db.session import get_db
from app.db.models import User
from app.core.security import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from app.services.data_processor import DataProcessor, DataProcessingError
from app.services.data_profiler import DataProfiler
from app.services.data_cleaner import DataCleaner
from app.services.data_helpers import FileValidator, MetadataExtractor, RecommendationEngine

router = APIRouter()
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# Initialize services
data_processor = DataProcessor()
data_profiler = DataProfiler()
data_cleaner = DataCleaner()
file_validator = FileValidator()
metadata_extractor = MetadataExtractor()
recommendation_engine = RecommendationEngine()

def process_uploaded_file(tmp_path):
    """
    Process an uploaded temporary file and return a tuple:
    (validation, metadata, insights, dataframe)
    This helper groups the related service calls to reduce coupling in endpoint handlers.
    """
    try:
        # Validate file (path-based validation)
        validation = file_validator.validate_file(tmp_path)
        # Load file (service is expected to handle streaming/efficient reads)
        df = data_processor.load_file(tmp_path)
        # Validate DataFrame
        df_validation = file_validator.validate_dataframe(df)
        validation['dataframe'] = df_validation
        # Extract metadata
        metadata = metadata_extractor.extract_metadata(df, tmp_path)
        # Get quick insights
        insights = recommendation_engine.get_quick_insights(df)
        return validation, metadata, insights, df
    except DataProcessingError:
        # propagate domain-specific errors
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}")
        # wrap unexpected errors in a domain error for consistent handling
        raise DataProcessingError(str(e))

# File upload security configuration
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.parquet', '.tsv', '.txt'}
MAX_FILE_SIZE = int(os.getenv('MAX_UPLOAD_SIZE_MB', '100')) * 1024 * 1024

def validate_upload(file: UploadFile) -> None:
    """Validate file upload for security"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate content type
    allowed_content_types = {
        'text/csv', 'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/json', 'application/octet-stream', 'text/plain'
    }
    if file.content_type and file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail=f"Content type {file.content_type} not allowed"
        )
    
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

async def safe_save_upload(file: UploadFile) -> str:
    """
    Save an UploadFile to a temporary file safely:
    - stream the file in chunks to avoid memory spikes
    - enforce MAX_FILE_SIZE
    - sanitize suffix (use allowed extensions only)
    - perform basic magic-byte checks for binary formats
    Returns the path to the temporary file (caller is responsible for cleanup).
    """
    import tempfile

    # Sanitize and choose suffix
    basename = os.path.basename(file.filename or "")
    suffix = os.path.splitext(basename)[1].lower()

    # Re-validate extension and content type defensively
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {suffix} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    allowed_content_types = {
        'text/csv', 'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/json', 'application/octet-stream', 'text/plain'
    }
    if file.content_type and file.content_type not in allowed_content_types:
        raise HTTPException(status_code=400, detail=f"Content type {file.content_type} not allowed")

    size = 0
    tmp_path = None
    try:
        # Stream write to temp file to avoid loading entire file into memory
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            while True:
                chunk = await file.read(8192)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    try:
                        tmp_file.close()
                    except Exception:
                        pass
                    try:
                        os.unlink(tmp_file.name)
                    except Exception:
                        pass
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB"
                    )
                tmp_file.write(chunk)
            tmp_path = tmp_file.name

        # Perform lightweight content verification based on magic bytes for known binary formats
        try:
            with open(tmp_path, 'rb') as fh:
                header = fh.read(8)
            # Parquet files start with b'PAR1'
            if header.startswith(b'PAR1') and suffix != '.parquet':
                logger.warning("Uploaded file magic indicates Parquet but extension differs.")
            # ZIP-based formats (xlsx) start with PK
            if header.startswith(b'PK') and suffix not in ('.xlsx',):
                logger.warning("Uploaded file magic indicates ZIP (possibly xlsx) but extension differs.")
            # Old XLS compound file signature
            if header.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1') and suffix not in ('.xls',):
                logger.warning("Uploaded file magic indicates old XLS but extension differs.")
            # For text-like types, ensure initial bytes are decodable as UTF-8
            if suffix in ('.json', '.csv', '.tsv', '.txt'):
                try:
                    with open(tmp_path, 'rb') as fh:
                        sample = fh.read(2048)
                    sample.decode('utf-8')
                except Exception:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass
                    raise HTTPException(status_code=400, detail="Uploaded text file is not valid UTF-8")
        except HTTPException:
            raise
        except Exception:
            logger.warning("Failed to perform detailed file magic checks; proceeding with caution.")
        return tmp_path
    except HTTPException:
        raise
    except Exception as e:
        # Attempt cleanup on error and return a consistent HTTP error;
        # safe_save_upload must only return a file path (str) or raise.
        logger.error(f"Error saving uploaded file: {e}")
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving uploaded file: {str(e)}"
        )


@router.post("/profile")
async def profile_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Profile a dataset and return comprehensive analysis.
    
    Returns detailed profiling information.
    """
    validate_upload(file)
    
    try:
        # Save uploaded file temporarily using the safe streamer (enforces size/type/magic-byte checks)
        tmp_path = await safe_save_upload(file)
        
        try:
            # Load file
            df = data_processor.load_file(tmp_path)
            
            # Profile dataset
            profile = data_profiler.profile_dataset(df)
            
            # Get insights
            insights = data_profiler.get_insights(df)
            
            # Extract metadata
            metadata = metadata_extractor.extract_metadata(df, tmp_path)
            
            return {
                "success": True,
                "profile": profile,
                "insights": insights,
                "metadata": metadata
            }
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"Error profiling data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error profiling data: {str(e)}"
        )


@router.post("/clean")
async def clean_data(
    file: UploadFile = File(...),
    operations: str = Form(...),  # JSON string of operations
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply cleaning operations to a dataset.
    
    Operations should be a JSON string with cleaning parameters.
    
    Example operations:
    {
        "handle_missing": true,
        "missing_strategy": "auto",
        "remove_duplicates": true,
        "handle_outliers": false,
        "normalize": false
    }
    """
    validate_upload(file)
    
    try:
        # Parse operations
        ops = json.loads(operations)
        
        # Save uploaded file temporarily using the safe streamer (enforces size/type/magic-byte checks)
        tmp_path = await safe_save_upload(file)
        
        try:
            # Load file
            df = data_processor.load_file(tmp_path)
            original_shape = df.shape
            
            # Apply cleaning operations
            if ops.get('auto_clean', False):
                df, report = data_cleaner.auto_clean(
                    df,
                    handle_missing=ops.get('handle_missing', True),
                    remove_duplicates=ops.get('remove_duplicates', True),
                    handle_outliers=ops.get('handle_outliers', False),
                    normalize=ops.get('normalize', False)
                )
            else:
                report = {'operations': []}
                
                # Manual operations
                if ops.get('handle_missing'):
                    strategy = ops.get('missing_strategy', 'auto')
                    df = data_cleaner.handle_missing_values(df, strategy=strategy)
                    report['operations'].append(f"Handled missing values with strategy: {strategy}")
                
                if ops.get('remove_duplicates'):
                    df = data_cleaner.remove_duplicates(df)
                    report['operations'].append("Removed duplicate rows")
                
                if ops.get('handle_outliers'):
                    method = ops.get('outlier_method', 'iqr')
                    if ops.get('cap_outliers', False):
                        df = data_cleaner.cap_outliers(df, method=method)
                        report['operations'].append(f"Capped outliers using {method} method")
                    else:
                        df = data_cleaner.remove_outliers(df, method=method)
                        report['operations'].append(f"Removed outliers using {method} method")
                
                if ops.get('normalize'):
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if numeric_cols:
                        method = ops.get('normalize_method', 'standard')
                        df = data_cleaner.normalize_column(df, columns=numeric_cols, method=method)
                        report['operations'].append(f"Normalized columns using {method} method")
            
            cleaned_shape = df.shape
            
            # Convert cleaned data to JSON for response
            # (In production, you might want to save this and return a download link)
            preview = df.head(100).to_dict(orient='records')
            
            return {
                "success": True,
                "message": "Data cleaned successfully",
                "report": report,
                "original_shape": {"rows": original_shape[0], "columns": original_shape[1]},
                "cleaned_shape": {"rows": cleaned_shape[0], "columns": cleaned_shape[1]},
                "preview": preview
            }
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operations JSON"
        )
    except Exception as e:
        logger.error(f"Error cleaning data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cleaning data: {str(e)}"
        )


@router.post("/recommendations")
async def get_recommendations(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get intelligent recommendations for data analysis.
    
    Returns recommendations for cleaning, analysis, visualization, and modeling.
    """
    validate_upload(file)
    
    try:
        # Save uploaded file temporarily using safe async saver (streams, validates extension/content-type/size and does magic-byte checks)
        tmp_path = await safe_save_upload(file)
        
        try:
            # Load file
            df = data_processor.load_file(tmp_path)
            
            # Get recommendations
            recommendations = recommendation_engine.get_recommendations(df)
            
            # Get quick insights
            insights = recommendation_engine.get_quick_insights(df)
            
            return {
                "success": True,
                "recommendations": recommendations,
                "insights": insights
            }
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.post("/optimize")
async def optimize_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Optimize dataset memory usage.
    
    Returns optimized dataset preview and memory reduction statistics.
    """
    validate_upload(file)
    
    try:
        # Save uploaded file temporarily using safe async saver (streams, validates extension/content-type/size and does magic-byte checks)
        tmp_path = await safe_save_upload(file)
        
        try:
            # Load file
            df = data_processor.load_file(tmp_path)
            
            # Get original memory usage
            original_memory = data_processor.get_memory_usage(df)
            
            # Optimize
            optimized_df = data_processor.optimize_memory(df)
            
            # Get optimized memory usage
            optimized_memory = data_processor.get_memory_usage(optimized_df)
            
            # Calculate reduction
            reduction_percent = ((original_memory['total_mb'] - optimized_memory['total_mb']) / 
                               original_memory['total_mb'] * 100)
            
            # Preview
            preview = optimized_df.head(100).to_dict(orient='records')
            
            return {
                "success": True,
                "message": "Data optimized successfully",
                "original_memory_mb": original_memory['total_mb'],
                "optimized_memory_mb": optimized_memory['total_mb'],
                "reduction_percent": reduction_percent,
                "preview": preview
            }
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"Error optimizing data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error optimizing data: {str(e)}"
        )


@router.get("/info/{format}")
async def get_format_info(
    format: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get information about supported file formats.
    
    Args:
        format: File format (csv, excel, json, parquet, tsv, or 'all')
    """
    format_info = {
        "csv": {
            "extensions": [".csv"],
            "description": "Comma-separated values",
            "supports_encoding_detection": True,
            "supports_delimiter_detection": True,
            "max_size_recommendation": "500 MB"
        },
        "excel": {
            "extensions": [".xlsx", ".xls"],
            "description": "Microsoft Excel spreadsheet",
            "supports_multiple_sheets": True,
            "max_size_recommendation": "100 MB"
        },
        "json": {
            "extensions": [".json"],
            "description": "JavaScript Object Notation",
            "supports_nested_structures": True,
            "max_size_recommendation": "100 MB"
        },
        "parquet": {
            "extensions": [".parquet"],
            "description": "Apache Parquet columnar format",
            "optimized_for_large_datasets": True,
            "max_size_recommendation": "1 GB"
        },
        "tsv": {
            "extensions": [".tsv", ".txt"],
            "description": "Tab-separated values",
            "supports_encoding_detection": True,
            "max_size_recommendation": "500 MB"
        }
    }
    
    if format.lower() == "all":
        return {
            "success": True,
            "formats": format_info
        }
    
    if format.lower() in format_info:
        return {
            "success": True,
            "format": format_info[format.lower()]
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Format '{format}' not found"
    )
