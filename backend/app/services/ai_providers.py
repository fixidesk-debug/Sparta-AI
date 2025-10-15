"""
AI Provider Abstraction Layer
Supports multiple AI providers (OpenAI, Anthropic, Groq, etc.)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, cast, AsyncGenerator
from enum import Enum
import logging
from openai import AsyncOpenAI
import anthropic

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
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


class OpenAIProvider(AIProviderBase):
    """OpenAI API provider (GPT-4, GPT-3.5, etc.)"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
            model: Model name (e.g., 'gpt-4', 'gpt-3.5-turbo')
        """
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate completion using OpenAI API
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI parameters (top_p, frequency_penalty, etc.)
            
        Returns:
            Generated text
        """
        try:
            self.logger.info(f"Generating OpenAI completion with model {self.model}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=cast(Any, messages),
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            completion = response.choices[0].message.content
            self.logger.info(f"OpenAI completion generated: {len(completion)} chars")
            
            return completion or ""
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise Exception(f"OpenAI generation failed: {str(e)}")
    
    async def generate_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        Generate streaming completion using OpenAI API
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI parameters
            
        Yields:
            Text chunks as they arrive
        """
        try:
            self.logger.info(f"Generating OpenAI streaming completion with model {self.model}")
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=cast(Any, messages),
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"OpenAI streaming error: {e}")
            raise Exception(f"OpenAI streaming failed: {str(e)}")


class AnthropicProvider(AIProviderBase):
    """Anthropic Claude API provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        """
        Initialize Anthropic provider
        
        Args:
            api_key: Anthropic API key
            model: Model name (e.g., 'claude-3-opus-20240229', 'claude-3-sonnet-20240229')
        """
        super().__init__(api_key, model)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate completion using Anthropic API
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Anthropic parameters
            
        Returns:
            Generated text
        """
        try:
            self.logger.info(f"Generating Anthropic completion with model {self.model}")
            
            # Convert messages format if needed
            # Anthropic uses system parameter separately
            system_message = None
            converted_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    converted_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            create_params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": converted_messages,
                **kwargs
            }
            if system_message is not None:
                create_params["system"] = system_message
            
            response = await self.client.messages.create(**create_params)
            
            completion = response.content[0].text
            self.logger.info(f"Anthropic completion generated: {len(completion)} chars")
            
            return completion
            
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            raise Exception(f"Anthropic generation failed: {str(e)}")
    
    async def generate_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        Generate streaming completion using Anthropic API
        
        Args:
            messages: Conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Anthropic parameters
            
        Yields:
            Text chunks as they arrive
        """
        try:
            self.logger.info(f"Generating Anthropic streaming completion with model {self.model}")
            
            # Convert messages format
            system_message = None
            converted_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    converted_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            stream_params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": converted_messages,
                **kwargs
            }
            if system_message is not None:
                stream_params["system"] = system_message
            
            async with self.client.messages.stream(**stream_params) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            self.logger.error(f"Anthropic streaming error: {e}")
            raise Exception(f"Anthropic streaming failed: {str(e)}")


class AIProviderFactory:
    """Factory for creating AI provider instances"""
    
    @staticmethod
    def create_provider(
        provider: AIProvider,
        api_key: str,
        model: Optional[str] = None
    ) -> AIProviderBase:
        """
        Create an AI provider instance
        
        Args:
            provider: AIProvider enum value
            api_key: API key for the provider
            model: Optional model name (uses default if not provided)
            
        Returns:
            AIProviderBase instance
            
        Raises:
            ValueError: If provider is not supported
        """
        from .groq_provider import GroqProvider
        
        providers = {
            AIProvider.OPENAI: (OpenAIProvider, "gpt-4"),
            AIProvider.ANTHROPIC: (AnthropicProvider, "claude-3-opus-20240229"),
            AIProvider.GROQ: (GroqProvider, "llama-3.3-70b-versatile")
        }
        
        if provider not in providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_class, default_model = providers[provider]
        model = model or default_model
        
        logger.info(f"Creating {provider.value} provider with model {model}")
        return provider_class(api_key, model)
