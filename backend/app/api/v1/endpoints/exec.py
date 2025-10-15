from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.db.session import get_db
from app.db.models import User, File, Query as QueryModel
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token
from app.services.code_executor import CodeExecutor
import logging
import pandas as pd

logger = logging.getLogger(__name__)

router = APIRouter()


class CodeExecutionRequest(BaseModel):
    """Request model for code execution"""
    code: str = Field(..., description="Python code to execute")
    file_id: Optional[int] = Field(None, description="File ID to load data from")
    query_id: Optional[int] = Field(None, description="Query ID associated with this execution")
    timeout_seconds: int = Field(30, ge=1, le=300, description="Execution timeout in seconds")
    max_memory_mb: int = Field(512, ge=128, le=2048, description="Maximum memory in MB")


class CodeExecutionResponse(BaseModel):
    """Response model for code execution"""
    success: bool = Field(..., description="Whether execution was successful")
    output: str = Field("", description="Captured stdout output")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    images: List[str] = Field(default_factory=list, description="Base64-encoded matplotlib plots")
    plotly_figures: List[Dict[str, Any]] = Field(default_factory=list, description="Plotly figure data")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Output variables")
    timestamp: str = Field(..., description="Execution timestamp")


class CodeValidationRequest(BaseModel):
    """Request model for code validation"""
    code: str = Field(..., description="Python code to validate")


class CodeValidationResponse(BaseModel):
    """Response model for code validation"""
    valid: bool = Field(..., description="Whether code is valid")
    error: Optional[str] = Field(None, description="Validation error message")
    timestamp: str = Field(..., description="Validation timestamp")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email: Optional[str] = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code_endpoint(
    execution_request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute Python code in a secure sandboxed environment.
    
    Security features:
    - Restricted imports (data science libraries only)
    - Execution timeout
    - Memory limits
    - File system isolation
    - Output capture and sanitization
    
    Args:
        execution_request: Code execution request with code and parameters
        current_user: Authenticated user
        db: Database session
        
    Returns:
        CodeExecutionResponse with execution results
    """
    try:
        user_id: int = current_user.id  # type: ignore
        
        logger.info(f"Executing code for user {user_id}, file_id={execution_request.file_id}")
        
        # Prepare execution context
        context: Dict[str, Any] = {}
        
        # Load dataframe if file_id is provided
        if execution_request.file_id:
            file = db.query(File).filter(
                File.id == execution_request.file_id,
                File.user_id == user_id
            ).first()
            
            if not file:
                raise HTTPException(
                    status_code=404,
                    detail=f"File {execution_request.file_id} not found"
                )
            
            try:
                # Load the dataframe
                df = pd.read_csv(str(file.file_path))
                context['df'] = df
                logger.info(f"Loaded dataframe with shape {df.shape}")
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to load file: {str(e)}"
                )
        
        # Create executor with specified limits
        executor = CodeExecutor(
            timeout_seconds=execution_request.timeout_seconds,
            max_memory_mb=execution_request.max_memory_mb
        )
        
        # Execute the code
        result = executor.execute(
            code=execution_request.code,
            context=context
        )
        
        # Update query execution status if query_id provided
        if execution_request.query_id:
            query = db.query(QueryModel).filter(
                QueryModel.id == execution_request.query_id,
                QueryModel.user_id == user_id
            ).first()
            
            if query:
                if result['success']:
                    setattr(query, 'execution_status', 'completed')
                    setattr(query, 'execution_result', result['output'])
                else:
                    setattr(query, 'execution_status', 'failed')
                    setattr(query, 'error_message', result['error'])
                
                db.commit()
                logger.info(f"Updated query {execution_request.query_id} status to {query.execution_status}")
        
        logger.info(f"Code execution completed: success={result['success']}, time={result['execution_time']:.2f}s")
        
        return CodeExecutionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in execute_code_endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Code execution failed: {str(e)}"
        )


@router.post("/validate", response_model=CodeValidationResponse)
async def validate_code_endpoint(
    validation_request: CodeValidationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Validate Python code without executing it.
    
    Checks for:
    - Syntax errors
    - Security violations
    - Forbidden operations
    
    Args:
        validation_request: Code validation request
        current_user: Authenticated user
        
    Returns:
        CodeValidationResponse with validation results
    """
    try:
        executor = CodeExecutor()
        result = executor.validate_code(validation_request.code)
        
        return CodeValidationResponse(**result)
        
    except Exception as e:
        logger.exception(f"Error in validate_code_endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Code validation failed: {str(e)}"
        )


# Keep legacy endpoint for backwards compatibility
@router.post("/run", response_model=CodeExecutionResponse)
async def execute_code_legacy(
    execution_request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Legacy endpoint for code execution (redirects to /execute).
    Maintained for backwards compatibility.
    """
    return await execute_code_endpoint(execution_request, current_user, db)
