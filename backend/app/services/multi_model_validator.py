"""
Multi-Model Validator using Groq's Multiple Models
"""
from typing import Dict, Any, List
import logging
from app.services.groq_provider import GroqProvider

logger = logging.getLogger(__name__)


class MultiModelValidator:
    """Validate code using multiple Groq models"""
    
    VALIDATION_MODELS = [
        "llama-3.3-70b-versatile",  # Best for reasoning
        "llama-3.1-70b-versatile",  # Good for validation
        "mixtral-8x7b-32768"        # Fast alternative
    ]
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.providers = [
            GroqProvider(api_key, model) for model in self.VALIDATION_MODELS
        ]
    
    async def validate_code(
        self,
        query: str,
        code: str,
        data_context: str
    ) -> Dict[str, Any]:
        """
        Validate code using multiple models
        
        Returns aggregated validation score
        """
        try:
            validation_prompt = f"""Review this Python data analysis code for correctness.

User Query: {query}

Data Context:
{data_context}

Generated Code:
```python
{code}
```

Rate 0-100 on:
1. Correctness: Answers query correctly?
2. Safety: No security issues?
3. Efficiency: Optimized?
4. Robustness: Handles edge cases?

Respond with JSON:
{{"score": <0-100>, "issues": ["list"], "suggestions": ["list"]}}
"""
            
            messages = [
                {"role": "system", "content": "You are a code review expert. Be critical and honest."},
                {"role": "user", "content": validation_prompt}
            ]
            
            # Get validations from all models
            validations = []
            for i, provider in enumerate(self.providers):
                try:
                    response = await provider.generate_completion(
                        messages, temperature=0.1, max_tokens=1000
                    )
                    
                    # Parse JSON response
                    import json
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                        result["model"] = self.VALIDATION_MODELS[i]
                        validations.append(result)
                except Exception as e:
                    logger.error(f"Validation error with model {i}: {e}")
                    continue
            
            if not validations:
                return {"score": 50, "validated": False, "reason": "No validations completed"}
            
            # Aggregate scores
            avg_score = sum(v.get("score", 0) for v in validations) / len(validations)
            all_issues = []
            all_suggestions = []
            
            for v in validations:
                all_issues.extend(v.get("issues", []))
                all_suggestions.extend(v.get("suggestions", []))
            
            # Remove duplicates
            all_issues = list(set(all_issues))
            all_suggestions = list(set(all_suggestions))
            
            return {
                "score": avg_score,
                "validated": avg_score >= 85,
                "issues": all_issues,
                "suggestions": all_suggestions,
                "model_scores": [v.get("score", 0) for v in validations],
                "consensus": max(v.get("score", 0) for v in validations) - min(v.get("score", 0) for v in validations) < 20
            }
            
        except Exception as e:
            logger.error(f"Multi-model validation error: {e}")
            return {"score": 0, "validated": False, "reason": str(e)}
    
    async def self_correct_code(
        self,
        original_code: str,
        validation_result: Dict[str, Any],
        query: str,
        data_context: str
    ) -> str:
        """
        Self-correct code using best model
        """
        try:
            if validation_result.get("score", 0) >= 90:
                return original_code
            
            issues = validation_result.get("issues", [])
            suggestions = validation_result.get("suggestions", [])
            
            correction_prompt = f"""Improve this Python code based on feedback.

Original Query: {query}

Data Context:
{data_context}

Current Code:
```python
{original_code}
```

Issues: {', '.join(issues)}
Suggestions: {', '.join(suggestions)}

Generate improved code. Return ONLY Python code, no explanations.
"""
            
            messages = [
                {"role": "system", "content": "You are an expert code improver. Generate only corrected code."},
                {"role": "user", "content": correction_prompt}
            ]
            
            # Use best model for correction
            best_provider = self.providers[0]
            corrected_code = await best_provider.generate_completion(
                messages, temperature=0.2, max_tokens=2000
            )
            
            # Clean response
            corrected_code = corrected_code.replace("```python", "").replace("```", "").strip()
            
            return corrected_code
            
        except Exception as e:
            logger.error(f"Self-correction error: {e}")
            return original_code
    
    async def iterative_improvement(
        self,
        query: str,
        initial_code: str,
        data_context: str,
        max_iterations: int = 2
    ) -> Dict[str, Any]:
        """
        Iteratively improve code
        """
        current_code = initial_code
        iteration = 0
        best_score = 0
        best_code = initial_code
        
        while iteration < max_iterations:
            # Validate
            validation = await self.validate_code(query, current_code, data_context)
            
            score = validation.get("score", 0)
            if score > best_score:
                best_score = score
                best_code = current_code
            
            # Check if good enough
            if validation.get("validated", False):
                return {
                    "final_code": current_code,
                    "iterations": iteration + 1,
                    "final_score": score,
                    "success": True
                }
            
            # Try to improve
            improved_code = await self.self_correct_code(
                current_code, validation, query, data_context
            )
            
            if improved_code == current_code:
                break
            
            current_code = improved_code
            iteration += 1
        
        return {
            "final_code": best_code,
            "iterations": iteration + 1,
            "final_score": best_score,
            "success": best_score >= 85
        }
