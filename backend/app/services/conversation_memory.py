"""
Conversation Memory Management
Manages conversation history for multi-turn interactions
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import deque
import logging
import json

logger = logging.getLogger(__name__)


class Message:
    """Represents a single conversation message"""
    
    def __init__(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize message
        
        Args:
            role: Message role ('system', 'user', 'assistant')
            content: Message content
            metadata: Optional metadata (file_id, code, results, etc.)
            timestamp: Message timestamp (defaults to now)
        """
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'role': self.role,
            'content': self.content,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }
    
    def to_chat_format(self) -> Dict[str, str]:
        """Convert to chat API format (role + content only)"""
        return {
            'role': self.role,
            'content': self.content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            role=data['role'],
            content=data['content'],
            metadata=data.get('metadata', {}),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else None
        )


class ConversationMemory:
    """Manages conversation history for a single session"""
    
    def __init__(self, max_history: int = 50, max_tokens: int = 8000):
        """
        Initialize conversation memory
        
        Args:
            max_history: Maximum number of messages to keep
            max_tokens: Approximate max tokens for context (for pruning)
        """
        self.messages: deque = deque(maxlen=max_history)
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.system_message: Optional[Message] = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def set_system_message(self, content: str):
        """
        Set the system message (context/instructions)
        
        Args:
            content: System message content
        """
        self.system_message = Message(role='system', content=content)
        self.logger.info("System message set")
    
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add user message
        
        Args:
            content: User message content
            metadata: Optional metadata
        """
        message = Message(role='user', content=content, metadata=metadata)
        self.messages.append(message)
        self.logger.info(f"Added user message: {content[:50]}...")
    
    def add_assistant_message(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add assistant message
        
        Args:
            content: Assistant message content
            metadata: Optional metadata (generated code, results, etc.)
        """
        message = Message(role='assistant', content=content, metadata=metadata)
        self.messages.append(message)
        self.logger.info(f"Added assistant message: {content[:50]}...")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add message with any role
        
        Args:
            role: Message role
            content: Message content
            metadata: Optional metadata
        """
        if role == 'system':
            self.set_system_message(content)
        else:
            message = Message(role=role, content=content, metadata=metadata)
            self.messages.append(message)
            self.logger.info(f"Added {role} message: {content[:50]}...")
    
    def get_messages(self, limit: Optional[int] = None, include_system: bool = True) -> List[Message]:
        """
        Get conversation messages
        
        Args:
            limit: Optional limit on number of messages (most recent)
            include_system: Whether to include system message
            
        Returns:
            List of Message objects
        """
        messages = []
        
        if include_system and self.system_message:
            messages.append(self.system_message)
        
        if limit:
            # Get last N messages
            messages.extend(list(self.messages)[-limit:])
        else:
            messages.extend(self.messages)
        
        return messages
    
    def get_chat_format(self, limit: Optional[int] = None, include_system: bool = True) -> List[Dict[str, str]]:
        """
        Get messages in chat API format
        
        Args:
            limit: Optional limit on number of messages
            include_system: Whether to include system message
            
        Returns:
            List of dicts with 'role' and 'content'
        """
        messages = self.get_messages(limit=limit, include_system=include_system)
        return [msg.to_chat_format() for msg in messages]
    
    def get_history_text(self, limit: Optional[int] = None) -> str:
        """
        Get conversation history as formatted text
        
        Args:
            limit: Optional limit on number of messages
            
        Returns:
            Formatted conversation history
        """
        messages = self.get_messages(limit=limit, include_system=False)
        
        if not messages:
            return "No conversation history"
        
        history_lines = []
        for msg in messages:
            timestamp = msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            history_lines.append(f"[{timestamp}] {msg.role.upper()}: {msg.content}")
            
            # Include code if present in metadata
            if msg.metadata.get('code'):
                history_lines.append(f"  Generated Code:\n{msg.metadata['code']}")
            
            # Include results if present
            if msg.metadata.get('results'):
                history_lines.append(f"  Results: {msg.metadata['results']}")
        
        return "\n".join(history_lines)
    
    def get_last_code(self) -> Optional[str]:
        """
        Get the last generated code from conversation
        
        Returns:
            Last generated code or None
        """
        for msg in reversed(self.messages):
            if msg.role == 'assistant' and msg.metadata.get('code'):
                return msg.metadata['code']
        return None
    
    def get_last_results(self) -> Optional[str]:
        """
        Get the last execution results from conversation
        
        Returns:
            Last results or None
        """
        for msg in reversed(self.messages):
            if msg.metadata.get('results'):
                return msg.metadata['results']
        return None
    
    def get_context_summary(self, max_messages: int = 5) -> str:
        """
        Get a summary of recent conversation context
        
        Args:
            max_messages: Maximum messages to include in summary
            
        Returns:
            Context summary string
        """
        messages = list(self.messages)[-max_messages:]
        
        if not messages:
            return "No previous conversation"
        
        summary_parts = [f"Recent conversation ({len(messages)} messages):"]
        
        for msg in messages:
            content_preview = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            summary_parts.append(f"- {msg.role}: {content_preview}")
        
        # Add code context if available
        last_code = self.get_last_code()
        if last_code:
            code_preview = last_code[:100] + "..." if len(last_code) > 100 else last_code
            summary_parts.append(f"\nLast generated code:\n{code_preview}")
        
        return "\n".join(summary_parts)
    
    def estimate_tokens(self) -> int:
        """
        Estimate total tokens in conversation
        (Rough estimate: ~4 chars per token)
        
        Returns:
            Estimated token count
        """
        total_chars = 0
        
        if self.system_message:
            total_chars += len(self.system_message.content)
        
        for msg in self.messages:
            total_chars += len(msg.content)
        
        return total_chars // 4
    
    def prune_if_needed(self):
        """Prune old messages if token count exceeds limit"""
        estimated_tokens = self.estimate_tokens()
        
        if estimated_tokens > self.max_tokens:
            # Remove oldest messages (but keep last 10)
            messages_to_keep = max(10, len(self.messages) - 10)
            removed_count = len(self.messages) - messages_to_keep
            
            # Keep only recent messages
            self.messages = deque(list(self.messages)[-messages_to_keep:], maxlen=self.max_history)
            
            self.logger.info(f"Pruned {removed_count} old messages to stay under token limit")
    
    def clear(self):
        """Clear all messages (keeps system message)"""
        self.messages.clear()
        self.logger.info("Cleared conversation history")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert conversation to dictionary
        
        Returns:
            Dictionary representation
        """
        return {
            'system_message': self.system_message.to_dict() if self.system_message else None,
            'messages': [msg.to_dict() for msg in self.messages],
            'message_count': len(self.messages),
            'estimated_tokens': self.estimate_tokens()
        }
    
    def to_json(self) -> str:
        """
        Convert conversation to JSON string
        
        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], max_history: int = 50) -> 'ConversationMemory':
        """
        Create conversation memory from dictionary
        
        Args:
            data: Dictionary with conversation data
            max_history: Maximum history size
            
        Returns:
            ConversationMemory instance
        """
        memory = cls(max_history=max_history)
        
        if data.get('system_message'):
            memory.system_message = Message.from_dict(data['system_message'])
        
        for msg_data in data.get('messages', []):
            memory.messages.append(Message.from_dict(msg_data))
        
        return memory


class ConversationMemoryManager:
    """Manages multiple conversation memories for different sessions"""
    
    def __init__(self):
        """Initialize conversation memory manager"""
        self.memories: Dict[str, ConversationMemory] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_or_create(self, session_id: str, max_history: int = 50) -> ConversationMemory:
        """
        Get existing memory or create new one
        
        Args:
            session_id: Session identifier (e.g., user_id or chat_session_id)
            max_history: Maximum history size
            
        Returns:
            ConversationMemory instance
        """
        if session_id not in self.memories:
            self.memories[session_id] = ConversationMemory(max_history=max_history)
            self.logger.info(f"Created new conversation memory for session {session_id}")
        
        return self.memories[session_id]
    
    def get(self, session_id: str) -> Optional[ConversationMemory]:
        """
        Get existing memory
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationMemory instance or None
        """
        return self.memories.get(session_id)
    
    def remove(self, session_id: str):
        """
        Remove conversation memory
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.memories:
            del self.memories[session_id]
            self.logger.info(f"Removed conversation memory for session {session_id}")
    
    def clear_all(self):
        """Clear all conversation memories"""
        self.memories.clear()
        self.logger.info("Cleared all conversation memories")
    
    def cleanup_inactive(self, inactive_threshold: int = 3600):
        """
        Clean up inactive conversations
        
        Args:
            inactive_threshold: Seconds of inactivity before cleanup
        """
        now = datetime.utcnow()
        to_remove = []
        
        for session_id, memory in self.memories.items():
            if memory.messages:
                last_message = list(memory.messages)[-1]
                seconds_inactive = (now - last_message.timestamp).total_seconds()
                
                if seconds_inactive > inactive_threshold:
                    to_remove.append(session_id)
        
        for session_id in to_remove:
            self.remove(session_id)
        
        if to_remove:
            self.logger.info(f"Cleaned up {len(to_remove)} inactive conversations")


# Global conversation memory manager instance
conversation_memory_manager = ConversationMemoryManager()
