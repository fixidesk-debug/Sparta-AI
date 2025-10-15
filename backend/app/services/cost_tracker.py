"""
Cost Tracker - Usage monitoring and cost optimization
Tracks API costs and provides optimization recommendations
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ai_provider_manager import ProviderType

logger = logging.getLogger(__name__)


@dataclass
class UsageRecord:
    """Single usage record"""
    timestamp: datetime
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    latency_ms: float


@dataclass
class UsageStats:
    """Aggregated usage statistics"""
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    average_cost_per_request: float = 0.0
    by_provider: Dict[str, float] = field(default_factory=dict)
    by_model: Dict[str, float] = field(default_factory=dict)
    by_hour: Dict[int, float] = field(default_factory=dict)


class CostTracker:
    """
    Track and optimize AI API costs
    
    Features:
    - Real-time cost tracking
    - Provider cost comparison
    - Budget monitoring and alerts
    - Usage analytics
    - Cost optimization recommendations
    """
    
    def __init__(self, provider_configs: List, budget_limit: Optional[float] = None):
        """
        Initialize cost tracker
        
        Args:
            provider_configs: List of ProviderConfig objects
            budget_limit: Optional monthly budget limit in USD
        """
        self.provider_configs = {c.provider_type: c for c in provider_configs}
        self.budget_limit = budget_limit
        
        # Usage history
        self.usage_history: List[UsageRecord] = []
        
        # Aggregated stats
        self.daily_costs: Dict[str, float] = defaultdict(float)  # date -> cost
        self.monthly_costs: Dict[str, float] = defaultdict(float)  # month -> cost
        self.provider_costs: Dict[str, float] = defaultdict(float)
        self.model_costs: Dict[str, float] = defaultdict(float)
        
        # Alerts
        self.alert_thresholds = [0.5, 0.75, 0.9, 1.0]  # % of budget
        self.alerts_sent: set = set()
        
        logger.info(
            f"CostTracker initialized"
            f"{f' with budget ${budget_limit:.2f}' if budget_limit else ''}"
        )
    
    def calculate_cost(
        self,
        provider: 'ProviderType',  # type: ignore
        model: str,
        tokens_used: int,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None
    ) -> float:
        """
        Calculate cost for API request
        
        Args:
            provider: Provider type
            model: Model name
            tokens_used: Total tokens (if input/output not specified)
            input_tokens: Input tokens
            output_tokens: Output tokens
            
        Returns:
            Cost in USD
        """
        config = self.provider_configs.get(provider)
        if not config:
            logger.warning(f"No cost config for provider {provider.value}")
            return 0.0
        
        # If input/output not specified, estimate 60/40 split
        if input_tokens is None or output_tokens is None:
            input_tokens = int(tokens_used * 0.6)
            output_tokens = int(tokens_used * 0.4)
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * config.cost_per_1k_input_tokens
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output_tokens
        
        total_cost = input_cost + output_cost
        
        return total_cost
    
    def record_usage(
        self,
        provider: 'ProviderType',  # type: ignore
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float
    ):
        """Record API usage"""
        # Calculate cost
        cost = self.calculate_cost(
            provider,
            model,
            input_tokens + output_tokens,
            input_tokens,
            output_tokens
        )
        
        # Create record
        record = UsageRecord(
            timestamp=datetime.now(),
            provider=provider.value,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            latency_ms=latency_ms
        )
        
        self.usage_history.append(record)
        
        # Update aggregates
        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")
        
        self.daily_costs[today] += cost
        self.monthly_costs[month] += cost
        self.provider_costs[provider.value] += cost
        self.model_costs[model] += cost
        
        # Check budget alerts
        if self.budget_limit:
            self._check_budget_alerts()
        
        logger.debug(
            f"Recorded usage: {provider.value}/{model} "
            f"{input_tokens}+{output_tokens} tokens, ${cost:.6f}"
        )
    
    def _check_budget_alerts(self):
        """Check if budget thresholds crossed"""
        if not self.budget_limit:
            return
        
        current_month = datetime.now().strftime("%Y-%m")
        monthly_spend = self.monthly_costs[current_month]
        usage_ratio = monthly_spend / self.budget_limit
        
        for threshold in self.alert_thresholds:
            if usage_ratio >= threshold:
                alert_key = f"{current_month}-{threshold}"
                if alert_key not in self.alerts_sent:
                    self.alerts_sent.add(alert_key)
                    logger.warning(
                        f"🚨 BUDGET ALERT: {threshold*100:.0f}% of monthly budget used "
                        f"(${monthly_spend:.2f} / ${self.budget_limit:.2f})"
                    )
    
    def get_usage_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> UsageStats:
        """
        Get usage statistics for date range
        
        Args:
            start_date: Start date (default: beginning of month)
            end_date: End date (default: now)
            
        Returns:
            Aggregated usage statistics
        """
        # Default date range
        if not start_date:
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        if not end_date:
            end_date = datetime.now()
        
        # Filter records
        filtered = [
            r for r in self.usage_history
            if start_date <= r.timestamp <= end_date
        ]
        
        if not filtered:
            return UsageStats()
        
        # Calculate stats
        stats = UsageStats()
        stats.total_requests = len(filtered)
        stats.total_tokens = sum(r.input_tokens + r.output_tokens for r in filtered)
        stats.total_cost = sum(r.cost for r in filtered)
        stats.average_cost_per_request = stats.total_cost / stats.total_requests
        
        # By provider
        provider_costs = defaultdict(float)
        for r in filtered:
            provider_costs[r.provider] += r.cost
        stats.by_provider = dict(provider_costs)
        
        # By model
        model_costs = defaultdict(float)
        for r in filtered:
            model_costs[r.model] += r.cost
        stats.by_model = dict(model_costs)
        
        # By hour
        hour_costs = defaultdict(float)
        for r in filtered:
            hour = r.timestamp.hour
            hour_costs[hour] += r.cost
        stats.by_hour = dict(hour_costs)
        
        return stats
    
    def get_cost_breakdown(self) -> Dict[str, Any]:
        """Get detailed cost breakdown"""
        current_month = datetime.now().strftime("%Y-%m")
        monthly_spend = self.monthly_costs[current_month]
        
        breakdown = {
            "current_month_total": monthly_spend,
            "budget_limit": self.budget_limit,
            "budget_used_percent": (
                (monthly_spend / self.budget_limit * 100) if self.budget_limit else None
            ),
            "by_provider": dict(self.provider_costs),
            "by_model": dict(self.model_costs),
            "daily_costs": dict(self.daily_costs),
            "total_requests": len(self.usage_history)
        }
        
        return breakdown
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get cost optimization recommendations"""
        recommendations = []
        
        if not self.usage_history:
            return ["No usage data available yet"]
        
        # Analyze provider costs
        if self.provider_costs:
            sorted_providers = sorted(
                self.provider_costs.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            most_expensive = sorted_providers[0]
            if len(sorted_providers) > 1:
                cheapest = sorted_providers[-1]
                savings = most_expensive[1] - cheapest[1]
                
                if savings > 10.0:  # More than $10 savings
                    recommendations.append(
                        f"Consider using {cheapest[0]} more often - "
                        f"potential savings of ${savings:.2f}"
                    )
        
        # Analyze model costs
        if self.model_costs:
            sorted_models = sorted(
                self.model_costs.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            most_expensive_model = sorted_models[0]
            recommendations.append(
                f"Most expensive model: {most_expensive_model[0]} "
                f"(${most_expensive_model[1]:.2f})"
            )
        
        # Budget warnings
        if self.budget_limit:
            current_month = datetime.now().strftime("%Y-%m")
            monthly_spend = self.monthly_costs[current_month]
            
            if monthly_spend > self.budget_limit:
                recommendations.append(
                    f"⚠️  Budget exceeded by ${monthly_spend - self.budget_limit:.2f}"
                )
            elif monthly_spend > self.budget_limit * 0.8:
                remaining = self.budget_limit - monthly_spend
                recommendations.append(
                    f"Approaching budget limit - ${remaining:.2f} remaining"
                )
        
        # Usage patterns
        stats = self.get_usage_stats()
        if stats.total_requests > 0:
            avg_cost = stats.average_cost_per_request
            if avg_cost > 0.10:
                recommendations.append(
                    f"High average cost per request (${avg_cost:.4f}) - "
                    "consider using cheaper models for simple tasks"
                )
        
        return recommendations if recommendations else ["Usage patterns look optimal"]
    
    def compare_provider_costs(self, tokens: int = 1000) -> Dict[str, float]:
        """
        Compare costs across providers for given token count
        
        Args:
            tokens: Number of tokens to compare (default: 1000)
            
        Returns:
            Dictionary mapping provider to cost
        """
        costs = {}
        
        for provider_type, config in self.provider_configs.items():
            # Assume 60/40 input/output split
            input_tokens = int(tokens * 0.6)
            output_tokens = int(tokens * 0.4)
            
            cost = self.calculate_cost(
                provider_type,
                config.models[0],
                tokens,
                input_tokens,
                output_tokens
            )
            
            costs[provider_type.value] = cost
        
        return costs
    
    def get_cheapest_provider(
        self,
        tokens: int = 1000
    ) -> Tuple[str, float]:
        """
        Get cheapest provider for token count
        
        Args:
            tokens: Number of tokens
            
        Returns:
            Tuple of (provider_name, cost)
        """
        costs = self.compare_provider_costs(tokens)
        if not costs:
            return ("none", 0.0)
        
        cheapest = min(costs.items(), key=lambda x: x[1])
        return cheapest
    
    def export_usage_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """
        Export usage report as markdown
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Markdown formatted report
        """
        stats = self.get_usage_stats(start_date, end_date)
        
        report = f"""# AI Usage Report
        
**Period:** {start_date or 'Start'} to {end_date or 'Now'}

## Summary
- **Total Requests:** {stats.total_requests:,}
- **Total Tokens:** {stats.total_tokens:,}
- **Total Cost:** ${stats.total_cost:.2f}
- **Average Cost/Request:** ${stats.average_cost_per_request:.4f}

## By Provider
"""
        
        for provider, cost in sorted(stats.by_provider.items(), key=lambda x: -x[1]):
            percent = (cost / stats.total_cost * 100) if stats.total_cost > 0 else 0
            report += f"- **{provider}:** ${cost:.2f} ({percent:.1f}%)\n"
        
        report += "\n## By Model\n"
        for model, cost in sorted(stats.by_model.items(), key=lambda x: -x[1]):
            percent = (cost / stats.total_cost * 100) if stats.total_cost > 0 else 0
            report += f"- **{model}:** ${cost:.2f} ({percent:.1f}%)\n"
        
        report += "\n## Recommendations\n"
        for rec in self.get_optimization_recommendations():
            report += f"- {rec}\n"
        
        return report
