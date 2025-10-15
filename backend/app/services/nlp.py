from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import File
from app.services.ai_code_generator import AICodeGenerator, CodeGenerationResult
from app.services.ai_providers import AIProvider
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


async def process_natural_language_query(
    query_text: str,
    file_id: Optional[int],
    user_id: int,
    db: Session,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process natural language queries and generate Python code for data analysis.
    
    Args:
        query_text: Natural language query from user
        file_id: Optional file ID to analyze
        user_id: User ID
        db: Database session
        session_id: Optional session ID for conversation memory
        
    Returns:
        Dictionary with code, explanation, and metadata
    """
    
    try:
        # Validate that file exists if file_id is provided
        if file_id:
            file = db.query(File).filter(
                File.id == file_id,
                File.user_id == user_id
            ).first()
            
            if not file:
                return {
                    "success": False,
                    "error": "File not found",
                    "code": None,
                    "explanation": None
                }
        
        # Determine AI provider
        provider_name = settings.DEFAULT_AI_PROVIDER.lower()
        if provider_name == "anthropic" and settings.ANTHROPIC_API_KEY:
            provider = AIProvider.ANTHROPIC
        else:
            provider = AIProvider.OPENAI
        
        # Create AI code generator
        generator = AICodeGenerator(
            provider=provider,
            temperature=settings.CODE_GENERATION_TEMPERATURE,
            max_tokens=settings.CODE_GENERATION_MAX_TOKENS
        )
        
        # Generate code
        logger.info(f"Processing query: {query_text[:100]}... for user {user_id}")
        
        if not file_id:
            return {
                "success": False,
                "error": "File ID is required for code generation",
                "code": None,
                "explanation": None
            }
        
        result: CodeGenerationResult = await generator.generate_code(
            query=query_text,
            file_id=file_id,
            user_id=user_id,
            db=db,
            session_id=session_id
        )
        
        # Return result
        if result.is_valid:
            logger.info(f"Successfully generated code for query: {query_text[:50]}...")
            return {
                "success": True,
                "code": result.code,
                "explanation": result.explanation,
                "analysis_type": result.analysis_type.value if result.analysis_type else "custom",
                "metadata": result.metadata,
                "error": None
            }
        else:
            logger.warning(f"Code validation failed: {result.error}")
            return {
                "success": False,
                "error": f"Code validation failed: {result.error}",
                "code": result.code,  # Return code anyway for debugging
                "explanation": result.explanation,
                "metadata": result.metadata
            }
        
    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        return {
            "success": False,
            "error": f"Error processing query: {str(e)}",
            "code": None,
            "explanation": None
        }
