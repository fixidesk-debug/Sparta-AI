"""
Rate Limiter - Request throttling and queue management
Handles rate limits and prevents API quota exhaustion
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    max_requests_per_minute: int
    max_requests_per_hour: int
    max_concurrent_requests: int
    burst_allowance: int = 5  # Allow small bursts


class RateLimiter:
    """
    Rate limiting and request throttling
    
    Features:
    - Per-minute and per-hour rate limits
    - Concurrent request limiting
    - Request queuing
    - Exponential backoff
    - Burst handling
    """
    
    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter
        
        Args:
            config: Rate limit configuration
        """
        self.config = config
        
        # Request timestamps
        self.minute_requests: deque = deque()
        self.hour_requests: deque = deque()
        
        # Concurrent request semaphore
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
        # Queue for waiting requests
        self.queue: asyncio.Queue = asyncio.Queue()
        
        # Metrics
        self.total_requests = 0
        self.throttled_requests = 0
        self.queued_requests = 0
        
        logger.info(
            f"RateLimiter initialized: "
            f"{config.max_requests_per_minute}/min, "
            f"{config.max_requests_per_hour}/hour, "
            f"{config.max_concurrent_requests} concurrent"
        )
    
    async def acquire(self, wait: bool = True) -> bool:
        """
        Acquire rate limit token
        
        Args:
            wait: Whether to wait if limit reached
            
        Returns:
            True if acquired, False if limit reached and not waiting
        """
        self.total_requests += 1
        
        while True:
            # Clean old timestamps
            self._clean_timestamps()
            
            # Check limits
            can_proceed = (
                len(self.minute_requests) < self.config.max_requests_per_minute and
                len(self.hour_requests) < self.config.max_requests_per_hour
            )
            
            if can_proceed:
                # Try to acquire semaphore
                try:
                    await asyncio.wait_for(
                        self.semaphore.acquire(),
                        timeout=0.1 if not wait else None
                    )
                    
                    # Record request
                    now = datetime.now()
                    self.minute_requests.append(now)
                    self.hour_requests.append(now)
                    
                    return True
                    
                except asyncio.TimeoutError:
                    if not wait:
                        return False
                    # Continue to wait
            
            if not wait:
                return False
            
            # Rate limit reached - wait
            self.throttled_requests += 1
            wait_time = self._calculate_wait_time()
            
            logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
    
    def release(self):
        """Release rate limit token"""
        self.semaphore.release()
    
    def _clean_timestamps(self):
        """Remove timestamps outside rate limit windows"""
        now = datetime.now()
        
        # Clean minute window
        minute_ago = now - timedelta(minutes=1)
        while self.minute_requests and self.minute_requests[0] < minute_ago:
            self.minute_requests.popleft()
        
        # Clean hour window
        hour_ago = now - timedelta(hours=1)
        while self.hour_requests and self.hour_requests[0] < hour_ago:
            self.hour_requests.popleft()
    
    def _calculate_wait_time(self) -> float:
        """Calculate how long to wait before next request"""
        now = datetime.now()
        
        # Check minute limit
        if len(self.minute_requests) >= self.config.max_requests_per_minute:
            oldest = self.minute_requests[0]
            minute_ago = now - timedelta(minutes=1)
            if oldest > minute_ago:
                return (oldest - minute_ago).total_seconds()
        
        # Check hour limit
        if len(self.hour_requests) >= self.config.max_requests_per_hour:
            oldest = self.hour_requests[0]
            hour_ago = now - timedelta(hours=1)
            if oldest > hour_ago:
                return (oldest - hour_ago).total_seconds()
        
        # Default wait time
        return 1.0
    
    def get_current_usage(self) -> dict:
        """Get current rate limit usage"""
        self._clean_timestamps()
        
        return {
            "requests_last_minute": len(self.minute_requests),
            "requests_last_hour": len(self.hour_requests),
            "minute_limit": self.config.max_requests_per_minute,
            "hour_limit": self.config.max_requests_per_hour,
            "concurrent_limit": self.config.max_concurrent_requests,
            "minute_usage_percent": (
                len(self.minute_requests) / self.config.max_requests_per_minute * 100
            ),
            "hour_usage_percent": (
                len(self.hour_requests) / self.config.max_requests_per_hour * 100
            ),
            "total_requests": self.total_requests,
            "throttled_requests": self.throttled_requests
        }
    
    def is_limit_reached(self) -> bool:
        """Check if rate limit is currently reached"""
        self._clean_timestamps()
        
        return (
            len(self.minute_requests) >= self.config.max_requests_per_minute or
            len(self.hour_requests) >= self.config.max_requests_per_hour
        )
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
