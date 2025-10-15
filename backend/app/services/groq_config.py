"""
Simplified Groq Configuration
Single API key, automatic model selection for all use cases
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import os
import logging

from .groq_provider import GroqProvider, GroqModelSelector
from .model_selector import TaskType

logger = logging.getLogger(__name__)


class ModelPreference(Enum):
    """User preferences for model selection"""
    AUTO = "auto"  # Automatically select best model
    SPEED = "speed"  # Prefer faster models
    QUALITY = "quality"  # Prefer higher quality models
    BALANCED = "balanced"  # Balance speed and quality


@dataclass
class GroqConfig:
    """
    Simplified Groq configuration
    
    Only requires API key, handles everything else automatically
    """
    api_key: str
    model_preference: ModelPreference = ModelPreference.AUTO
    enable_streaming: bool = True
    default_temperature: float = 0.7
    default_max_tokens: int = 2000
    
    @classmethod
    def from_env(cls) -> 'GroqConfig':
        """
        Create configuration from environment variables
        
        Environment variables:
        - GROQ_API_KEY: Groq API key (required)
        - GROQ_MODEL_PREFERENCE: auto|speed|quality|balanced (default: auto)
        - GROQ_ENABLE_STREAMING: true|false (default: true)
        
        Returns:
            GroqConfig instance
        """
        api_key = os.getenv("GROQ_API_KEY", "")
        
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is required. "
                "Get your API key from https://console.groq.com/keys"
            )
        
        model_pref_str = os.getenv("GROQ_MODEL_PREFERENCE", "auto").lower()
        try:
            model_preference = ModelPreference(model_pref_str)
        except ValueError:
            logger.warning(f"Invalid model preference '{model_pref_str}', using AUTO")
            model_preference = ModelPreference.AUTO
        
        enable_streaming = os.getenv("GROQ_ENABLE_STREAMING", "true").lower() == "true"
        
        return cls(
            api_key=api_key,
            model_preference=model_preference,
            enable_streaming=enable_streaming
        )
    
    @classmethod
    def from_api_key(cls, api_key: str, **kwargs) -> 'GroqConfig':
        """
        Create configuration from API key
        
        Args:
            api_key: Groq API key
            **kwargs: Additional configuration options
            
        Returns:
            GroqConfig instance
        """
        return cls(api_key=api_key, **kwargs)
    
    def validate(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if not self.api_key or len(self.api_key) < 10:
            raise ValueError(
                "Invalid Groq API key. Get your key from https://console.groq.com/keys"
            )
        
        if not 0 <= self.default_temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        
        if self.default_max_tokens < 1 or self.default_max_tokens > 8000:
            raise ValueError("max_tokens must be between 1 and 8000")
        
        return True


class GroqManager:
    """
    Simplified Groq Manager
    
    Single API key, automatic model selection based on task
    
    Usage:
        # Initialize with API key
        manager = GroqManager(api_key="your-groq-api-key")
        
        # Generate completion (auto-selects best model)
        response = await manager.generate(
            messages=[{"role": "user", "content": "Explain quantum computing"}],
            task_type="reasoning"  # or use TaskType enum
        )
        
        # Override model selection
        response = await manager.generate(
            messages=[...],
            model="llama-3.1-8b-instant"  # Force specific model
        )
        
        # Stream response
        async for chunk in manager.generate_stream(messages=[...]):
            print(chunk, end="", flush=True)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[GroqConfig] = None,
        **kwargs
    ):
        """
        Initialize Groq Manager
        
        Args:
            api_key: Groq API key (or use config)
            config: GroqConfig instance (or create from api_key)
            **kwargs: Additional config options if using api_key
        """
        if config:
            self.config = config
        elif api_key:
            self.config = GroqConfig.from_api_key(api_key, **kwargs)
        else:
            # Try to load from environment
            self.config = GroqConfig.from_env()
        
        # Validate configuration
        self.config.validate()
        
        # Initialize provider with auto-selection enabled
        self.provider = GroqProvider(
            api_key=self.config.api_key,
            auto_select_model=True
        )
        
        logger.info(
            f"GroqManager initialized with {self.config.model_preference.value} preference"
        )
    
    async def generate(
        self,
        messages: list,
        task_type: Optional[str | TaskType] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion with automatic model selection
        
        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            task_type: Type of task (auto-selects model) - can be string or TaskType enum
            model: Override model selection (optional)
            temperature: Sampling temperature (default from config)
            max_tokens: Max tokens to generate (default from config)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with:
                - content: Generated text
                - model: Model used
                - tokens: Tokens used (estimate)
                - task_type: Task type used
        """
        # Convert string task_type to enum
        if isinstance(task_type, str):
            try:
                task_type = TaskType(task_type.lower())
            except ValueError:
                logger.warning(f"Unknown task type '{task_type}', using GENERAL")
                task_type = TaskType.GENERAL
        elif task_type is None:
            task_type = TaskType.GENERAL
        
        # Use config defaults if not specified
        temperature = temperature if temperature is not None else self.config.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.config.default_max_tokens
        
        # Apply model preference
        prefer_speed = self.config.model_preference == ModelPreference.SPEED
        prefer_quality = self.config.model_preference == ModelPreference.QUALITY
        
        # Select model if not specified
        if not model:
            context_length = sum(len(m.get("content", "")) for m in messages) // 4
            model = GroqModelSelector.select_best_model(
                task_type=task_type,
                context_length=context_length,
                prefer_speed=prefer_speed,
                prefer_quality=prefer_quality
            )
        
        # Generate completion
        try:
            content = await self.provider.generate_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                task_type=task_type,
                model_override=model
            )
            
            # Estimate tokens (rough approximation)
            total_chars = sum(len(m.get("content", "")) for m in messages) + len(content)
            estimated_tokens = total_chars // 4
            
            return {
                "content": content,
                "model": model,
                "tokens": estimated_tokens,
                "task_type": task_type.value,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                "content": "",
                "model": model,
                "tokens": 0,
                "task_type": task_type.value if task_type else "unknown",
                "success": False,
                "error": str(e)
            }
    
    async def generate_stream(
        self,
        messages: list,
        task_type: Optional[str | TaskType] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Generate streaming completion with automatic model selection
        
        Args:
            messages: List of message dicts
            task_type: Type of task (auto-selects model)
            model: Override model selection (optional)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            **kwargs: Additional parameters
            
        Yields:
            Content chunks as they arrive
        """
        if not self.config.enable_streaming:
            # Fall back to non-streaming
            result = await self.generate(
                messages=messages,
                task_type=task_type,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            yield result["content"]
            return
        
        # Convert string task_type to enum
        if isinstance(task_type, str):
            try:
                task_type = TaskType(task_type.lower())
            except ValueError:
                task_type = TaskType.GENERAL
        elif task_type is None:
            task_type = TaskType.GENERAL
        
        # Use config defaults
        temperature = temperature if temperature is not None else self.config.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.config.default_max_tokens
        
        # Select model
        if not model:
            context_length = sum(len(m.get("content", "")) for m in messages) // 4
            model = GroqModelSelector.select_best_model(
                task_type=task_type,
                context_length=context_length
            )
        
        # Stream completion
        try:
            async for chunk in self.provider.generate_streaming_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                task_type=task_type,
                model_override=model
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield f"\n\n[Error: {str(e)}]"
    
    def get_available_models(self) -> list:
        """Get list of available Groq models"""
        return self.provider.get_available_models()
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a model
        
        Args:
            model_name: Model name (or all models if None)
            
        Returns:
            Model information dictionary
        """
        if model_name:
            return self.provider.get_model_info(model_name)
        else:
            return GroqModelSelector.get_all_models()
    
    def recommend_model(self, task_type: str | TaskType) -> Dict[str, Any]:
        """
        Get model recommendation for a task type
        
        Args:
            task_type: Type of task (string or TaskType enum)
            
        Returns:
            Dictionary with:
                - recommended_model: Model name
                - model_info: Model information
                - reasoning: Why this model was selected
        """
        # Convert string to TaskType
        if isinstance(task_type, str):
            try:
                task_type = TaskType(task_type.lower())
            except ValueError:
                task_type = TaskType.GENERAL
        
        # Select model
        model = GroqModelSelector.select_best_model(task_type=task_type)
        model_info = GroqModelSelector.get_model_info(model)
        
        if not model_info:
            model_info = {"description": "Unknown model"}
        
        return {
            "recommended_model": model,
            "model_info": model_info,
            "reasoning": f"Selected {model} because it's {model_info['description']}",
            "task_type": task_type.value
        }


# Convenience function for quick setup
def create_groq_manager(api_key: Optional[str] = None) -> GroqManager:
    """
    Quick setup function
    
    Args:
        api_key: Groq API key (or uses GROQ_API_KEY env var)
        
    Returns:
        Configured GroqManager
        
    Example:
        manager = create_groq_manager("your-api-key")
        response = await manager.generate(
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    return GroqManager(api_key=api_key)
