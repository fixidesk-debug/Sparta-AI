"""
Groq Integration Examples
Simple usage examples with automatic model selection
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.groq_config import GroqManager, create_groq_manager
from app.services.model_selector import TaskType


async def example_1_simple_usage():
    """Example 1: Simplest usage - just API key"""
    print("=" * 60)
    print("EXAMPLE 1: Simple Usage")
    print("=" * 60)
    
    # Initialize with just API key (auto-selects models for each task)
    manager = create_groq_manager(api_key=os.getenv("GROQ_API_KEY"))
    
    # Generate response - automatically selects best model
    response = await manager.generate(
        messages=[
            {"role": "user", "content": "Explain quantum computing in simple terms"}
        ]
    )
    
    print(f"Model used: {response['model']}")
    print(f"Response: {response['content'][:200]}...")
    print()


async def example_2_task_based_selection():
    """Example 2: Different tasks automatically use different models"""
    print("=" * 60)
    print("EXAMPLE 2: Task-Based Model Selection")
    print("=" * 60)
    
    manager = create_groq_manager(api_key=os.getenv("GROQ_API_KEY"))
    
    # Code generation task - will use mixtral-8x7b-32768 (best for code)
    code_response = await manager.generate(
        messages=[
            {"role": "user", "content": "Write a Python function to calculate fibonacci"}
        ],
        task_type=TaskType.CODE_GENERATION
    )
    print(f"Code Task - Model: {code_response['model']}")
    print(f"Response: {code_response['content'][:150]}...\n")
    
    # Simple conversation - will use llama-3.1-8b-instant (fast)
    chat_response = await manager.generate(
        messages=[
            {"role": "user", "content": "What's the capital of France?"}
        ],
        task_type=TaskType.CONVERSATION
    )
    print(f"Chat Task - Model: {chat_response['model']}")
    print(f"Response: {chat_response['content']}\n")
    
    # Complex reasoning - will use llama-3.3-70b-versatile (smartest)
    reasoning_response = await manager.generate(
        messages=[
            {"role": "user", "content": "Analyze the ethical implications of AI in healthcare"}
        ],
        task_type=TaskType.REASONING
    )
    print(f"Reasoning Task - Model: {reasoning_response['model']}")
    print(f"Response: {reasoning_response['content'][:150]}...\n")


async def example_3_streaming():
    """Example 3: Streaming responses"""
    print("=" * 60)
    print("EXAMPLE 3: Streaming Responses")
    print("=" * 60)
    
    manager = create_groq_manager(api_key=os.getenv("GROQ_API_KEY"))
    
    print("Streaming response: ", end="", flush=True)
    async for chunk in manager.generate_stream(
        messages=[
            {"role": "user", "content": "Tell me a short story about a robot"}
        ],
        task_type=TaskType.CREATIVE_WRITING
    ):
        print(chunk, end="", flush=True)
    print("\n")


async def example_4_model_override():
    """Example 4: Override automatic selection"""
    print("=" * 60)
    print("EXAMPLE 4: Manual Model Override")
    print("=" * 60)
    
    manager = create_groq_manager(api_key=os.getenv("GROQ_API_KEY"))
    
    # Force use of fast model even for complex task
    response = await manager.generate(
        messages=[
            {"role": "user", "content": "Explain quantum entanglement"}
        ],
        task_type=TaskType.REASONING,
        model="llama-3.1-8b-instant"  # Override to use fast model
    )
    
    print(f"Forced model: {response['model']}")
    print(f"Response: {response['content'][:200]}...")
    print()


async def example_5_model_recommendations():
    """Example 5: Get model recommendations"""
    print("=" * 60)
    print("EXAMPLE 5: Model Recommendations")
    print("=" * 60)
    
    manager = create_groq_manager(api_key=os.getenv("GROQ_API_KEY"))
    
    # Get recommendation for different tasks
    tasks = [
        TaskType.CODE_GENERATION,
        TaskType.CONVERSATION,
        TaskType.REASONING,
        TaskType.DATA_ANALYSIS
    ]
    
    for task in tasks:
        recommendation = manager.recommend_model(task)
        print(f"\nTask: {task.value}")
        print(f"  Recommended: {recommendation['recommended_model']}")
        print(f"  Reason: {recommendation['reasoning']}")
    
    print()


async def example_6_list_models():
    """Example 6: List all available models"""
    print("=" * 60)
    print("EXAMPLE 6: Available Models")
    print("=" * 60)
    
    manager = create_groq_manager(api_key=os.getenv("GROQ_API_KEY"))
    
    models = manager.get_available_models()
    print(f"Available models: {len(models)}\n")
    
    for model_name in models:
        info = manager.get_model_info(model_name)
        print(f"{model_name}:")
        print(f"  Capability: {info['capability']}")
        print(f"  Context: {info['context']} tokens")
        print(f"  Speed: {info['speed']}, Cost: {info['cost']}")
        print(f"  Best for: {', '.join([t.value for t in info['best_for']])}")
        print(f"  Description: {info['description']}\n")


async def example_7_chat_conversation():
    """Example 7: Multi-turn conversation"""
    print("=" * 60)
    print("EXAMPLE 7: Multi-Turn Conversation")
    print("=" * 60)
    
    manager = create_groq_manager(api_key=os.getenv("GROQ_API_KEY"))
    
    messages = [
        {"role": "user", "content": "What is machine learning?"}
    ]
    
    # First response
    response1 = await manager.generate(
        messages=messages,
        task_type=TaskType.CONVERSATION
    )
    print(f"User: {messages[0]['content']}")
    print(f"AI ({response1['model']}): {response1['content']}\n")
    
    # Add to conversation
    messages.append({"role": "assistant", "content": response1['content']})
    messages.append({"role": "user", "content": "Can you give me an example?"})
    
    # Second response
    response2 = await manager.generate(
        messages=messages,
        task_type=TaskType.CONVERSATION
    )
    print(f"User: {messages[-1]['content']}")
    print(f"AI ({response2['model']}): {response2['content'][:200]}...")
    print()


async def example_8_preferences():
    """Example 8: Set preferences for speed or quality"""
    print("=" * 60)
    print("EXAMPLE 8: Model Preferences")
    print("=" * 60)
    
    from app.services.groq_config import GroqConfig, ModelPreference
    
    # Prefer speed
    config_speed = GroqConfig.from_api_key(
        api_key=os.getenv("GROQ_API_KEY"),
        model_preference=ModelPreference.SPEED
    )
    manager_speed = GroqManager(config=config_speed)
    
    response_speed = await manager_speed.generate(
        messages=[{"role": "user", "content": "Explain AI"}],
        task_type=TaskType.REASONING
    )
    print(f"Speed preference - Model: {response_speed['model']}")
    
    # Prefer quality
    config_quality = GroqConfig.from_api_key(
        api_key=os.getenv("GROQ_API_KEY"),
        model_preference=ModelPreference.QUALITY
    )
    manager_quality = GroqManager(config=config_quality)
    
    response_quality = await manager_quality.generate(
        messages=[{"role": "user", "content": "Explain AI"}],
        task_type=TaskType.REASONING
    )
    print(f"Quality preference - Model: {response_quality['model']}")
    print()


async def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "GROQ AI - USAGE EXAMPLES" + " " * 24 + "║")
    print("║" + " " * 5 + "Automatic Model Selection Based on Task" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Note: These examples won't actually run without a real API key
    # Uncomment the ones you want to try with a real key
    
    print("To run these examples:")
    print("1. Set GROQ_API_KEY environment variable with your actual Groq API key")
    print("2. Get your API key from: https://console.groq.com/keys")
    print("3. Uncomment the example functions below")
    print()
    
    # await example_1_simple_usage()
    # await example_2_task_based_selection()
    # await example_3_streaming()
    # await example_4_model_override()
    # await example_5_model_recommendations()
    # await example_6_list_models()
    # await example_7_chat_conversation()
    # await example_8_preferences()
    
    print("Examples ready to run!")


if __name__ == "__main__":
    asyncio.run(main())
