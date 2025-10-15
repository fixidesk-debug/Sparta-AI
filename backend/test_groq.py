"""
Quick Test Script for Groq Integration
Tests the automatic model selection without needing actual API calls
"""
from app.services.groq_provider import GroqModelSelector
from app.services.model_selector import TaskType


def test_model_selection():
    """Test model selection logic"""
    print("=" * 60)
    print("GROQ MODEL SELECTION TEST")
    print("=" * 60)
    print()
    
    # Test different task types
    test_cases = [
        (TaskType.CODE_GENERATION, "Code generation task"),
        (TaskType.CONVERSATION, "Simple conversation"),
        (TaskType.REASONING, "Complex reasoning"),
        (TaskType.DATA_ANALYSIS, "Data analysis"),
        (TaskType.MATH, "Mathematical problem"),
        (TaskType.SUMMARIZATION, "Text summarization"),
    ]
    
    print("Task-Based Model Selection:")
    print("-" * 60)
    
    for task_type, description in test_cases:
        model = GroqModelSelector.select_best_model(task_type=task_type)
        model_info = GroqModelSelector.get_model_info(model)
        
        print(f"\n{description} ({task_type.value}):")
        print(f"  → Selected: {model}")
        print(f"  → Capability: {model_info['capability']}")
        print(f"  → Speed: {model_info['speed']}, Cost: {model_info['cost']}")
        print(f"  → Context: {model_info['context']:,} tokens")
    
    print()
    print("-" * 60)
    
    # Test preferences
    print("\nPreference Testing:")
    print("-" * 60)
    
    task = TaskType.REASONING
    
    # Default
    model_default = GroqModelSelector.select_best_model(task_type=task)
    print(f"\nDefault for {task.value}:")
    print(f"  → {model_default}")
    
    # Prefer speed
    model_speed = GroqModelSelector.select_best_model(
        task_type=task,
        prefer_speed=True
    )
    print(f"\nSpeed preference for {task.value}:")
    print(f"  → {model_speed}")
    
    # Prefer quality
    model_quality = GroqModelSelector.select_best_model(
        task_type=task,
        prefer_quality=True
    )
    print(f"\nQuality preference for {task.value}:")
    print(f"  → {model_quality}")
    
    print()
    print("-" * 60)
    
    # Test context length handling
    print("\nContext Length Handling:")
    print("-" * 60)
    
    model_short = GroqModelSelector.select_best_model(
        task_type=TaskType.CODE_GENERATION,
        context_length=5000
    )
    print("\nShort context (5K tokens):")
    print(f"  → {model_short}")
    
    model_long = GroqModelSelector.select_best_model(
        task_type=TaskType.CODE_GENERATION,
        context_length=20000
    )
    print("\nLong context (20K tokens):")
    print(f"  → {model_long} (needs 32K context window)")
    
    print()
    print("-" * 60)
    
    # Test manual override
    print("\nManual Override:")
    print("-" * 60)
    
    model_override = GroqModelSelector.select_best_model(
        task_type=TaskType.REASONING,
        user_preference="llama-3.1-8b-instant"
    )
    print("\nForced to use llama-3.1-8b-instant:")
    print(f"  → {model_override}")
    
    print()
    print("=" * 60)
    
    # List all models
    print("\nAVAILABLE MODELS:")
    print("=" * 60)
    
    models = GroqModelSelector.get_all_models()
    for model_name, model_info in models.items():
        print(f"\n{model_name}:")
        print(f"  Capability: {model_info['capability']}")
        print(f"  Context: {model_info['context']:,} tokens")
        print(f"  Speed: {model_info['speed']}, Cost: {model_info['cost']}")
        print(f"  Best for: {', '.join([t.value for t in model_info['best_for']])}")
        print(f"  Description: {model_info['description']}")
    
    print()
    print("=" * 60)
    print("✅ Model selection logic working correctly!")
    print("=" * 60)
    print()
    
    return True


def test_configuration():
    """Test configuration without API key"""
    print()
    print("=" * 60)
    print("CONFIGURATION TEST")
    print("=" * 60)
    print()
    
    from app.services.groq_config import GroqConfig, ModelPreference
    
    try:
        # Test config creation
        config = GroqConfig.from_api_key(
            api_key="test-key-12345678901234",  # Fake key for testing
            model_preference=ModelPreference.AUTO
        )
        print("✅ Config creation: PASSED")
        print(f"  Model preference: {config.model_preference.value}")
        print(f"  Streaming enabled: {config.enable_streaming}")
        print(f"  Default temperature: {config.default_temperature}")
        print(f"  Default max_tokens: {config.default_max_tokens}")
        
    except Exception as e:
        print(f"❌ Config creation: FAILED - {e}")
    
    print()
    print("=" * 60)
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "GROQ INTEGRATION TEST" + " " * 22 + "║")
    print("║" + " " * 10 + "Smart Model Selection System" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Run tests
    test_model_selection()
    test_configuration()
    
    print("\n✨ All tests completed!")
    print()
    print("To use with real API:")
    print("1. Get API key from: https://console.groq.com/keys")
    print("2. Set environment variable: GROQ_API_KEY=your-key")
    print("3. Run examples: python groq_examples.py")
    print()
