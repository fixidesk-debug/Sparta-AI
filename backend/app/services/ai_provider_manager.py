"""
AI Provider Manager - Central coordination for multiple AI providers
Handles model selection, load balancing, failover, and monitoring
"""
from typing import Optional, Dict, Any, List, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
import asyncio
import logging
import json
import hashlib
import os
import hmac
import secrets
from collections import defaultdict, deque

# Process-level secret for cache HMAC key; override via environment variable CACHE_KEY_SECRET
_CACHE_KEY_SECRET = os.environ.get("CACHE_KEY_SECRET")
if _CACHE_KEY_SECRET is None:
    # generate a per-process random secret if not provided (avoids predictable keys)
    _CACHE_KEY_SECRET = secrets.token_bytes(32)
elif isinstance(_CACHE_KEY_SECRET, str):
    _CACHE_KEY_SECRET = _CACHE_KEY_SECRET.encode()

from .model_selector import ModelSelector, TaskType
from .request_router import RequestRouter
from .response_evaluator import ResponseEvaluator
from .cost_tracker import CostTracker
from .rate_limiter import RateLimiter, RateLimitConfig
from .context_manager import ContextManager
from .health_monitor import HealthMonitor
from .ai_providers import AIProviderBase, OpenAIProvider, AnthropicProvider


logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported AI provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    LLAMACPP = "llamacpp"
    CUSTOM = "custom"


@dataclass
class ProviderConfig:
    """Configuration for a single AI provider"""
    provider_type: ProviderType
    api_key: Optional[str]
    models: List[str]
    base_url: Optional[str] = None
    priority: int = 1
    enabled: bool = True
    max_concurrent_requests: int = 10
    timeout_seconds: int = 60
    retry_attempts: int = 3
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
    def get_cache_key(self) -> str:
        """Generate cache key for request"""
        content = json.dumps({
            "messages": self.messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "task_type": self.task_type.value
        }, sort_keys=True)
        # Use a keyed HMAC to generate cache keys (not for password hashing)
        # This avoids use of a bare hash in contexts where a secret is expected.
        return hmac.new(_CACHE_KEY_SECRET, content.encode(), hashlib.sha256).hexdigest()
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_cache_key(self) -> str:
        """Generate cache key for request"""
        content = json.dumps({
            "messages": self.messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "task_type": self.task_type.value
        }, sort_keys=True)
        # Use a keyed HMAC (with SHA-256) for cache keys to avoid use of a bare hash.
        # This is not for password hashing; it prevents predictable cache keys.
        return hmac.new(_CACHE_KEY_SECRET, content.encode(), hashlib.sha256).hexdigest()


