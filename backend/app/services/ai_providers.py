"""
AI Provider Abstraction Layer
Supports multiple AI providers (OpenAI, Anthropic, Groq, etc.)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, AsyncGenerator
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers"""
    GROQ = "groq"


class AIProviderBase(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, api_key: str, model: str):
        """
        Initialize AI provider
        
        Args:
            api_key: API key for the provider
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate completion from messages
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated completion text
        """
        pass
    
    @abstractmethod
    async def generate_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming completion from messages
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Completion chunks as they arrive
        """
        pass





class AIProviderFactory:
    """Factory for creating AI provider instances"""
    
    @staticmethod
    def create_provider(
        provider: AIProvider,
        api_key: str,
        model: Optional[str] = None
    ) -> AIProviderBase:
        from .groq_provider import GroqProvider
        
        if provider != AIProvider.GROQ:
            raise ValueError(f"Only Groq provider supported")
        
        model = model or "llama-3.3-70b-versatile"
        logger.info(f"Creating Groq provider with model {model}")
        return GroqProvider(api_key, model)
