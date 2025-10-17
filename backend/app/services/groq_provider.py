"""
Groq Provider - Multi-Model AI Provider
"""
from typing import List, Dict, AsyncGenerator, Optional
import logging
from groq import AsyncGroq

logger = logging.getLogger(__name__)


class GroqProvider:
    """Groq AI provider with multiple models"""
    
    MODELS = {
        "llama-3.3-70b": "llama-3.3-70b-versatile",
        "llama-3.1-70b": "llama-3.1-70b-versatile", 
        "llama-3.1-8b": "llama-3.1-8b-instant",
        "mixtral-8x7b": "mixtral-8x7b-32768",
        "gemma-7b": "gemma-7b-it"
    }
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model
        self.client = AsyncGroq(api_key=api_key)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        try:
            self.logger.info(f"Generating completion with {self.model}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            completion = response.choices[0].message.content
            self.logger.info(f"Completion generated: {len(completion)} chars")
            
            return completion or ""
            
        except Exception as e:
            self.logger.error(f"Groq API error: {e}")
            raise Exception(f"Groq generation failed: {str(e)}")
    
    async def generate_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        try:
            self.logger.info(f"Generating streaming completion with {self.model}")
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"Groq streaming error: {e}")
            raise Exception(f"Groq streaming failed: {str(e)}")
