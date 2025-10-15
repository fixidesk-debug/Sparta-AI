"""
AI Provider System - Example Usage and Integration Guide

This demonstrates how to use the comprehensive AI provider system
for various use cases in Sparta AI.
"""
import asyncio

# Import components
import os
from .ai_provider_manager import (
    AIProviderManager,
    ProviderType,
    ProviderConfig,
    AIRequest,
    create_provider_manager
)
from .model_selector import TaskType
from .cost_tracker import CostTracker


# Example 1: Basic Setup and Usage
async def example_basic_usage():
    """
    Basic AI provider setup and single request
    """
    print("=== Example 1: Basic Usage ===\n")
    
    # Create provider manager with multiple providers
    manager = await create_provider_manager(
        openai_key=os.getenv("OPENAI_API_KEY"),
        anthropic_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    try:
        # Create a simple request
        request = AIRequest(
            messages=[
                {"role": "user", "content": "Explain quantum computing in simple terms"}
            ],
            task_type=TaskType.GENERAL,
            temperature=0.7,
            max_tokens=500
        )
        
        # Generate response (automatic model selection)
        response = await manager.generate(request)
        
        print(f"Provider: {response.provider.value}")
        print(f"Model: {response.model}")
        print(f"Tokens: {response.tokens_used}")
        print(f"Cost: ${response.cost:.6f}")
        print(f"Latency: {response.latency_ms:.0f}ms")
        print(f"Quality Score: {response.quality_score:.2f}")
        print(f"\nResponse:\n{response.content}\n")
        
    finally:
        await manager.shutdown()


# Example 2: Code Generation with Specific Provider
async def example_code_generation():
    """
    Code generation task with provider preference
    """
    print("=== Example 2: Code Generation ===\n")
    
    manager = await create_provider_manager(
        openai_key=os.getenv("OPENAI_API_KEY"),
        anthropic_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    try:
        # Code generation request
        request = AIRequest(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Python programmer."
                },
                {
                    "role": "user",
                    "content": "Write a Python function to calculate Fibonacci numbers using memoization"
                }
            ],
            task_type=TaskType.CODE_GENERATION,
            temperature=0.3,  # Lower temperature for more deterministic code
            max_tokens=1000,
            provider_preference=ProviderType.ANTHROPIC  # Claude is great for code
        )
        
        response = await manager.generate(request)
        
        print(f"Generated code using {response.model}:")
        print(response.content)
        
    finally:
        await manager.shutdown()


# Example 3: Streaming Response
async def example_streaming():
    """
    Streaming response for real-time output
    """
    print("=== Example 3: Streaming Response ===\n")
    
    manager = await create_provider_manager(
        openai_key=os.getenv("OPENAI_API_KEY")
    )
    
    try:
        request = AIRequest(
            messages=[
                {"role": "user", "content": "Write a short story about AI"}
            ],
            task_type=TaskType.CREATIVE_WRITING,
            stream=True
        )
        
        print("Streaming response: ", end="", flush=True)
        
        async for chunk in manager.generate_stream(request):
            print(chunk, end="", flush=True)
        
        print("\n")
        
    finally:
        await manager.shutdown()


