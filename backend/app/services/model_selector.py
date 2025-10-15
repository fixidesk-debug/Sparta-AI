"""
Model Selector - Intelligent model selection based on task requirements
Analyzes task complexity and selects optimal model
"""
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ai_provider_manager import ProviderType

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of AI tasks with different requirements"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    DATA_ANALYSIS = "data_analysis"
    CONVERSATION = "conversation"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CREATIVE_WRITING = "creative_writing"
    QUESTION_ANSWERING = "question_answering"
    REASONING = "reasoning"
    MATH = "math"
    GENERAL = "general"


class ModelCapability(Enum):
    """Model capability levels"""
    BASIC = "basic"  # Simple tasks, fast responses
    STANDARD = "standard"  # Most general tasks
    ADVANCED = "advanced"  # Complex reasoning, code generation
    EXPERT = "expert"  # Highest quality, complex tasks


@dataclass
class ModelInfo:
    """Information about a specific model"""
    provider: 'ProviderType'  # type: ignore
    model_name: str
    capability: ModelCapability
    context_window: int
    cost_tier: int  # 1=cheap, 5=expensive
    speed_tier: int  # 1=fast, 5=slow
    quality_tier: int  # 1=basic, 5=expert
    strengths: List[TaskType]
    max_output_tokens: int = 4096


@dataclass
class ModelSelection:
    """Selected model with reasoning"""
    provider: 'ProviderType'  # type: ignore
    model_name: str
    confidence: float
    reasoning: str
    estimated_cost: float
    estimated_latency_ms: float


