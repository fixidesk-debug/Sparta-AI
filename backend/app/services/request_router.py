"""
Request Router - Load balancing and fallback chain management
Routes requests to optimal providers with automatic failover
"""
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import random
import logging

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Request routing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    RANDOM = "random"
    PRIORITY = "priority"
    COST_OPTIMIZED = "cost_optimized"


@dataclass
class LoadStats:
    """Load statistics for a provider"""
    active_requests: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 1.0
        return (self.total_requests - self.failed_requests) / self.total_requests


class RequestRouter:
    """
    Intelligent request routing system
    
    Features:
    - Multiple routing strategies
    - Load balancing across providers
    - Automatic fallback chains
    - Circuit breaker pattern
    - Adaptive routing based on performance
    """
    
    def __init__(self, provider_configs: List):
        """
        Initialize request router
        
        Args:
            provider_configs: List of ProviderConfig objects
        """
        self.provider_configs = provider_configs
        self.load_stats: Dict[str, LoadStats] = defaultdict(LoadStats)
        
        # Round robin counters
        self.round_robin_counters: Dict[str, int] = defaultdict(int)
        
        # Circuit breaker thresholds
        self.circuit_breaker_threshold = 0.5  # 50% failure rate
        self.circuit_breaker_min_requests = 10
        
        logger.info("RequestRouter initialized")
    
    async def route_request(
        self,
        task_type: 'TaskType',  # type: ignore
        strategy: RoutingStrategy = RoutingStrategy.LEAST_LOADED
    ) -> Tuple['ProviderType', str]:  # type: ignore
        """
        Route request to optimal provider
        
        Args:
            task_type: Type of task
            strategy: Routing strategy to use
            
        Returns:
            Tuple of (provider_type, model_name)
        """
        
        if strategy == RoutingStrategy.ROUND_ROBIN:
            return await self._route_round_robin()
        elif strategy == RoutingStrategy.LEAST_LOADED:
            return await self._route_least_loaded()
        elif strategy == RoutingStrategy.RANDOM:
            return await self._route_random()
        elif strategy == RoutingStrategy.PRIORITY:
            return await self._route_priority()
        elif strategy == RoutingStrategy.COST_OPTIMIZED:
            return await self._route_cost_optimized()
        else:
            return await self._route_least_loaded()
    
    async def _route_round_robin(self) -> Tuple['ProviderType', str]:  # type: ignore
        """Round robin routing across providers"""
        
        # Get available providers sorted by type
        available = [c for c in self.provider_configs if c.enabled]
        if not available:
            raise Exception("No available providers")
        
        # Get counter for this routing
        counter = self.round_robin_counters["global"]
        selected = available[counter % len(available)]
        
        # Increment counter
        self.round_robin_counters["global"] = (counter + 1) % len(available)
        
        return selected.provider_type, selected.models[0]
    
    async def _route_least_loaded(self) -> Tuple['ProviderType', str]:  # type: ignore
        """Route to provider with least active requests"""
        
        available = [c for c in self.provider_configs if c.enabled]
        if not available:
            raise Exception("No available providers")
        
        # Check circuit breakers
        available = [c for c in available if not self._is_circuit_open(c.provider_type)]
        
        if not available:
            # All circuit breakers open - reset and try again
            logger.warning("All circuit breakers open, resetting")
            self.load_stats.clear()
            available = [c for c in self.provider_configs if c.enabled]
        
        # Find least loaded
        min_load = float('inf')
        selected = available[0]
        
        for config in available:
            stats = self.load_stats[config.provider_type.value]
            # Consider both active requests and success rate
            effective_load = stats.active_requests / (stats.success_rate + 0.1)
            
            if effective_load < min_load:
                min_load = effective_load
                selected = config
        
        return selected.provider_type, selected.models[0]
    
    async def _route_random(self) -> Tuple['ProviderType', str]:  # type: ignore
        """Random routing"""
        
        available = [c for c in self.provider_configs if c.enabled]
        if not available:
            raise Exception("No available providers")
        
        selected = random.choice(available)
        return selected.provider_type, selected.models[0]
    
    async def _route_priority(self) -> Tuple['ProviderType', str]:  # type: ignore
        """Route based on provider priority"""
        
        available = [c for c in self.provider_configs if c.enabled]
        if not available:
            raise Exception("No available providers")
        
        # Sort by priority (higher priority first)
        available.sort(key=lambda c: c.priority, reverse=True)
        
        # Check circuit breakers and select first available
        for config in available:
            if not self._is_circuit_open(config.provider_type):
                return config.provider_type, config.models[0]
        
        # All have open circuits - use highest priority anyway
        return available[0].provider_type, available[0].models[0]
    
    async def _route_cost_optimized(self) -> Tuple['ProviderType', str]:  # type: ignore
        """Route to cheapest available provider"""
        
        available = [c for c in self.provider_configs if c.enabled]
        if not available:
            raise Exception("No available providers")
        
        # Sort by cost (cheapest first)
        available.sort(key=lambda c: c.cost_per_1k_input_tokens + c.cost_per_1k_output_tokens)
        
        # Check circuit breakers
        for config in available:
            if not self._is_circuit_open(config.provider_type):
                return config.provider_type, config.models[0]
        
        # All have open circuits - use cheapest anyway
        return available[0].provider_type, available[0].models[0]
    
    async def get_fallback_chain(
        self,
        primary_provider: 'ProviderType',  # type: ignore
        task_type: 'TaskType'  # type: ignore
    ) -> List[Tuple['ProviderType', str]]:  # type: ignore
        """
        Get fallback chain starting with primary provider
        
        Args:
            primary_provider: Primary provider to try first
            task_type: Type of task for fallback selection
            
        Returns:
            Ordered list of (provider, model) tuples to try
        """
        
        chain = []
        
        # Add primary provider
        primary_config = next(
            (c for c in self.provider_configs if c.provider_type == primary_provider),
            None
        )
        if primary_config:
            chain.append((primary_provider, primary_config.models[0]))
        
        # Add other providers sorted by priority and success rate
        other_providers = [
            c for c in self.provider_configs
            if c.provider_type != primary_provider and c.enabled
        ]
        
        # Sort by priority and success rate
        other_providers.sort(
            key=lambda c: (
                -c.priority,  # Higher priority first
                -self.load_stats[c.provider_type.value].success_rate  # Higher success rate
            )
        )
        
        for config in other_providers:
            chain.append((config.provider_type, config.models[0]))
        
        logger.info(
            f"Generated fallback chain: "
            f"{' -> '.join([p.value for p, _ in chain])}"
        )
        
        return chain
    
    def record_request_start(self, provider: 'ProviderType'):  # type: ignore
        """Record request start for load tracking"""
        stats = self.load_stats[provider.value]
        stats.active_requests += 1
        stats.total_requests += 1
    
    def record_request_end(
        self,
        provider: 'ProviderType',  # type: ignore
        success: bool,
        latency_ms: float
    ):
        """Record request completion for load tracking"""
        stats = self.load_stats[provider.value]
        stats.active_requests = max(0, stats.active_requests - 1)
        
        if not success:
            stats.failed_requests += 1
        
        # Update average latency (exponential moving average)
        alpha = 0.1
        stats.average_latency_ms = (
            alpha * latency_ms + (1 - alpha) * stats.average_latency_ms
        )
    
    def _is_circuit_open(self, provider: 'ProviderType') -> bool:  # type: ignore
        """Check if circuit breaker is open for provider"""
        stats = self.load_stats[provider.value]
        
        # Need minimum requests before opening circuit
        if stats.total_requests < self.circuit_breaker_min_requests:
            return False
        
        # Check failure rate
        failure_rate = 1 - stats.success_rate
        is_open = failure_rate > self.circuit_breaker_threshold
        
        if is_open:
            logger.warning(
                f"Circuit breaker open for {provider.value}: "
                f"failure rate {failure_rate:.2%}"
            )
        
        return is_open
    
    def reset_circuit_breaker(self, provider: 'ProviderType'):  # type: ignore
        """Reset circuit breaker for provider"""
        if provider.value in self.load_stats:
            del self.load_stats[provider.value]
            logger.info(f"Reset circuit breaker for {provider.value}")
    
    def get_load_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get load statistics for all providers"""
        return {
            provider: {
                "active_requests": stats.active_requests,
                "total_requests": stats.total_requests,
                "failed_requests": stats.failed_requests,
                "success_rate": stats.success_rate,
                "average_latency_ms": stats.average_latency_ms
            }
            for provider, stats in self.load_stats.items()
        }
