"""
Health Monitor - Provider availability and health tracking
Monitors provider status and manages circuit breakers
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from collections import deque
import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ai_provider_manager import ProviderType

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Provider health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class ProviderHealth:
    """Health information for a provider"""
    status: str
    success_rate: float
    average_latency_ms: float
    last_success: Optional[datetime]
    last_failure: Optional[datetime]
    consecutive_failures: int
    total_requests: int
    failed_requests: int
    last_error: Optional[str] = None
    uptime_percent: float = 100.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "status": self.status,
            "success_rate": self.success_rate,
            "average_latency_ms": self.average_latency_ms,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "consecutive_failures": self.consecutive_failures,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "last_error": self.last_error,
            "uptime_percent": self.uptime_percent
        }


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    timestamp: datetime
    success: bool
    latency_ms: float
    error: Optional[str] = None


class HealthMonitor:
    """
    Monitor provider health and availability
    
    Features:
    - Real-time health status tracking
    - Automatic health checks
    - Circuit breaker pattern
    - Performance metrics
    - Alerting on degradation
    """
    
    def __init__(self, provider_configs: List, check_interval: int = 60):
        """
        Initialize health monitor
        
        Args:
            provider_configs: List of ProviderConfig objects
            check_interval: Health check interval in seconds
        """
        self.provider_configs = {c.provider_type: c for c in provider_configs}
        self.check_interval = check_interval
        
        # Health data per provider
        self.health_data: Dict[str, ProviderHealth] = {}
        self.health_history: Dict[str, deque] = {}
        
        # Initialize health data
        for provider_type in self.provider_configs.keys():
            self.health_data[provider_type.value] = ProviderHealth(
                status=HealthStatus.UNKNOWN.value,
                success_rate=0.0,
                average_latency_ms=0.0,
                last_success=None,
                last_failure=None,
                consecutive_failures=0,
                total_requests=0,
                failed_requests=0
            )
            self.health_history[provider_type.value] = deque(maxlen=100)
        
        # Circuit breaker thresholds
        self.failure_threshold = 5  # Consecutive failures before marking down
        self.degraded_threshold = 0.7  # Success rate threshold for degraded status
        
        # Monitoring task
        self.monitoring_task: Optional[asyncio.Task] = None
        
        logger.info(f"HealthMonitor initialized for {len(self.provider_configs)} providers")
    
    async def start_monitoring(self, provider_instances: Dict):
        """Start health monitoring background task"""
        self.provider_instances = provider_instances
        self.monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("Health monitoring started")
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitoring stopped")
    
    async def _monitor_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self.check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    async def _perform_health_checks(self):
        """Perform health checks on all providers"""
        for provider_type, instance in self.provider_instances.items():
            try:
                result = await self._check_provider_health(instance)
                await self._record_health_check(provider_type, result)
            except Exception as e:
                logger.error(f"Health check failed for {provider_type.value}: {e}")
                result = HealthCheckResult(
                    timestamp=datetime.now(),
                    success=False,
                    latency_ms=0.0,
                    error=str(e)
                )
                await self._record_health_check(provider_type, result)
    
    async def _check_provider_health(self, instance) -> HealthCheckResult:
        """Perform health check on provider instance"""
        start = datetime.now()
        
        try:
            # Simple test message
            test_messages = [
                {"role": "user", "content": "Hello"}
            ]
            
            # Try to generate with short timeout
            response = await asyncio.wait_for(
                instance.generate_completion(
                    messages=test_messages,
                    max_tokens=10,
                    temperature=0.1
                ),
                timeout=10.0
            )
            
            latency = (datetime.now() - start).total_seconds() * 1000
            
            return HealthCheckResult(
                timestamp=datetime.now(),
                success=bool(response),
                latency_ms=latency
            )
            
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return HealthCheckResult(
                timestamp=datetime.now(),
                success=False,
                latency_ms=latency,
                error=str(e)
            )
    
    async def _record_health_check(
        self,
        provider: 'ProviderType',  # type: ignore
        result: HealthCheckResult
    ):
        """Record health check result"""
        health = self.health_data[provider.value]
        history = self.health_history[provider.value]
        
        # Add to history
        history.append(result)
        
        # Update metrics
        health.total_requests += 1
        if not result.success:
            health.failed_requests += 1
            health.consecutive_failures += 1
            health.last_failure = result.timestamp
            health.last_error = result.error
        else:
            health.consecutive_failures = 0
            health.last_success = result.timestamp
        
        # Calculate success rate from history
        if history:
            successful = sum(1 for r in history if r.success)
            health.success_rate = successful / len(history)
        
        # Calculate average latency
        if history:
            latencies = [r.latency_ms for r in history if r.success]
            if latencies:
                health.average_latency_ms = sum(latencies) / len(latencies)
        
        # Update status
        health.status = self._determine_status(health).value
        
        # Log status changes
        if health.status == HealthStatus.DOWN.value:
            logger.warning(
                f"Provider {provider.value} marked as DOWN: "
                f"{health.consecutive_failures} consecutive failures"
            )
        elif health.status == HealthStatus.DEGRADED.value:
            logger.warning(
                f"Provider {provider.value} marked as DEGRADED: "
                f"success rate {health.success_rate:.2%}"
            )
    
    def _determine_status(self, health: ProviderHealth) -> HealthStatus:
        """Determine health status from metrics"""
        # Check consecutive failures
        if health.consecutive_failures >= self.failure_threshold:
            return HealthStatus.DOWN
        
        # Check success rate
        if health.total_requests >= 10:  # Need minimum sample
            if health.success_rate < self.degraded_threshold:
                return HealthStatus.DEGRADED
        
        # Check if we have recent success
        if health.last_success:
            time_since_success = datetime.now() - health.last_success
            if time_since_success > timedelta(minutes=5):
                return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    async def record_success(self, provider: 'ProviderType'):  # type: ignore
        """Record successful request"""
        health = self.health_data[provider.value]
        health.total_requests += 1
        health.consecutive_failures = 0
        health.last_success = datetime.now()
        
        # Update success rate
        history = self.health_history[provider.value]
        result = HealthCheckResult(
            timestamp=datetime.now(),
            success=True,
            latency_ms=0.0
        )
        history.append(result)
        
        if history:
            successful = sum(1 for r in history if r.success)
            health.success_rate = successful / len(history)
        
        # Update status
        health.status = self._determine_status(health).value
    
    async def record_failure(self, provider: 'ProviderType', error: str):  # type: ignore
        """Record failed request"""
        health = self.health_data[provider.value]
        health.total_requests += 1
        health.failed_requests += 1
        health.consecutive_failures += 1
        health.last_failure = datetime.now()
        health.last_error = error
        
        # Update success rate
        history = self.health_history[provider.value]
        result = HealthCheckResult(
            timestamp=datetime.now(),
            success=False,
            latency_ms=0.0,
            error=error
        )
        history.append(result)
        
        if history:
            successful = sum(1 for r in history if r.success)
            health.success_rate = successful / len(history)
        
        # Update status
        old_status = health.status
        health.status = self._determine_status(health).value
        
        # Alert on status change
        if health.status != old_status:
            logger.warning(
                f"Provider {provider.value} status changed: "
                f"{old_status} -> {health.status}"
            )
    
    async def get_provider_health(
        self,
        provider: 'ProviderType'  # type: ignore
    ) -> ProviderHealth:
        """Get health status for provider"""
        return self.health_data[provider.value]
    
    async def get_all_health_status(self) -> Dict['ProviderType', ProviderHealth]:  # type: ignore
        """Get health status for all providers"""
        return {
            ProviderType(name): health
            for name, health in self.health_data.items()
        }
    
    def get_healthy_providers(self) -> List[str]:
        """Get list of healthy provider names"""
        return [
            name for name, health in self.health_data.items()
            if health.status == HealthStatus.HEALTHY.value
        ]
    
    def is_provider_healthy(self, provider: 'ProviderType') -> bool:  # type: ignore
        """Check if provider is healthy"""
        health = self.health_data.get(provider.value)
        if not health:
            return False
        return health.status in [HealthStatus.HEALTHY.value, HealthStatus.DEGRADED.value]
    
    def get_health_report(self) -> str:
        """Generate health report"""
        report = "# AI Provider Health Report\n\n"
        report += f"**Generated:** {datetime.now().isoformat()}\n\n"
        
        for name, health in self.health_data.items():
            status_emoji = {
                HealthStatus.HEALTHY.value: "✅",
                HealthStatus.DEGRADED.value: "⚠️",
                HealthStatus.DOWN.value: "❌",
                HealthStatus.UNKNOWN.value: "❓"
            }.get(health.status, "❓")
            
            report += f"## {status_emoji} {name}\n"
            report += f"- **Status:** {health.status}\n"
            report += f"- **Success Rate:** {health.success_rate:.1%}\n"
            report += f"- **Avg Latency:** {health.average_latency_ms:.0f}ms\n"
            report += f"- **Total Requests:** {health.total_requests}\n"
            report += f"- **Failed Requests:** {health.failed_requests}\n"
            report += f"- **Consecutive Failures:** {health.consecutive_failures}\n"
            
            if health.last_success:
                report += f"- **Last Success:** {health.last_success.isoformat()}\n"
            if health.last_failure:
                report += f"- **Last Failure:** {health.last_failure.isoformat()}\n"
            if health.last_error:
                report += f"- **Last Error:** {health.last_error}\n"
            
            report += "\n"
        
        return report
