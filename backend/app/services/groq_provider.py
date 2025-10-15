"""
Groq AI Provider with Intelligent Model Selection
Automatically selects the best Groq model based on task complexity
"""
from typing import List, Dict, Optional, AsyncGenerator
import logging
from groq import AsyncGroq
from groq.types.chat import ChatCompletionMessageParam
from .ai_providers import AIProviderBase
from .model_selector import TaskType

logger = logging.getLogger(__name__)


class GroqModelSelector:
    """
    Intelligent Groq model selection based on task requirements
    
    Groq Models Available (as of 2025):
    - llama-3.3-70b-versatile: Best overall, great for complex reasoning
    - llama-3.1-8b-instant: Fast, good for simple tasks
    - mixtral-8x7b-32768: Excellent for code generation, 32k context
    - gemma2-9b-it: Fast and efficient for general tasks
    - llama-3.2-90b-vision-preview: Vision capabilities (if needed)
    """
    
    # Model configurations with their strengths
    MODELS = {
        # Best for complex reasoning, analysis, expert-level tasks
        "llama-3.3-70b-versatile": {
            "capability": "expert",
            "context": 8192,
            "speed": "medium",
            "cost": "high",
            "best_for": [
                TaskType.REASONING,
                TaskType.DATA_ANALYSIS,
                TaskType.CODE_REVIEW,
                TaskType.MATH
            ],
            "description": "70B parameter model, best for complex reasoning and analysis"
        },
        
        # Best for code generation and technical tasks
        "mixtral-8x7b-32768": {
            "capability": "advanced",
            "context": 32768,
            "speed": "medium",
            "cost": "medium",
            "best_for": [
                TaskType.CODE_GENERATION,
                TaskType.CODE_REVIEW
            ],
            "description": "Mixtral model with 32k context, excellent for code"
        },
        
        # Fast model for simple tasks
        "llama-3.1-8b-instant": {
            "capability": "standard",
            "context": 8192,
            "speed": "fast",
            "cost": "low",
            "best_for": [
                TaskType.CONVERSATION,
                TaskType.QUESTION_ANSWERING,
                TaskType.SUMMARIZATION,
                TaskType.GENERAL
            ],
            "description": "8B instant model, fast for simple tasks"
        },
        
        # Balanced model for general use
        "gemma2-9b-it": {
            "capability": "standard",
            "context": 8192,
            "speed": "fast",
            "cost": "low",
            "best_for": [
                TaskType.CONVERSATION,
                TaskType.TRANSLATION,
                TaskType.SUMMARIZATION,
                TaskType.GENERAL
            ],
            "description": "Gemma 9B model, fast and efficient"
        }
    }
    
    # Task complexity scores (1-5, higher = more complex)
    TASK_COMPLEXITY = {
        TaskType.CONVERSATION: 1,
        TaskType.SUMMARIZATION: 2,
        TaskType.QUESTION_ANSWERING: 2,
        TaskType.TRANSLATION: 2,
        TaskType.GENERAL: 2,
        TaskType.CREATIVE_WRITING: 3,
        TaskType.DATA_ANALYSIS: 4,
        TaskType.CODE_REVIEW: 4,
        TaskType.CODE_GENERATION: 4,
        TaskType.REASONING: 5,
        TaskType.MATH: 5
    }
    
    @classmethod
    def select_best_model(
        cls,
        task_type: TaskType,
        context_length: int = 0,
        prefer_speed: bool = False,
        prefer_quality: bool = False,
        user_preference: Optional[str] = None
    ) -> str:
        """
        Select the best Groq model for the given task
        
        Args:
            task_type: Type of task to perform
            context_length: Required context window size
            prefer_speed: Prioritize faster models
            prefer_quality: Prioritize quality over speed
            user_preference: User's preferred model (overrides selection)
            
        Returns:
            Selected model name
        """
        # User preference overrides everything
        if user_preference and user_preference in cls.MODELS:
            logger.info(f"Using user-specified model: {user_preference}")
            return user_preference
        
        # Get task complexity
        complexity = cls.TASK_COMPLEXITY.get(task_type, 3)
        
        # Filter models by context length requirement
        available_models = {
            name: info for name, info in cls.MODELS.items()
            if info["context"] >= context_length
        }
        
        if not available_models:
            logger.warning(f"No models support context length {context_length}, using best available")
            available_models = cls.MODELS
        
        # Score each model
        scored_models = []
        for model_name, model_info in available_models.items():
            score = 0
            
            # Task match bonus
            if task_type in model_info["best_for"]:
                score += 10
            
            # Complexity match
            if complexity >= 4 and model_info["capability"] in ["advanced", "expert"]:
                score += 5
            elif complexity <= 2 and model_info["capability"] == "standard":
                score += 5
            
            # Speed preference
            if prefer_speed and model_info["speed"] == "fast":
                score += 3
            
            # Quality preference
            if prefer_quality and model_info["capability"] == "expert":
                score += 3
            
            # Context window bonus (larger is better for complex tasks)
            if complexity >= 3:
                score += model_info["context"] / 10000
            
            scored_models.append((score, model_name, model_info))
        
        # Sort by score (descending)
        scored_models.sort(reverse=True, key=lambda x: x[0])
        
        # Select best model
        best_score, best_model, best_info = scored_models[0]
        
        logger.info(
            f"Selected {best_model} for {task_type.value} "
            f"(score: {best_score:.1f}, {best_info['description']})"
        )
        
        return best_model
    
    @classmethod
    def get_all_models(cls) -> Dict[str, Dict]:
        """Get information about all available models"""
        return cls.MODELS.copy()
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Optional[Dict]:
        """Get information about a specific model"""
        return cls.MODELS.get(model_name)


