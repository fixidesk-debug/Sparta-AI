from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.db.models import File
from app.services.ai_code_generator import AICodeGenerator, CodeGenerationResult, AnalysisType
from app.services.ai_providers import AIProvider
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def _generate_follow_up_questions(query: str, analysis_type: Optional[AnalysisType]) -> List[str]:
    """Generate contextual follow-up questions based on the analysis type."""
    
    # Default questions
    default_questions = [
        "Can you show me the distribution of the data?",
        "What are the key statistics for this dataset?",
        "Are there any outliers or anomalies?"
    ]
    
    if not analysis_type:
        return default_questions
    
    # Type-specific questions
    questions_map = {
        AnalysisType.VISUALIZATION: [
            "Can you create a different type of chart for this data?",
            "What insights can we draw from this visualization?",
            "Can you add trend lines or annotations?"
        ],
        AnalysisType.STATISTICAL: [
            "Can you perform a correlation analysis?",
            "What's the distribution of the key variables?",
            "Are there any significant patterns in the data?"
        ],
        AnalysisType.EXPLORATORY: [
            "What are the key statistics for each column?",
            "Can you show the distribution of values?",
            "Are there any missing values or outliers?"
        ],
        AnalysisType.AGGREGATION: [
            "Can you group by a different column?",
            "What are the top 10 values?",
            "Can you calculate additional aggregate metrics?"
        ],
        AnalysisType.CORRELATION: [
            "Which variables are most strongly correlated?",
            "Can you visualize the correlation matrix?",
            "What relationships exist in the data?"
        ],
        AnalysisType.TIME_SERIES: [
            "What are the trends over time?",
            "Can you forecast future values?",
            "Are there any seasonal patterns?"
        ],
        AnalysisType.CLEANING: [
            "How many missing values are there?",
            "Can you show data quality issues?",
            "What cleaning steps were applied?"
        ]
    }
    
    return questions_map.get(analysis_type, default_questions)


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
        
        # Use Groq as the only AI provider
        provider = AIProvider.GROQ
        
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
            
            # Generate follow-up questions based on the analysis type
            follow_up_questions = _generate_follow_up_questions(query_text, result.analysis_type)
            
            return {
                "success": True,
                "code": result.code,
                "explanation": result.explanation,
                "analysis_type": result.analysis_type.value if result.analysis_type else "custom",
                "metadata": result.metadata,
                "follow_up_questions": follow_up_questions,
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
