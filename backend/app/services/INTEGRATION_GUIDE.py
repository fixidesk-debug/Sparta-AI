"""
Quick Integration Guide - AI Provider System into Sparta AI

This guide shows how to integrate the new AI provider system into existing code.
"""

# ============================================================================
# STEP 1: Update Environment Variables (.env)
# ============================================================================

"""
Add to .env file:

# AI Provider Configuration
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here  # Optional

# AI Provider Settings
AI_DEFAULT_PROVIDER=openai
AI_ENABLE_CACHING=true
AI_ENABLE_COST_OPTIMIZATION=true
AI_ENABLE_QUALITY_SCORING=true
AI_MONTHLY_BUDGET=100.0  # Optional budget limit in USD

# Model Preferences
AI_CODE_MODEL=claude-3-5-sonnet-20240620  # Best for code
AI_CHAT_MODEL=gpt-3.5-turbo  # Fast for chat
AI_ANALYSIS_MODEL=gpt-4  # Best for analysis
"""


# ============================================================================
# STEP 2: Update Config (app/core/config.py)
# ============================================================================

"""
Add to Settings class in config.py:

class Settings(BaseSettings):
    # ... existing settings ...
    
    # AI Provider System
    AI_DEFAULT_PROVIDER: str = "openai"
    AI_ENABLE_CACHING: bool = True
    AI_ENABLE_COST_OPTIMIZATION: bool = True
    AI_ENABLE_QUALITY_SCORING: bool = True
    AI_MONTHLY_BUDGET: Optional[float] = None
    
    # Model Preferences
    AI_CODE_MODEL: str = "claude-3-5-sonnet-20240620"
    AI_CHAT_MODEL: str = "gpt-3.5-turbo"
    AI_ANALYSIS_MODEL: str = "gpt-4"
"""


# ============================================================================
# STEP 3: Create AI Manager Instance (app/main.py)
# ============================================================================

"""
Add to main.py:

from app.services.ai_provider_manager import create_provider_manager
from app.core.config import settings

# Global AI manager instance
ai_manager = None

@app.on_event("startup")
async def startup_event():
    '''Initialize AI provider manager on startup'''
    global ai_manager
    
    logger.info("Initializing AI Provider Manager...")
    
    try:
        ai_manager = await create_provider_manager(
            openai_key=settings.OPENAI_API_KEY,
            anthropic_key=settings.ANTHROPIC_API_KEY,
            google_key=settings.GOOGLE_API_KEY
        )
        
        logger.info("AI Provider Manager initialized successfully")
        
        # Log initial metrics
        metrics = await ai_manager.get_metrics()
        logger.info(f"Active providers: {metrics['active_providers']}")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI Provider Manager: {e}")
        # System can still run without AI if needed

@app.on_event("shutdown")
async def shutdown_event():
    '''Shutdown AI provider manager'''
    global ai_manager
    
    if ai_manager:
        logger.info("Shutting down AI Provider Manager...")
        await ai_manager.shutdown()
        logger.info("AI Provider Manager shut down successfully")
"""


# ============================================================================
# STEP 4: Update AI Code Generator (app/services/ai_code_generator.py)
# ============================================================================

