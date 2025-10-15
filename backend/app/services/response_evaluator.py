"""
Response Evaluator - Quality assessment and scoring system
Evaluates AI responses for quality, relevance, and correctness
"""
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Dimensions of response quality"""
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CLARITY = "clarity"
    COHERENCE = "coherence"
    CREATIVITY = "creativity"


@dataclass
class ResponseQuality:
    """Quality assessment results"""
    overall_score: float  # 0-1
    dimension_scores: Dict[QualityDimension, float]
    issues: List[str]
    strengths: List[str]
    confidence: float


class ResponseEvaluator:
    """
    Evaluate AI response quality
    
    Features:
    - Multi-dimensional quality scoring
    - Task-specific evaluation criteria
    - Heuristic-based assessment
    - Pattern detection for common issues
    """
    
    def __init__(self):
        """Initialize response evaluator"""
        # Patterns for quality issues
        self.issue_patterns = {
            "incomplete": [
                r"(?:to be continued|part \d+|continued in)",
                r"(?:will continue|let me continue|more to come)"
            ],
            "uncertainty": [
                r"(?:i'm not sure|i don't know|unclear|uncertain)",
                r"(?:might be|could be|possibly|perhaps)"
            ],
            "apology": [
                r"(?:i apologize|sorry|my apologies)",
                r"(?:unfortunately|regrettably)"
            ],
            "generic": [
                r"(?:as an ai|i'm an ai assistant|i'm a language model)"
            ]
        }
        
        logger.info("ResponseEvaluator initialized")
    
    async def evaluate(
        self,
        messages: List[Dict[str, str]],
        response: str,
        task_type: 'TaskType'  # type: ignore
    ) -> ResponseQuality:
        """
        Evaluate response quality
        
        Args:
            messages: Conversation context
            response: AI response to evaluate
            task_type: Type of task
            
        Returns:
            Quality assessment with scores and feedback
        """
        from .model_selector import TaskType
        
        # Calculate dimension scores
        dimension_scores = {}
        
        dimension_scores[QualityDimension.RELEVANCE] = await self._score_relevance(
            messages, response, task_type
        )
        
        dimension_scores[QualityDimension.COMPLETENESS] = await self._score_completeness(
            response, task_type
        )
        
        dimension_scores[QualityDimension.ACCURACY] = await self._score_accuracy(
            response, task_type
        )
        
        dimension_scores[QualityDimension.CLARITY] = await self._score_clarity(response)
        
        dimension_scores[QualityDimension.COHERENCE] = await self._score_coherence(response)
        
        if task_type == TaskType.CREATIVE_WRITING:
            dimension_scores[QualityDimension.CREATIVITY] = await self._score_creativity(response)
        
        # Calculate overall score (weighted average)
        weights = self._get_dimension_weights(task_type)
        overall_score = sum(
            score * weights.get(dim, 1.0)
            for dim, score in dimension_scores.items()
        ) / sum(weights.values())
        
        # Detect issues and strengths
        issues = self._detect_issues(response)
        strengths = self._detect_strengths(response, dimension_scores)
        
        # Calculate confidence based on clarity and consistency
        confidence = (
            dimension_scores[QualityDimension.CLARITY] * 0.5 +
            dimension_scores[QualityDimension.COHERENCE] * 0.5
        )
        
        return ResponseQuality(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            issues=issues,
            strengths=strengths,
            confidence=confidence
        )
    
    async def _score_relevance(
        self,
        messages: List[Dict[str, str]],
        response: str,
        task_type: 'TaskType'  # type: ignore
    ) -> float:
        """Score how relevant response is to the query"""
        if not messages:
            return 0.5
        
        # Get last user message
        user_messages = [m for m in messages if m.get("role") == "user"]
        if not user_messages:
            return 0.5
        
        query = user_messages[-1].get("content", "")
        
        # Extract key terms from query
        query_terms = set(self._extract_key_terms(query.lower()))
        response_terms = set(self._extract_key_terms(response.lower()))
        
        # Calculate term overlap
        if not query_terms:
            return 0.5
        
        overlap = len(query_terms & response_terms) / len(query_terms)
        
        # Boost score if response directly addresses query
        if self._addresses_query(query, response):
            overlap = min(1.0, overlap + 0.2)
        
        return overlap
    
    async def _score_completeness(self, response: str, task_type: 'TaskType') -> float:  # type: ignore
        """Score how complete the response is"""
        from .model_selector import TaskType
        
        score = 1.0
        
        # Check for incompleteness indicators
        for pattern in self.issue_patterns["incomplete"]:
            if re.search(pattern, response.lower()):
                score -= 0.3
        
        # Check length appropriateness
        min_lengths = {
            TaskType.CODE_GENERATION: 50,
            TaskType.DATA_ANALYSIS: 100,
            TaskType.CREATIVE_WRITING: 200,
            TaskType.CONVERSATION: 20,
            TaskType.SUMMARIZATION: 50
        }
        
        min_length = min_lengths.get(task_type, 30)
        if len(response) < min_length:
            score -= 0.2
        
        # Check for truncation
        if response.endswith("...") or response.endswith("…"):
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    async def _score_accuracy(self, response: str, task_type: 'TaskType') -> float:  # type: ignore
        """Score accuracy indicators"""
        from .model_selector import TaskType
        
        score = 0.7  # Neutral baseline
        
        # Boost for specific task types with verifiable structure
        if task_type in [TaskType.CODE_GENERATION, TaskType.MATH]:
            # Check for code blocks or mathematical notation
            if "```" in response or re.search(r'\$.*\$', response):
                score += 0.2
        
        # Penalize uncertainty
        uncertainty_count = sum(
            len(re.findall(pattern, response.lower()))
            for pattern in self.issue_patterns["uncertainty"]
        )
        score -= min(0.3, uncertainty_count * 0.1)
        
        # Penalize excessive apologies
        apology_count = sum(
            len(re.findall(pattern, response.lower()))
            for pattern in self.issue_patterns["apology"]
        )
        score -= min(0.2, apology_count * 0.1)
        
        return max(0.0, min(1.0, score))
    
    async def _score_clarity(self, response: str) -> float:
        """Score clarity and readability"""
        score = 0.5
        
        # Check sentence structure
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.3
        
        # Average sentence length (optimal: 15-25 words)
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if 15 <= avg_length <= 25:
            score += 0.2
        elif avg_length < 10 or avg_length > 40:
            score -= 0.1
        
        # Check for formatting
        has_formatting = bool(
            re.search(r'(```|###|\*\*|__|\n\n)', response)
        )
        if has_formatting:
            score += 0.1
        
        # Check for proper capitalization
        properly_capitalized = sum(
            1 for s in sentences if s and s[0].isupper()
        )
        capitalization_ratio = properly_capitalized / len(sentences)
        score += 0.2 * capitalization_ratio
        
        return max(0.0, min(1.0, score))
    
    async def _score_coherence(self, response: str) -> float:
        """Score logical flow and coherence"""
        score = 0.7
        
        # Check for logical connectors
        connectors = [
            "however", "therefore", "thus", "hence", "moreover",
            "furthermore", "additionally", "consequently", "meanwhile",
            "first", "second", "finally", "in conclusion"
        ]
        
        connector_count = sum(
            1 for connector in connectors
            if connector in response.lower()
        )
        
        # Boost for presence of connectors (but not too many)
        if 1 <= connector_count <= 5:
            score += 0.2
        elif connector_count > 5:
            score += 0.1
        
        # Check for paragraph structure
        paragraphs = response.split("\n\n")
        if len(paragraphs) > 1:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    async def _score_creativity(self, response: str) -> float:
        """Score creativity and originality"""
        score = 0.5
        
        # Check vocabulary diversity
        words = response.lower().split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            score += 0.3 * unique_ratio
        
        # Check for descriptive language
        descriptive_patterns = [
            r'\b(vivid|colorful|striking|brilliant|magnificent)\b',
            r'\b(gentle|fierce|subtle|profound|intricate)\b'
        ]
        
        for pattern in descriptive_patterns:
            if re.search(pattern, response.lower()):
                score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _get_dimension_weights(self, task_type: 'TaskType') -> Dict[QualityDimension, float]:  # type: ignore
        """Get dimension weights for task type"""
        from .model_selector import TaskType
        
        # Default weights
        weights = {
            QualityDimension.RELEVANCE: 2.0,
            QualityDimension.COMPLETENESS: 1.5,
            QualityDimension.ACCURACY: 1.5,
            QualityDimension.CLARITY: 1.0,
            QualityDimension.COHERENCE: 1.0
        }
        
        # Task-specific adjustments
        if task_type in [TaskType.CODE_GENERATION, TaskType.MATH]:
            weights[QualityDimension.ACCURACY] = 2.5
            weights[QualityDimension.COMPLETENESS] = 2.0
        elif task_type == TaskType.CREATIVE_WRITING:
            weights[QualityDimension.CREATIVITY] = 2.0
            weights[QualityDimension.COHERENCE] = 1.5
        elif task_type == TaskType.SUMMARIZATION:
            weights[QualityDimension.COMPLETENESS] = 2.0
            weights[QualityDimension.CLARITY] = 1.5
        
        return weights
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text"""
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "from", "as", "is", "was",
            "are", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "will", "would", "should", "could",
            "may", "might", "can", "this", "that", "these", "those"
        }
        
        # Extract words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter stop words and short words
        return [w for w in words if w not in stop_words and len(w) > 2]
    
    def _addresses_query(self, query: str, response: str) -> bool:
        """Check if response directly addresses query"""
        # Check for direct answer patterns
        answer_patterns = [
            r'^(yes|no|sure|certainly|absolutely),',
            r'^(the answer is|the solution is|to do this)',
            r'^(here\'s|here is|this is)'
        ]
        
        for pattern in answer_patterns:
            if re.search(pattern, response.lower()):
                return True
        
        return False
    
    def _detect_issues(self, response: str) -> List[str]:
        """Detect quality issues in response"""
        issues = []
        
        # Check each issue type
        for issue_type, patterns in self.issue_patterns.items():
            for pattern in patterns:
                if re.search(pattern, response.lower()):
                    issues.append(f"Contains {issue_type} language")
                    break
        
        # Check for very short responses
        if len(response) < 20:
            issues.append("Response is very short")
        
        # Check for repetition
        sentences = re.split(r'[.!?]+', response)
        unique_sentences = set(s.strip().lower() for s in sentences if s.strip())
        if len(sentences) > 3 and len(unique_sentences) < len(sentences) * 0.7:
            issues.append("Contains repetitive content")
        
        return issues
    
    def _detect_strengths(
        self,
        response: str,
        dimension_scores: Dict[QualityDimension, float]
    ) -> List[str]:
        """Detect strengths in response"""
        strengths = []
        
        # Check high-scoring dimensions
        for dimension, score in dimension_scores.items():
            if score >= 0.8:
                strengths.append(f"High {dimension.value}")
        
        # Check for code examples
        if "```" in response:
            strengths.append("Includes code examples")
        
        # Check for structured content
        if re.search(r'(?:###|\*\*|\d+\.)', response):
            strengths.append("Well-structured formatting")
        
        # Check for detailed explanation
        if len(response) > 500:
            strengths.append("Comprehensive and detailed")
        
        return strengths


async def compare_responses(
    responses: List[str],
    messages: List[Dict[str, str]],
    task_type: 'TaskType'  # type: ignore
) -> List[Tuple[int, ResponseQuality]]:
    """
    Compare multiple responses and rank by quality
    
    Args:
        responses: List of responses to compare
        messages: Conversation context
        task_type: Type of task
        
    Returns:
        List of (index, quality) sorted by quality score (best first)
    """
    evaluator = ResponseEvaluator()
    
    evaluations = []
    for i, response in enumerate(responses):
        quality = await evaluator.evaluate(messages, response, task_type)
        evaluations.append((i, quality))
    
    # Sort by overall score (descending)
    evaluations.sort(key=lambda x: x[1].overall_score, reverse=True)
    
    return evaluations