@dataclass
class AIResponse:
    """Response from AI provider"""
    content: str
    provider: ProviderType
    model: str
    tokens_used: int
    cost: float
    latency_ms: float
    quality_score: float
    cached: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIProviderManager:
    """
    Central AI provider management system
    
    Features:
    - Automatic model selection based on task
    - Load balancing across providers
    - Fallback chains for reliability
    - Cost optimization
    - Response quality scoring
    - Rate limit handling
    - Context length management
    - Health monitoring
    """
    
    def __init__(
        self,
        providers: List[ProviderConfig],
        enable_caching: bool = True,
        enable_cost_optimization: bool = True,
        enable_quality_scoring: bool = True
    ):
        """
        Initialize AI Provider Manager
        
        Args:
            providers: List of provider configurations
            enable_caching: Enable response caching
            enable_cost_optimization: Enable cost-based model selection
            enable_quality_scoring: Enable response quality evaluation
        """
        self.providers = {p.provider_type: p for p in providers if p.enabled}
        self.provider_instances: Dict[ProviderType, AIProviderBase] = {}
        
        # Initialize components
        self.model_selector = ModelSelector(providers)
        self.request_router = RequestRouter(providers)
        self.response_evaluator = ResponseEvaluator() if enable_quality_scoring else None
        self.cost_tracker = CostTracker(providers) if enable_cost_optimization else None
        self.context_manager = ContextManager()
        self.health_monitor = HealthMonitor(providers)
        
        # Rate limiters per provider
        self.rate_limiters: Dict[ProviderType, RateLimiter] = {}
        for provider_type, config in self.providers.items():
            self.rate_limiters[provider_type] = RateLimiter(
                RateLimitConfig(
                    max_requests_per_minute=config.max_concurrent_requests * 6,
                    max_requests_per_hour=config.max_concurrent_requests * 60,
                    max_concurrent_requests=config.max_concurrent_requests
                )
            )
        
        # Response cache
        self.enable_caching = enable_caching
        self.cache: Dict[str, Tuple[AIResponse, datetime]] = {}
        self.cache_ttl = timedelta(hours=1)
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cached_responses": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "average_latency_ms": 0.0,
            "provider_usage": defaultdict(int),
            "model_usage": defaultdict(int)
        }
        
        # Request queue for rate limiting
        self.request_queues: Dict[ProviderType, deque] = defaultdict(deque)
        
        logger.info(f"AIProviderManager initialized with {len(self.providers)} providers")
    
    async def initialize(self):
        """Initialize all provider connections"""
        for provider_type, config in self.providers.items():
            try:
                instance = await self._create_provider_instance(provider_type, config)
                self.provider_instances[provider_type] = instance
                logger.info(f"Initialized {provider_type.value} provider")
            except Exception as e:
                logger.error(f"Failed to initialize {provider_type.value}: {e}")
        
        # Start health monitoring
        await self.health_monitor.start_monitoring(self.provider_instances)
    
    async def _create_provider_instance(
        self,
        provider_type: ProviderType,
        config: ProviderConfig
    ) -> AIProviderBase:
        """Create provider instance based on type.

        Security: ensure that providers which require API keys are only created when
        a non-empty, non-whitespace API key is provided to avoid accidentally
        creating a functioning provider with an empty credential (which could
        allow bypass of intended access restrictions).
        """
        # Providers that require an API key to operate
        providers_requiring_key = {
            ProviderType.OPENAI,
            ProviderType.ANTHROPIC,
            ProviderType.GOOGLE
        }

        if provider_type in providers_requiring_key:
            if not config.api_key or not isinstance(config.api_key, str) or not config.api_key.strip():
                # Explicitly fail instead of falling back to an empty string API key.
                raise PermissionError(f"API key required for provider {provider_type.value}")

        if provider_type == ProviderType.OPENAI:
            return OpenAIProvider(
                api_key=config.api_key,
                model=config.models[0] if config.models else "gpt-4"
            )
        elif provider_type == ProviderType.ANTHROPIC:
            return AnthropicProvider(
                api_key=config.api_key,
                model=config.models[0] if config.models else "claude-3-5-sonnet-20240620"
            )
        # Add other providers as needed; for providers that don't require keys, allow creation
        elif provider_type == ProviderType.CUSTOM:
            # Expect a factory callable in metadata to construct custom providers
            factory = config.metadata.get("factory") if config.metadata else None
            if callable(factory):
                return factory(config)
            raise ValueError("Custom provider requires a callable 'factory' in ProviderConfig.metadata")
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
    
    async def generate(self, request: AIRequest) -> AIResponse:
        """
        Generate AI response with automatic provider selection and failover
        
        Args:
            request: AI request with messages and parameters
            
        Returns:
            AI response with content and metadata
            
        Raises:
            Exception: If all providers fail
        """
        self.metrics["total_requests"] += 1
        start_time = datetime.now(timezone.utc)
        
        # Check cache
        if self.enable_caching and not request.stream:
            cached_response = self._get_cached_response(request)
            if cached_response:
                self.metrics["cached_responses"] += 1
                logger.info("Returning cached response for request")
                return cached_response
        
        try:
            # Optimize context window
            optimized_messages = await self.context_manager.optimize_messages(
                request.messages,
                request.max_tokens
            )
            request.messages = optimized_messages
            
            # Select best model for task
            selected_model, provider_type = await self._select_model(request)
            
            # Route request with fallback chain
            response = await self._route_request_with_fallback(
                request,
                provider_type,
                selected_model
            )
            
            # Calculate metrics
            latency_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            response.latency_ms = latency_ms
            
            # Evaluate response quality
            if self.response_evaluator and not request.stream:
                quality = await self.response_evaluator.evaluate(
                    request.messages,
                    response.content,
                    request.task_type
                )
                response.quality_score = quality.overall_score
            
            # Track cost
            if self.cost_tracker:
                cost = self.cost_tracker.calculate_cost(
                    provider_type,
                    selected_model,
                    response.tokens_used
                )
                response.cost = cost
                self.metrics["total_cost"] += cost
            
            # Update metrics
            self._update_metrics(response, latency_ms)
            
            # Cache response
            if self.enable_caching and not request.stream:
                self._cache_response(request, response)
            
            self.metrics["successful_requests"] += 1
            return response
            
        except Exception as e:
            self.metrics["failed_requests"] += 1
            logger.error(f"AI generation failed: {e}")
            raise Exception(f"All AI providers failed: {str(e)}")
    
    async def generate_stream(
        self,
        request: AIRequest
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming AI response
        
        Args:
            request: AI request (stream=True)
            
        Yields:
            Content chunks as they arrive
        """
        request.stream = True
        self.metrics["total_requests"] += 1
        
        # Select model
        selected_model, provider_type = await self._select_model(request)
        
        # Get provider instance
        provider = self.provider_instances.get(provider_type)
        if not provider:
            raise Exception(f"Provider {provider_type.value} not available")
        
        # Check rate limit
        await self.rate_limiters[provider_type].acquire()
        
        try:
            # Stream response
            try:
                stream_result = await provider.generate_streaming_completion(
                    messages=request.messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
                
                # Check if stream is valid and is an async generator
                if stream_result is not None and hasattr(stream_result, '__aiter__'):
                    async for chunk in stream_result:  # type: ignore
                        yield chunk
                else:
                    logger.warning("Provider did not return an async iterable for streaming")
                
            except AttributeError as e:
                logger.error(f"Provider does not support streaming: {e}")
            
            self.metrics["successful_requests"] += 1
            
        except Exception as e:
            self.metrics["failed_requests"] += 1
            logger.error(f"Streaming generation failed: {e}")
            raise
        finally:
            self.rate_limiters[provider_type].release()
    
    async def _select_model(
        self,
        request: AIRequest
    ) -> Tuple[str, ProviderType]:
        """Select best model and provider for request"""
        
        # Use preference if specified and available
        if request.provider_preference:
            if request.provider_preference in self.provider_instances:
                provider_type = request.provider_preference
                config = self.providers[provider_type]
                model = request.model_preference or config.models[0]
                return model, provider_type
        
        # Use model selector for automatic selection
        selected = await self.model_selector.select_model(
            task_type=request.task_type,
            context_length=self.context_manager.estimate_tokens(request.messages),
            optimize_for_cost=self.cost_tracker is not None
        )
        
        return selected.model_name, selected.provider
    
    async def _route_request_with_fallback(
        self,
        request: AIRequest,
        provider_type: ProviderType,
        model: str
    ) -> AIResponse:
        """Route request with automatic fallback chain"""
        
        # Get fallback chain
        fallback_chain = await self.request_router.get_fallback_chain(
            provider_type,
            request.task_type
        )
        
        last_error = None
        
        # Ensure fallback_chain is iterable
        if not fallback_chain:
            fallback_chain = [(provider_type, model)]
        
        for fallback_provider, fallback_model in fallback_chain:
            try:
                # Check provider health
                health = await self.health_monitor.get_provider_health(fallback_provider)
                if health.status == "down":
                    logger.warning(f"Skipping {fallback_provider.value} - provider is down")
                    continue
                
                # Get provider instance
                provider = self.provider_instances.get(fallback_provider)
                if not provider:
                    continue
                
                # Check rate limit
                rate_limiter = self.rate_limiters[fallback_provider]
                await rate_limiter.acquire()
                
                try:
                    # Generate response
                    content = await self._generate_with_retry(
                        provider,
                        request,
                        fallback_model
                    )
                    
                    # Create response
                    response = AIResponse(
                        content=content,
                        provider=fallback_provider,
                        model=fallback_model,
                        tokens_used=self.context_manager.estimate_tokens(
                            request.messages + [{"role": "assistant", "content": content}]
                        ),
                        cost=0.0,
                        latency_ms=0.0,
                        quality_score=0.0
                    )
                    
                    # Update health
                    await self.health_monitor.record_success(fallback_provider)
                    
                    return response
                    
                finally:
                    rate_limiter.release()
                    
            except Exception as e:
                last_error = e
                logger.error(f"Provider {fallback_provider.value} failed: {e}")
                await self.health_monitor.record_failure(fallback_provider, str(e))
                continue
        
        # All providers failed
        raise Exception(f"All providers in fallback chain failed. Last error: {last_error}")
    
    async def _generate_with_retry(
        self,
        provider: AIProviderBase,
        request: AIRequest,
        model: str
    ) -> str:
        """Generate response with exponential backoff retry"""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                # Update provider model
                provider.model = model
                
                # Generate
                content = await provider.generate_completion(
                    messages=request.messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
                
                return content
                
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    raise
        
        raise Exception("Max retries exceeded")
    
    def _get_cached_response(self, request: AIRequest) -> Optional[AIResponse]:
        """Get cached response if available and not expired"""
        cache_key = request.get_cache_key()
        
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]
            if datetime.now(timezone.utc) - timestamp < self.cache_ttl:
                response.cached = True
                return response
            else:
                # Remove expired entry
                del self.cache[cache_key]
        
        return None
    
    def _cache_response(self, request: AIRequest, response: AIResponse):
        """Cache response for future use"""
        cache_key = request.get_cache_key()
        self.cache[cache_key] = (response, datetime.now(timezone.utc))
        
        # Clean old cache entries periodically
        if len(self.cache) > 1000:
            self._clean_cache()
    
    def _clean_cache(self):
        """Remove expired cache entries"""
        now = datetime.now(timezone.utc)
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if now - timestamp >= self.cache_ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        
        logger.info(f"Cleaned {len(expired_keys)} expired cache entries")
    
    def _update_metrics(self, response: AIResponse, latency_ms: float):
        """Update internal metrics"""
        self.metrics["total_tokens"] += response.tokens_used
        self.metrics["provider_usage"][response.provider.value] += 1
        self.metrics["model_usage"][response.model] += 1
        
        # Update average latency
        total_requests = self.metrics["successful_requests"]
        current_avg = self.metrics["average_latency_ms"]
        self.metrics["average_latency_ms"] = (
            (current_avg * (total_requests - 1) + latency_ms) / total_requests
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        health_status = await self.health_monitor.get_all_health_status()
        
        return {
            **self.metrics,
            "cache_size": len(self.cache),
            "provider_health": {
                provider.value: health.to_dict()
                for provider, health in health_status.items()
            },
            "cost_breakdown": self.cost_tracker.get_cost_breakdown() if self.cost_tracker else {},
            "active_providers": len(self.provider_instances)
        }
    
    async def compare_providers(
        self,
        request: AIRequest,
        providers: Optional[List[ProviderType]] = None
    ) -> Dict[ProviderType, AIResponse]:
        """
        Compare multiple providers on same request
        
        Args:
            request: Request to send to all providers
            providers: Specific providers to compare (or all if None)
            
        Returns:
            Dictionary mapping provider to response
        """
        if providers is None:
            providers = list(self.provider_instances.keys())
        
        results = {}
        
        # Generate responses concurrently
        tasks = []
        for provider_type in providers:
            if provider_type in self.provider_instances:
                # Create request copy with provider preference
                provider_request = AIRequest(
                    messages=request.messages.copy(),
                    task_type=request.task_type,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    provider_preference=provider_type
                )
                tasks.append(self.generate(provider_request))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map responses to providers
        for provider_type, response in zip(providers, responses):
            if isinstance(response, Exception):
                logger.error(f"Provider {provider_type.value} failed: {response}")
            else:
                results[provider_type] = response
        
        return results
    
    async def shutdown(self):
        """Gracefully shutdown manager"""
        logger.info("Shutting down AI Provider Manager")
        
        # Stop health monitoring
        await self.health_monitor.stop_monitoring()
        
        # Clear cache
        self.cache.clear()
        
        # Log final metrics
        logger.info(f"Final metrics: {json.dumps(self.metrics, indent=2)}")


# Example usage and configuration
async def create_provider_manager(
    openai_key: Optional[str] = None,
    anthropic_key: Optional[str] = None,
    google_key: Optional[str] = None
) -> AIProviderManager:
    """
    Create configured provider manager
    
    Args:
        openai_key: OpenAI API key
        anthropic_key: Anthropic API key
        google_key: Google API key
        
    Returns:
        Configured AIProviderManager
    """
    providers = []
    
    # OpenAI configuration
    if openai_key:
        providers.append(ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key=openai_key,
            models=["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"],
            priority=1,
            max_concurrent_requests=10,
            cost_per_1k_input_tokens=0.03,
            cost_per_1k_output_tokens=0.06
        ))
    
    # Anthropic configuration
    if anthropic_key:
        providers.append(ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            api_key=anthropic_key,
            models=["claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"],
            priority=1,
            max_concurrent_requests=5,
            cost_per_1k_input_tokens=0.003,
            cost_per_1k_output_tokens=0.015
        ))
    
    manager = AIProviderManager(
        providers=providers,
        enable_caching=True,
        enable_cost_optimization=True,
        enable_quality_scoring=True
    )
    
    await manager.initialize()
    
    return manager