"""
Replace existing OpenAI code with:

from app.services.ai_provider_manager import AIRequest, AIResponse
from app.services.model_selector import TaskType
from app.main import ai_manager

class AICodeGenerator:
    '''Generate code using AI provider system'''
    
    async def generate_code(
        self,
        query: str,
        context: Optional[str] = None,
        data_info: Optional[Dict[str, Any]] = None
    ) -> str:
        '''
        Generate code using best available AI provider
        
        Args:
            query: User's code generation request
            context: Additional context about the data
            data_info: Information about the dataset
            
        Returns:
            Generated Python code
        '''
        # Build system message
        system_message = '''You are an expert Python data analyst and programmer.
Generate clean, efficient, and well-documented Python code for data analysis.
Use pandas, numpy, matplotlib, and other standard libraries as needed.'''
        
        # Build user message
        user_message = f"Query: {query}\n\n"
        
        if context:
            user_message += f"Context: {context}\n\n"
        
        if data_info:
            user_message += f"Dataset Info: {json.dumps(data_info, indent=2)}\n\n"
        
        user_message += "Generate Python code to solve this task."
        
        # Create AI request
        request = AIRequest(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            task_type=TaskType.CODE_GENERATION,
            temperature=0.3,  # Lower for more deterministic code
            max_tokens=2000
        )
        
        # Generate code (automatic provider selection)
        response = await ai_manager.generate(request)
        
        # Log metrics
        logger.info(
            f"Code generated using {response.model} "
            f"(cost: ${response.cost:.6f}, "
            f"quality: {response.quality_score:.2f})"
        )
        
        # Extract code from response
        code = self._extract_code(response.content)
        
        return code
    
    def _extract_code(self, response: str) -> str:
        '''Extract code from markdown code blocks'''
        import re
        
        # Try to extract from code blocks
        code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', response, re.DOTALL)
        
        if code_blocks:
            return code_blocks[0].strip()
        
        # Return full response if no code blocks
        return response.strip()
    
    async def generate_code_streaming(
        self,
        query: str,
        context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        '''Generate code with streaming response'''
        
        system_message = "You are an expert Python programmer."
        user_message = f"Generate Python code for: {query}"
        
        if context:
            user_message += f"\n\nContext: {context}"
        
        request = AIRequest(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            task_type=TaskType.CODE_GENERATION,
            temperature=0.3,
            stream=True
        )
        
        async for chunk in ai_manager.generate_stream(request):
            yield chunk
"""


# ============================================================================
# STEP 5: Update Conversation Service (app/services/conversation_memory.py)
# ============================================================================

"""
Update conversation handling:

from app.services.ai_provider_manager import AIRequest
from app.services.model_selector import TaskType

class ConversationMemory:
    '''Manage conversation with AI'''
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        '''Generate AI response for conversation'''
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Create request
        request = AIRequest(
            messages=conversation_history,
            task_type=TaskType.CONVERSATION,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Generate response (context automatically optimized)
        response = await ai_manager.generate(request)
        
        # Add to history
        conversation_history.append({
            "role": "assistant",
            "content": response.content
        })
        
        return response.content
    
    async def generate_streaming_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        '''Generate streaming response'''
        
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        request = AIRequest(
            messages=conversation_history,
            task_type=TaskType.CONVERSATION,
            temperature=0.7,
            stream=True
        )
        
        full_response = ""
        
        async for chunk in ai_manager.generate_stream(request):
            full_response += chunk
            yield chunk
        
        # Add complete response to history
        conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
"""


# ============================================================================
# STEP 6: Add Admin Dashboard Endpoints (app/api/v1/endpoints/admin.py)
# ============================================================================

"""
Create new endpoints for monitoring:

from fastapi import APIRouter, Depends
from app.main import ai_manager

router = APIRouter()

@router.get("/ai/metrics")
async def get_ai_metrics():
    '''Get AI provider system metrics'''
    
    if not ai_manager:
        return {"error": "AI manager not initialized"}
    
    metrics = await ai_manager.get_metrics()
    return metrics

@router.get("/ai/health")
async def get_ai_health():
    '''Get AI provider health status'''
    
    if not ai_manager:
        return {"error": "AI manager not initialized"}
    
    health_status = await ai_manager.health_monitor.get_all_health_status()
    
    return {
        provider.value: health.to_dict()
        for provider, health in health_status.items()
    }

@router.get("/ai/costs")
async def get_ai_costs():
    '''Get cost breakdown and recommendations'''
    
    if not ai_manager or not ai_manager.cost_tracker:
        return {"error": "Cost tracker not available"}
    
    breakdown = ai_manager.cost_tracker.get_cost_breakdown()
    recommendations = ai_manager.cost_tracker.get_optimization_recommendations()
    
    return {
        "breakdown": breakdown,
        "recommendations": recommendations
    }

@router.get("/ai/report")
async def get_ai_report():
    '''Get comprehensive AI usage report'''
    
    if not ai_manager:
        return {"error": "AI manager not initialized"}
    
    # Get metrics
    metrics = await ai_manager.get_metrics()
    
    # Get cost report
    cost_report = ""
    if ai_manager.cost_tracker:
        cost_report = ai_manager.cost_tracker.export_usage_report()
    
    # Get health report
    health_report = ai_manager.health_monitor.get_health_report()
    
    return {
        "metrics": metrics,
        "cost_report": cost_report,
        "health_report": health_report
    }
"""


