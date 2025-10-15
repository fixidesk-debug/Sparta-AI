from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models import Query as QueryModel, User
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core.security import decode_access_token
from app.services.nlp import process_natural_language_query
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    query_text: str
    file_id: Optional[int] = None
    session_id: Optional[str] = None  # For conversation memory

class QueryResponse(BaseModel):
    id: int
    query_text: str
    response: str
    generated_code: Optional[str] = None
    analysis_type: Optional[str] = None
    visualization_data: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True

class CodeGenerationResponse(BaseModel):
    """Enhanced response with code generation details"""
    query_id: int
    success: bool
    code: Optional[str] = None
    explanation: Optional[str] = None
    analysis_type: Optional[str] = None
    error: Optional[str] = None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.post("/ask", response_model=CodeGenerationResponse)
async def ask_query(
    query: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a natural language query and generate Python code for data analysis.
    
    Args:
        query: Query request with query_text, file_id, and optional session_id
        current_user: Authenticated user
        db: Database session
        
    Returns:
        CodeGenerationResponse with generated code and explanation
    """
    try:
        # Process the natural language query
        user_id: int = current_user.id  # type: ignore
        
        logger.info(f"Processing query for user {user_id}: {query.query_text[:50]}...")
        
        result = await process_natural_language_query(
            query.query_text,
            query.file_id,
            user_id,
            db,
            session_id=query.session_id
        )
        
        # Prepare response text
        if result["success"]:
            response_text = result.get("explanation", "Code generated successfully")
            if result.get("code"):
                response_text += f"\n\nGenerated Code:\n{result['code']}"
        else:
            response_text = result.get("error", "Failed to generate code")
        
        # Save query to database
        db_query = QueryModel(
            user_id=user_id,
            file_id=query.file_id,
            query_text=query.query_text,
            response=response_text,
            generated_code=result.get("code"),
            execution_status="pending" if result["success"] else "failed",
            error_message=result.get("error")
        )
        db.add(db_query)
        db.commit()
        db.refresh(db_query)
        
        logger.info(f"Query saved with ID: {db_query.id}")
        
        return CodeGenerationResponse(
            query_id=getattr(db_query, 'id'),
            success=result["success"],
            code=result.get("code"),
            explanation=result.get("explanation"),
            analysis_type=result.get("analysis_type"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.exception(f"Error in ask_query endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@router.get("/history", response_model=List[QueryResponse])
def get_query_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    queries = db.query(QueryModel).filter(
        QueryModel.user_id == current_user.id
    ).order_by(QueryModel.created_at.desc()).limit(limit).all()
    
    return queries

@router.get("/{query_id}", response_model=QueryResponse)
def get_query(
    query_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(QueryModel).filter(
        QueryModel.id == query_id,
        QueryModel.user_id == current_user.id
    ).first()
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return query