class ModelSelector:
    """
    Intelligent model selection system
    
    Selects the best model based on:
    - Task type and complexity
    - Context length requirements
    - Cost constraints
    - Quality requirements
    - Speed requirements
    """
    
    def __init__(self, provider_configs: List):
        """
        Initialize model selector
        
        Args:
            provider_configs: List of ProviderConfig objects
        """
        self.provider_configs = provider_configs
        self.model_database = self._build_model_database()
        
        # Task complexity scoring
        self.task_complexity = {
            TaskType.CONVERSATION: 1,
            TaskType.SUMMARIZATION: 2,
            TaskType.QUESTION_ANSWERING: 2,
            TaskType.TRANSLATION: 2,
            TaskType.DATA_ANALYSIS: 3,
            TaskType.CREATIVE_WRITING: 3,
            TaskType.CODE_REVIEW: 4,
            TaskType.CODE_GENERATION: 4,
            TaskType.REASONING: 4,
            TaskType.MATH: 5,
            TaskType.GENERAL: 2
        }
        
        logger.info(f"ModelSelector initialized with {len(self.model_database)} models")
    
    def _build_model_database(self) -> Dict[str, ModelInfo]:
        """Build database of available models with capabilities"""
        from .ai_provider_manager import ProviderType
        
        models = {}
        
        # OpenAI Models
        models["gpt-4"] = ModelInfo(
            provider=ProviderType.OPENAI,
            model_name="gpt-4",
            capability=ModelCapability.EXPERT,
            context_window=8192,
            cost_tier=5,
            speed_tier=4,
            quality_tier=5,
            strengths=[
                TaskType.CODE_GENERATION,
                TaskType.REASONING,
                TaskType.MATH,
                TaskType.CODE_REVIEW
            ],
            max_output_tokens=4096
        )
        
        models["gpt-4-turbo-preview"] = ModelInfo(
            provider=ProviderType.OPENAI,
            model_name="gpt-4-turbo-preview",
            capability=ModelCapability.EXPERT,
            context_window=128000,
            cost_tier=4,
            speed_tier=3,
            quality_tier=5,
            strengths=[
                TaskType.CODE_GENERATION,
                TaskType.DATA_ANALYSIS,
                TaskType.REASONING
            ],
            max_output_tokens=4096
        )
        
        models["gpt-3.5-turbo"] = ModelInfo(
            provider=ProviderType.OPENAI,
            model_name="gpt-3.5-turbo",
            capability=ModelCapability.STANDARD,
            context_window=16385,
            cost_tier=1,
            speed_tier=1,
            quality_tier=3,
            strengths=[
                TaskType.CONVERSATION,
                TaskType.QUESTION_ANSWERING,
                TaskType.SUMMARIZATION
            ],
            max_output_tokens=4096
        )
        
        # Anthropic Models
        models["claude-3-5-sonnet-20240620"] = ModelInfo(
            provider=ProviderType.ANTHROPIC,
            model_name="claude-3-5-sonnet-20240620",
            capability=ModelCapability.EXPERT,
            context_window=200000,
            cost_tier=3,
            speed_tier=2,
            quality_tier=5,
            strengths=[
                TaskType.CODE_GENERATION,
                TaskType.CODE_REVIEW,
                TaskType.DATA_ANALYSIS,
                TaskType.REASONING,
                TaskType.CREATIVE_WRITING
            ],
            max_output_tokens=4096
        )
        
        models["claude-3-haiku-20240307"] = ModelInfo(
            provider=ProviderType.ANTHROPIC,
            model_name="claude-3-haiku-20240307",
            capability=ModelCapability.STANDARD,
            context_window=200000,
            cost_tier=1,
            speed_tier=1,
            quality_tier=3,
            strengths=[
                TaskType.CONVERSATION,
                TaskType.SUMMARIZATION,
                TaskType.QUESTION_ANSWERING
            ],
            max_output_tokens=4096
        )
        
        # Google Models
        models["gemini-pro"] = ModelInfo(
            provider=ProviderType.GOOGLE,
            model_name="gemini-pro",
            capability=ModelCapability.ADVANCED,
            context_window=30720,
            cost_tier=2,
            speed_tier=2,
            quality_tier=4,
            strengths=[
                TaskType.REASONING,
                TaskType.DATA_ANALYSIS,
                TaskType.QUESTION_ANSWERING
            ],
            max_output_tokens=2048
        )
        
        models["gemini-flash"] = ModelInfo(
            provider=ProviderType.GOOGLE,
            model_name="gemini-flash",
            capability=ModelCapability.STANDARD,
            context_window=30720,
            cost_tier=1,
            speed_tier=1,
            quality_tier=3,
            strengths=[
                TaskType.CONVERSATION,
                TaskType.SUMMARIZATION
            ],
            max_output_tokens=2048
        )
        
        return models
    
    async def select_model(
        self,
        task_type: TaskType,
        context_length: int = 0,
        optimize_for_cost: bool = False,
        optimize_for_speed: bool = False,
        min_quality_tier: int = 3
    ) -> ModelSelection:
        """
        Select best model for task
        
        Args:
            task_type: Type of task to perform
            context_length: Estimated context length in tokens
            optimize_for_cost: Prioritize lower cost
            optimize_for_speed: Prioritize faster response
            min_quality_tier: Minimum quality tier (1-5)
            
        Returns:
            Selected model with reasoning
        """
        complexity = self.task_complexity.get(task_type, 2)
        
        # Filter models by availability and constraints
        candidates = []
        for model_name, model_info in self.model_database.items():
            # Check if provider is configured
            if not any(c.provider_type == model_info.provider for c in self.provider_configs):
                continue
            
            # Check context window
            if context_length > model_info.context_window:
                continue
            
            # Check quality requirement
            if model_info.quality_tier < min_quality_tier:
                continue
            
            # Calculate score
            score = self._calculate_model_score(
                model_info,
                task_type,
                complexity,
                optimize_for_cost,
                optimize_for_speed
            )
            
            candidates.append((score, model_info))
        
        if not candidates:
            raise Exception(
                f"No suitable model found for task {task_type.value} "
                f"with context length {context_length}"
            )
        
        # Sort by score (descending)
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        # Select best model
        best_score, best_model = candidates[0]
        
        # Calculate confidence (normalized score)
        max_possible_score = 100.0
        confidence = min(best_score / max_possible_score, 1.0)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            best_model,
            task_type,
            complexity,
            optimize_for_cost,
            optimize_for_speed
        )
        
        # Estimate cost and latency
        estimated_cost = self._estimate_cost(best_model, context_length)
        estimated_latency = self._estimate_latency(best_model, context_length)
        
        return ModelSelection(
            provider=best_model.provider,
            model_name=best_model.model_name,
            confidence=confidence,
            reasoning=reasoning,
            estimated_cost=estimated_cost,
            estimated_latency_ms=estimated_latency
        )
    
    def _calculate_model_score(
        self,
        model: ModelInfo,
        task_type: TaskType,
        complexity: int,
        optimize_for_cost: bool,
        optimize_for_speed: bool
    ) -> float:
        """Calculate model suitability score"""
        score = 0.0
        
        # Base score from capability match
        capability_scores = {
            ModelCapability.BASIC: 1,
            ModelCapability.STANDARD: 2,
            ModelCapability.ADVANCED: 4,
            ModelCapability.EXPERT: 5
        }
        
        required_capability = complexity
        model_capability = capability_scores[model.capability]
        
        if model_capability >= required_capability:
            score += 30.0
        else:
            score += 10.0 * (model_capability / required_capability)
        
        # Task type strength bonus
        if task_type in model.strengths:
            score += 25.0
        
        # Quality score
        score += model.quality_tier * 5.0
        
        # Cost optimization
        if optimize_for_cost:
            # Lower cost = higher score
            cost_score = (6 - model.cost_tier) * 5.0
            score += cost_score
        
        # Speed optimization
        if optimize_for_speed:
            # Lower speed tier = faster = higher score
            speed_score = (6 - model.speed_tier) * 5.0
            score += speed_score
        
        # Context window bonus (larger is better)
        if model.context_window >= 100000:
            score += 10.0
        elif model.context_window >= 30000:
            score += 5.0
        
        return score
    
    def _generate_reasoning(
        self,
        model: ModelInfo,
        task_type: TaskType,
        complexity: int,
        optimize_for_cost: bool,
        optimize_for_speed: bool
    ) -> str:
        """Generate human-readable reasoning for selection"""
        reasons = []
        
        reasons.append(
            f"Selected {model.model_name} ({model.provider.value}) "
            f"for {task_type.value} task"
        )
        
        if task_type in model.strengths:
            reasons.append(f"Model specializes in {task_type.value}")
        
        if optimize_for_cost:
            reasons.append(f"Cost-optimized (tier {model.cost_tier}/5)")
        
        if optimize_for_speed:
            reasons.append(f"Speed-optimized (tier {model.speed_tier}/5)")
        
        reasons.append(f"Quality tier: {model.quality_tier}/5")
        reasons.append(f"Context window: {model.context_window:,} tokens")
        
        return ". ".join(reasons) + "."
    
    def _estimate_cost(self, model: ModelInfo, context_length: int) -> float:
        """Estimate cost for request"""
        # Find provider config
        config = next(
            (c for c in self.provider_configs if c.provider_type == model.provider),
            None
        )
        
        if not config:
            return 0.0
        
        # Estimate tokens (input + output)
        input_tokens = context_length
        output_tokens = 500  # Average estimate
        
        input_cost = (input_tokens / 1000) * config.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output_tokens
        
        return input_cost + output_cost
    
    def _estimate_latency(self, model: ModelInfo, context_length: int) -> float:
        """Estimate response latency in milliseconds"""
        # Base latency by speed tier
        base_latencies = {
            1: 500,   # Fast
            2: 1000,  # Medium-fast
            3: 2000,  # Medium
            4: 4000,  # Slow
            5: 8000   # Very slow
        }
        
        base_latency = base_latencies.get(model.speed_tier, 2000)
        
        # Add latency for context length
        context_latency = (context_length / 1000) * 10  # 10ms per 1k tokens
        
        return base_latency + context_latency
    
    def get_all_models(self) -> List[ModelInfo]:
        """Get list of all available models"""
        available = []
        for model_info in self.model_database.values():
            if any(c.provider_type == model_info.provider for c in self.provider_configs):
                available.append(model_info)
        return available
    
    def get_models_by_task(self, task_type: TaskType) -> List[ModelInfo]:
        """Get models suitable for specific task type"""
        return [
            model for model in self.model_database.values()
            if task_type in model.strengths
        ]