class GroqProvider(AIProviderBase):
    """
    Groq AI Provider with automatic model selection
    
    Features:
    - Automatic model selection based on task type
    - Support for all Groq models
    - Streaming support
    - Fast inference speeds
    """
    
    def __init__(
        self,
        api_key: str,
        default_model: str = "llama-3.3-70b-versatile",
        auto_select_model: bool = True
    ):
        """
        Initialize Groq provider
        
        Args:
            api_key: Groq API key
            default_model: Default model to use
            auto_select_model: Enable automatic model selection
        """
        super().__init__(api_key, default_model)
        self.client = AsyncGroq(api_key=api_key)
        self.auto_select_model = auto_select_model
        self.model_selector = GroqModelSelector()
        
        logger.info(f"GroqProvider initialized with auto_select={auto_select_model}")
    
    def select_model_for_task(
        self,
        task_type: TaskType,
        context_length: int = 0,
        user_preference: Optional[str] = None
    ) -> str:
        """
        Select best model for the given task
        
        Args:
            task_type: Type of task
            context_length: Required context length
            user_preference: User's model preference
            
        Returns:
            Selected model name
        """
        if not self.auto_select_model:
            return user_preference or self.model
        
        return self.model_selector.select_best_model(
            task_type=task_type,
            context_length=context_length,
            user_preference=user_preference
        )
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        task_type: Optional[TaskType] = None,
        model_override: Optional[str] = None
    ) -> str:
        """
        Generate completion with automatic model selection
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            task_type: Type of task (for model selection)
            model_override: Override automatic model selection
            
        Returns:
            Generated text
        """
        try:
            # Select model
            if self.auto_select_model and task_type:
                context_length = sum(len(m.get("content", "")) for m in messages)
                selected_model = self.select_model_for_task(
                    task_type=task_type,
                    context_length=context_length // 4,  # Rough token estimate
                    user_preference=model_override
                )
            else:
                selected_model = model_override or self.model
            
            # Convert messages to proper type for Groq API
            typed_messages: List[ChatCompletionMessageParam] = messages  # type: ignore
            
            # Generate completion
            response = await self.client.chat.completions.create(
                model=selected_model,
                messages=typed_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            
            # Log with token usage if available
            if response.usage:
                logger.info(
                    f"Generated completion using {selected_model} "
                    f"({response.usage.total_tokens} tokens)"
                )
            else:
                logger.info(f"Generated completion using {selected_model}")
            
            return content or ""
            
        except Exception as e:
            logger.error(f"Groq completion failed: {e}")
            raise Exception(f"Groq API error: {str(e)}")
    
    async def generate_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        task_type: Optional[TaskType] = None,
        model_override: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming completion with automatic model selection
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            task_type: Type of task (for model selection)
            model_override: Override automatic model selection
            
        Yields:
            Generated text chunks
        """
        try:
            # Select model
            if self.auto_select_model and task_type:
                context_length = sum(len(m.get("content", "")) for m in messages)
                selected_model = self.select_model_for_task(
                    task_type=task_type,
                    context_length=context_length // 4,
                    user_preference=model_override
                )
            else:
                selected_model = model_override or self.model
            
            logger.info(f"Starting stream with {selected_model}")
            
            # Convert messages to proper type for Groq API
            typed_messages: List[ChatCompletionMessageParam] = messages  # type: ignore
            
            # Generate streaming completion
            stream = await self.client.chat.completions.create(
                model=selected_model,
                messages=typed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Groq streaming failed: {e}")
            raise Exception(f"Groq streaming error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available Groq models"""
        return list(GroqModelSelector.MODELS.keys())
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict:
        """
        Get information about a model
        
        Args:
            model_name: Model name (or current model if None)
            
        Returns:
            Model information dictionary
        """
        model = model_name or self.model
        info = GroqModelSelector.get_model_info(model)
        
        if info:
            return {
                "name": model,
                **info
            }
        else:
            return {
                "name": model,
                "error": "Model not found in database"
            }
