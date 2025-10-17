"""
Accuracy Enhancer - Multi-Model Validation and Self-Correction
"""
from typing import Dict, Any, List, Optional
import logging
from app.services.multi_model_validator import MultiModelValidator

logger = logging.getLogger(__name__)


class AccuracyEnhancer:
    """Enhance accuracy through multi-model validation and self-correction"""
    
    def __init__(self, api_key: str):
        self.validator = MultiModelValidator(api_key)
        self.validation_threshold = 0.85
    
    async def validate_with_multiple_models(
        self,
        query: str,
        code: str,
        data_context: str
    ) -> Dict[str, Any]:
        return await self.validator.validate_code(query, code, data_context)
    
    async def self_correct_code(
        self,
        original_code: str,
        validation_result: Dict[str, Any],
        query: str,
        data_context: str
    ) -> Optional[str]:
        return await self.validator.self_correct_code(
            original_code, validation_result, query, data_context
        )
    
    async def iterative_improvement(
        self,
        query: str,
        initial_code: str,
        data_context: str,
        max_iterations: int = 2
    ) -> Dict[str, Any]:
        return await self.validator.iterative_improvement(
            query, initial_code, data_context, max_iterations
        )
    
    @staticmethod
    def calculate_confidence_score(
        code: str,
        validation_result: Dict[str, Any],
        execution_success: bool
    ) -> float:
        """
        Calculate overall confidence score (0-1)
        """
        # Base score from validation
        validation_score = validation_result.get("score", 50) / 100
        
        # Execution success bonus
        execution_bonus = 0.2 if execution_success else -0.3
        
        # Code quality factors
        quality_score = 0.0
        
        # Has error handling
        if "try:" in code and "except" in code:
            quality_score += 0.1
        
        # Has input validation
        if "assert" in code or "if len(df)" in code:
            quality_score += 0.1
        
        # Has comments
        if code.count("#") >= 3:
            quality_score += 0.05
        
        # Not too long (maintainable)
        if len(code.split("\n")) < 100:
            quality_score += 0.05
        
        # Calculate final score
        confidence = min(1.0, max(0.0, validation_score + execution_bonus + quality_score))
        
        return confidence