# ============================================================================
# STEP 7: Add WebSocket Updates (app/services/websocket_manager.py)
# ============================================================================

"""
Send AI metrics to connected clients:

async def broadcast_ai_metrics(self):
    '''Broadcast AI metrics to all connected clients'''
    
    from app.main import ai_manager
    
    if not ai_manager:
        return
    
    try:
        metrics = await ai_manager.get_metrics()
        
        await self.broadcast({
            "type": "ai_metrics",
            "data": {
                "total_requests": metrics["total_requests"],
                "success_rate": metrics["successful_requests"] / max(metrics["total_requests"], 1),
                "cache_hit_rate": metrics["cached_responses"] / max(metrics["total_requests"], 1),
                "average_latency_ms": metrics["average_latency_ms"],
                "total_cost": metrics["total_cost"]
            }
        })
    except Exception as e:
        logger.error(f"Error broadcasting AI metrics: {e}")

# Call periodically (e.g., every 30 seconds)
async def start_periodic_metrics_broadcast(self):
    '''Start periodic AI metrics broadcast'''
    while True:
        await asyncio.sleep(30)
        await self.broadcast_ai_metrics()
"""


# ============================================================================
# STEP 8: Testing
# ============================================================================

"""
Test the integration:

# Test 1: Basic code generation
async def test_code_generation():
    request = AIRequest(
        messages=[
            {"role": "user", "content": "Write a function to calculate fibonacci"}
        ],
        task_type=TaskType.CODE_GENERATION
    )
    
    response = await ai_manager.generate(request)
    print(f"Generated code using {response.model}")
    print(f"Cost: ${response.cost:.6f}")
    print(response.content)

# Test 2: Conversation
async def test_conversation():
    messages = [
        {"role": "user", "content": "What is machine learning?"}
    ]
    
    request = AIRequest(
        messages=messages,
        task_type=TaskType.CONVERSATION
    )
    
    response = await ai_manager.generate(request)
    print(response.content)

# Test 3: Metrics
async def test_metrics():
    metrics = await ai_manager.get_metrics()
    print(f"Total requests: {metrics['total_requests']}")
    print(f"Total cost: ${metrics['total_cost']:.2f}")
    print(f"Provider usage: {metrics['provider_usage']}")

# Run tests
import asyncio
asyncio.run(test_code_generation())
asyncio.run(test_conversation())
asyncio.run(test_metrics())
"""


# ============================================================================
# MIGRATION CHECKLIST
# ============================================================================

"""
✅ Checklist for Integration:

1. Environment Setup
   [ ] Add API keys to .env file
   [ ] Update config.py with AI settings
   [ ] Install dependencies: pip install tiktoken google-generativeai

2. Code Updates
   [ ] Update main.py with startup/shutdown handlers
   [ ] Replace AI code in ai_code_generator.py
   [ ] Update conversation_memory.py
   [ ] Add admin endpoints for monitoring

3. Testing
   [ ] Test basic code generation
   [ ] Test conversation handling
   [ ] Test streaming responses
   [ ] Test provider fallback
   [ ] Test metrics collection
   [ ] Test cost tracking

4. Monitoring
   [ ] Set up health checks
   [ ] Configure budget alerts
   [ ] Review metrics dashboard
   [ ] Test WebSocket updates

5. Production
   [ ] Set production API keys
   [ ] Configure budget limits
   [ ] Enable monitoring alerts
   [ ] Review security settings
   [ ] Test failover scenarios
"""


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

"""
The new system is designed to be a drop-in replacement.

Old code:
    from app.services.ai_providers import OpenAIProvider
    
    provider = OpenAIProvider(api_key, model)
    response = await provider.generate_completion(messages)

New code (automatic provider selection):
    from app.services.ai_provider_manager import AIRequest
    from app.main import ai_manager
    
    request = AIRequest(messages=messages, task_type=TaskType.GENERAL)
    response = await ai_manager.generate(request)

Both patterns are supported! The old providers still work,
but the new system adds intelligence on top.
"""


print("✅ Integration guide complete!")
print("See inline comments for step-by-step integration instructions.")
