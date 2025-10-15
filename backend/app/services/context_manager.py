"""
Context Manager - Token counting and context window optimization
Manages context length and optimizes message history
"""
from typing import List, Dict
from dataclasses import dataclass
import tiktoken
import logging

logger = logging.getLogger(__name__)


@dataclass
class ContextWindow:
    """Context window information"""
    total_tokens: int
    max_tokens: int
    remaining_tokens: int
    messages_count: int
    truncated: bool = False


class ContextManager:
    """
    Manage context length and optimize token usage
    
    Features:
    - Accurate token counting
    - Message history optimization
    - Context window management
    - Automatic truncation strategies
    - Model-specific token limits
    """
    
    def __init__(self):
        """Initialize context manager"""
        # Token encoders for different models
        self.encoders = {}
        
        # Model context limits
        self.context_limits = {
            "gpt-4": 8192,
            "gpt-4-turbo-preview": 128000,
            "gpt-3.5-turbo": 16385,
            "claude-3-5-sonnet-20240620": 200000,
            "claude-3-haiku-20240307": 200000,
            "gemini-pro": 30720,
            "gemini-flash": 30720
        }
        
        # Default encoder
        try:
            self.default_encoder = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Could not load tiktoken encoder: {e}")
            self.default_encoder = None
        
        logger.info("ContextManager initialized")
    
    def estimate_tokens(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4"
    ) -> int:
        """
        Estimate token count for messages
        
        Args:
            messages: List of message dicts
            model: Model name for accurate counting
            
        Returns:
            Estimated token count
        """
        if not messages:
            return 0
        
        # Get encoder for model
        encoder = self._get_encoder(model)
        
        if not encoder:
            # Fallback: rough estimation
            return self._estimate_tokens_fallback(messages)
        
        # Count tokens accurately
        total_tokens = 0
        
        for message in messages:
            # Message overhead tokens
            total_tokens += 4  # Every message has overhead
            
            # Role tokens
            role = message.get("role", "")
            if role:
                total_tokens += len(encoder.encode(role))
            
            # Content tokens
            content = message.get("content", "")
            if content:
                total_tokens += len(encoder.encode(content))
        
        # Completion overhead
        total_tokens += 2
        
        return total_tokens
    
    def _estimate_tokens_fallback(self, messages: List[Dict[str, str]]) -> int:
        """Fallback token estimation without tiktoken"""
        total_chars = sum(
            len(msg.get("content", "")) + len(msg.get("role", ""))
            for msg in messages
        )
        # Rough estimation: 1 token ≈ 4 characters
        return total_chars // 4 + len(messages) * 4
    
    def _get_encoder(self, model: str):
        """Get token encoder for model"""
        if model in self.encoders:
            return self.encoders[model]
        
        if not self.default_encoder:
            return None
        
        # Try to get model-specific encoder
        try:
            if "gpt-4" in model or "gpt-3.5" in model:
                encoder = tiktoken.encoding_for_model(model)
            else:
                encoder = self.default_encoder
            
            self.encoders[model] = encoder
            return encoder
            
        except Exception as e:
            logger.warning(f"Could not get encoder for {model}: {e}")
            return self.default_encoder
    
    def get_context_window(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        max_completion_tokens: int = 2000
    ) -> ContextWindow:
        """
        Get context window information
        
        Args:
            messages: Message history
            model: Model name
            max_completion_tokens: Tokens reserved for completion
            
        Returns:
            Context window details
        """
        total_tokens = self.estimate_tokens(messages, model)
        max_tokens = self.context_limits.get(model, 8192)
        remaining = max_tokens - total_tokens - max_completion_tokens
        
        return ContextWindow(
            total_tokens=total_tokens,
            max_tokens=max_tokens,
            remaining_tokens=max(0, remaining),
            messages_count=len(messages),
            truncated=remaining < 0
        )
    
    async def optimize_messages(
        self,
        messages: List[Dict[str, str]],
        max_completion_tokens: int = 2000,
        model: str = "gpt-4",
        strategy: str = "recent"
    ) -> List[Dict[str, str]]:
        """
        Optimize message history to fit context window
        
        Args:
            messages: Original messages
            max_completion_tokens: Tokens to reserve for completion
            model: Model name
            strategy: Optimization strategy ("recent", "summarize", "smart")
            
        Returns:
            Optimized messages that fit context window
        """
        context = self.get_context_window(messages, model, max_completion_tokens)
        
        # If fits, return as-is
        if not context.truncated:
            return messages
        
        logger.info(
            f"Context window exceeded ({context.total_tokens} > {context.max_tokens}), "
            f"applying {strategy} strategy"
        )
        
        if strategy == "recent":
            return await self._optimize_recent(messages, model, max_completion_tokens)
        elif strategy == "summarize":
            return await self._optimize_summarize(messages, model, max_completion_tokens)
        elif strategy == "smart":
            return await self._optimize_smart(messages, model, max_completion_tokens)
        else:
            return await self._optimize_recent(messages, model, max_completion_tokens)
    
    async def _optimize_recent(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_completion_tokens: int
    ) -> List[Dict[str, str]]:
        """Keep most recent messages that fit"""
        max_tokens = self.context_limits.get(model, 8192)
        target_tokens = max_tokens - max_completion_tokens
        
        # Always keep system message if present
        system_messages = [m for m in messages if m.get("role") == "system"]
        other_messages = [m for m in messages if m.get("role") != "system"]
        
        # Count system tokens
        system_tokens = self.estimate_tokens(system_messages, model)
        available_tokens = target_tokens - system_tokens
        
        # Add messages from end until we hit limit
        optimized = []
        current_tokens = 0
        
        for message in reversed(other_messages):
            msg_tokens = self.estimate_tokens([message], model)
            
            if current_tokens + msg_tokens <= available_tokens:
                optimized.insert(0, message)
                current_tokens += msg_tokens
            else:
                break
        
        result = system_messages + optimized
        
        logger.info(
            f"Optimized from {len(messages)} to {len(result)} messages "
            f"({self.estimate_tokens(result, model)} tokens)"
        )
        
        return result
    
    async def _optimize_summarize(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_completion_tokens: int
    ) -> List[Dict[str, str]]:
        """Summarize old messages"""
        # Keep system and last N messages
        keep_count = 5
        
        system_messages = [m for m in messages if m.get("role") == "system"]
        other_messages = [m for m in messages if m.get("role") != "system"]
        
        if len(other_messages) <= keep_count:
            return messages
        
        # Messages to summarize
        to_summarize = other_messages[:-keep_count]
        to_keep = other_messages[-keep_count:]
        
        # Create summary message
        summary_content = "Previous conversation summary:\n\n"
        for msg in to_summarize:
            role = msg.get("role", "")
            content = msg.get("content", "")
            summary_content += f"{role}: {content[:100]}...\n"
        
        summary_message = {
            "role": "system",
            "content": summary_content
        }
        
        return system_messages + [summary_message] + to_keep
    
    async def _optimize_smart(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_completion_tokens: int
    ) -> List[Dict[str, str]]:
        """Smart optimization - keep important messages"""
        # Prioritize:
        # 1. System messages (always keep)
        # 2. Recent messages (last 5)
        # 3. Messages with code blocks
        # 4. Long messages (likely important)
        
        system_messages = [m for m in messages if m.get("role") == "system"]
        other_messages = [m for m in messages if m.get("role") != "system"]
        
        if len(other_messages) <= 5:
            return messages
        
        # Always keep recent messages
        recent = other_messages[-5:]
        older = other_messages[:-5]
        
        # Score older messages
        scored = []
        for msg in older:
            content = msg.get("content", "")
            score = 0
            
            # Code blocks are important
            if "```" in content:
                score += 10
            
            # Long messages likely important
            if len(content) > 500:
                score += 5
            
            # Questions are important
            if "?" in content:
                score += 3
            
            scored.append((score, msg))
        
        # Sort by score and keep top messages
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # Keep adding messages until we hit token limit
        max_tokens = self.context_limits.get(model, 8192)
        target_tokens = max_tokens - max_completion_tokens
        
        kept_older = []
        current_tokens = self.estimate_tokens(system_messages + recent, model)
        
        for score, msg in scored:
            msg_tokens = self.estimate_tokens([msg], model)
            if current_tokens + msg_tokens <= target_tokens:
                kept_older.append(msg)
                current_tokens += msg_tokens
            else:
                break
        
        # Maintain chronological order
        kept_older.sort(key=lambda m: older.index(m))
        
        return system_messages + kept_older + recent
    
    def get_model_limit(self, model: str) -> int:
        """Get context limit for model"""
        return self.context_limits.get(model, 8192)
    
    def can_fit(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_completion_tokens: int = 2000
    ) -> bool:
        """Check if messages fit in context window"""
        tokens = self.estimate_tokens(messages, model)
        limit = self.get_model_limit(model)
        return tokens + max_completion_tokens <= limit