# Example 4: Provider Comparison
async def example_provider_comparison():
    """
    Compare responses from multiple providers
    """
    print("=== Example 4: Provider Comparison ===\n")
    
    manager = await create_provider_manager(
        openai_key=os.getenv("OPENAI_API_KEY"),
        anthropic_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    try:
        request = AIRequest(
            messages=[
                {"role": "user", "content": "What is the meaning of life?"}
            ],
            task_type=TaskType.GENERAL
        )
        
        # Compare all providers
        results = await manager.compare_providers(request)
        
        print("Comparison Results:\n")
        for provider, response in results.items():
            print(f"\n{provider.value}:")
            print(f"  Model: {response.model}")
            print(f"  Cost: ${response.cost:.6f}")
            print(f"  Quality: {response.quality_score:.2f}")
            print(f"  Latency: {response.latency_ms:.0f}ms")
            print(f"  Response: {response.content[:200]}...")
        
    finally:
        await manager.shutdown()


# Example 5: Cost Optimization
async def example_cost_optimization():
    """
    Optimize for cost while maintaining quality
    """
    print("=== Example 5: Cost Optimization ===\n")
    
    # Create manager with cost tracking
    providers = [
        ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key=os.getenv("OPENAI_API_KEY"),
            models=["gpt-4", "gpt-3.5-turbo"],
            cost_per_1k_input_tokens=0.03,
            cost_per_1k_output_tokens=0.06
        ),
        ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            models=["claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"],
            cost_per_1k_input_tokens=0.003,
            cost_per_1k_output_tokens=0.015
        )
    ]
    
    manager = AIProviderManager(
        providers=providers,
        enable_cost_optimization=True
    )
    
    await manager.initialize()
    
    try:
        # Simple task - should use cheaper model
        simple_request = AIRequest(
            messages=[
                {"role": "user", "content": "What is 2+2?"}
            ],
            task_type=TaskType.GENERAL
        )
        
        response = await manager.generate(simple_request)
        print(f"Simple task used: {response.model} (${response.cost:.6f})")
        
        # Complex task - should use more capable model
        complex_request = AIRequest(
            messages=[
                {"role": "user", "content": "Implement a binary search tree with AVL balancing"}
            ],
            task_type=TaskType.CODE_GENERATION
        )
        
        response = await manager.generate(complex_request)
        print(f"Complex task used: {response.model} (${response.cost:.6f})")
        
        # Get cost recommendations
        if manager.cost_tracker:
            recommendations = manager.cost_tracker.get_optimization_recommendations()
            print("\nCost Optimization Recommendations:")
            for rec in recommendations:
                print(f"  - {rec}")
        
    finally:
        await manager.shutdown()


# Example 6: Fallback Chain
async def example_fallback():
    """
    Demonstrate automatic failover
    """
    print("=== Example 6: Fallback Chain ===\n")
    
    manager = await create_provider_manager(
        openai_key=os.getenv("OPENAI_API_KEY"),
        anthropic_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    try:
        request = AIRequest(
            messages=[
                {"role": "user", "content": "Explain machine learning"}
            ],
            task_type=TaskType.GENERAL,
            provider_preference=ProviderType.OPENAI  # Try OpenAI first
        )
        
        # If OpenAI fails, will automatically try Anthropic
        response = await manager.generate(request)
        
        print(f"Request succeeded using: {response.provider.value}")
        print(f"Model: {response.model}")
        
    finally:
        await manager.shutdown()


# Example 7: Monitoring and Metrics
async def example_monitoring():
    """
    Monitor system metrics and health
    """
    print("=== Example 7: Monitoring and Metrics ===\n")
    
    manager = await create_provider_manager(
        openai_key=os.getenv("OPENAI_API_KEY"),
        anthropic_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    try:
        # Make several requests
        for i in range(5):
            request = AIRequest(
                messages=[
                    {"role": "user", "content": f"Tell me about topic {i}"}
                ],
                task_type=TaskType.GENERAL
            )
            await manager.generate(request)
        
        # Get metrics
        metrics = await manager.get_metrics()
        
        print("System Metrics:")
        print(f"  Total Requests: {metrics['total_requests']}")
        print(f"  Successful: {metrics['successful_requests']}")
        print(f"  Failed: {metrics['failed_requests']}")
        print(f"  Cached: {metrics['cached_responses']}")
        print(f"  Total Cost: ${metrics['total_cost']:.4f}")
        print(f"  Average Latency: {metrics['average_latency_ms']:.0f}ms")
        
        print("\nProvider Usage:")
        for provider, count in metrics['provider_usage'].items():
            print(f"  {provider}: {count} requests")
        
        print("\nProvider Health:")
        for provider, health in metrics['provider_health'].items():
            print(f"  {provider}: {health['status']}")
        
    finally:
        await manager.shutdown()


# Example 8: Context Window Management
async def example_context_management():
    """
    Handle large conversation histories
    """
    print("=== Example 8: Context Window Management ===\n")
    
    manager = await create_provider_manager(
        openai_key=os.getenv("OPENAI_API_KEY")
    )
    
    try:
        # Create large conversation history
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        
        for i in range(20):
            messages.append({"role": "user", "content": f"Question {i}: Tell me about topic {i}"})
            messages.append({"role": "assistant", "content": f"Answer {i}: Here's information about topic {i}..."})
        
        messages.append({"role": "user", "content": "Summarize our conversation"})
        
        # Context manager will automatically optimize
        request = AIRequest(
            messages=messages,
            task_type=TaskType.CONVERSATION,
            max_tokens=500
        )
        
        await manager.generate(request)
        
        print(f"Successfully handled {len(messages)} messages")
        print("Context optimized and response generated")
        
    finally:
        await manager.shutdown()


# Example 9: Custom Configuration
async def example_custom_config():
    """
    Advanced configuration with custom settings
    """
    print("=== Example 9: Custom Configuration ===\n")
    
    # Custom provider configurations
    providers = [
        ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key=os.getenv("OPENAI_API_KEY"),
            models=["gpt-4", "gpt-3.5-turbo"],
            priority=2,  # Higher priority
            max_concurrent_requests=20,
            timeout_seconds=30,
            retry_attempts=3,
            cost_per_1k_input_tokens=0.03,
            cost_per_1k_output_tokens=0.06,
            metadata={"region": "us-east-1"}
        ),
        ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            models=["claude-3-5-sonnet-20240620"],
            priority=1,  # Lower priority
            max_concurrent_requests=10,
            timeout_seconds=60,
            cost_per_1k_input_tokens=0.003,
            cost_per_1k_output_tokens=0.015
        )
    ]
    
    manager = AIProviderManager(
        providers=providers,
        enable_caching=True,
        enable_cost_optimization=True,
        enable_quality_scoring=True
    )
    
    await manager.initialize()
    
    try:
        request = AIRequest(
            messages=[
                {"role": "user", "content": "Hello!"}
            ],
            task_type=TaskType.CONVERSATION
        )
        
        response = await manager.generate(request)
        print(f"Response using custom config: {response.model}")
        
    finally:
        await manager.shutdown()


# Example 10: Budget Control
async def example_budget_control():
    """
    Set and monitor budget limits
    """
    print("=== Example 10: Budget Control ===\n")
    
    # Create cost tracker with budget
    providers = [
        ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key=os.getenv("OPENAI_API_KEY"),
            models=["gpt-3.5-turbo"],
            cost_per_1k_input_tokens=0.001,
            cost_per_1k_output_tokens=0.002
        )
    ]
    
    cost_tracker = CostTracker(providers, budget_limit=10.0)  # $10 monthly budget
    
    print(f"Monthly budget set: ${cost_tracker.budget_limit:.2f}")
    
    # Simulate usage
    for i in range(100):
        cost_tracker.record_usage(
            provider=ProviderType.OPENAI,
            model="gpt-3.5-turbo",
            input_tokens=1000,
            output_tokens=500,
            latency_ms=1500
        )
    
    # Get breakdown
    breakdown = cost_tracker.get_cost_breakdown()
    print(f"\nCurrent month spend: ${breakdown['current_month_total']:.2f}")
    print(f"Budget used: {breakdown['budget_used_percent']:.1f}%")
    
    # Get recommendations
    recommendations = cost_tracker.get_optimization_recommendations()
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"  - {rec}")


# Main execution
async def main():
    """Run all examples"""
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Code Generation", example_code_generation),
        ("Streaming", example_streaming),
        ("Provider Comparison", example_provider_comparison),
        ("Cost Optimization", example_cost_optimization),
        ("Fallback Chain", example_fallback),
        ("Monitoring", example_monitoring),
        ("Context Management", example_context_management),
        ("Custom Config", example_custom_config),
        ("Budget Control", example_budget_control)
    ]
    
    print("AI Provider System - Example Usage\n")
    print("=" * 60)
    
    for name, func in examples:
        print(f"\n\nRunning: {name}")
        print("-" * 60)
        try:
            await func()
        except Exception as e:
            print(f"Error in {name}: {e}")
        print("\n")


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
