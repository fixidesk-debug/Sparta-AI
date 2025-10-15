"""
WebSocket Manager for Sparta AI

Manages WebSocket connections, message routing, authentication, and real-time communication.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Set, Any
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum

from fastapi import WebSocket
from starlette.websockets import WebSocketState


logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types"""
    # Chat messages
    CHAT_MESSAGE = "chat_message"
    CHAT_RESPONSE = "chat_response"
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"
    
    # Code execution
    CODE_EXECUTE = "code_execute"
    CODE_STATUS = "code_status"
    CODE_OUTPUT = "code_output"
    CODE_COMPLETE = "code_complete"
    CODE_ERROR = "code_error"
    
    # File operations
    FILE_UPLOAD_START = "file_upload_start"
    FILE_UPLOAD_PROGRESS = "file_upload_progress"
    FILE_UPLOAD_COMPLETE = "file_upload_complete"
    FILE_UPLOAD_ERROR = "file_upload_error"
    
    # Collaboration
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    USER_LIST = "user_list"
    CURSOR_MOVE = "cursor_move"
    
    # System
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    SYSTEM = "system"
    DISCONNECT = "disconnect"


class ConnectionStatus(str, Enum):
    """Connection status states"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection"""
    websocket: WebSocket
    user_id: str
    session_id: str
    connected_at: float = field(default_factory=time.time)
    last_ping: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    status: ConnectionStatus = ConnectionStatus.CONNECTED
    message_count: int = 0
    rate_limit_tokens: float = 100.0
    rooms: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """WebSocket message structure"""
    type: MessageType
    data: Dict[str, Any]
    sender_id: Optional[str] = None
    room: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    message_id: Optional[str] = None


class RateLimiter:
    """Token bucket rate limiter for WebSocket messages"""
    
    def __init__(
        self,
        rate: float = 10.0,  # messages per second
        burst: float = 20.0,  # max burst size
    ):
        self.rate = rate
        self.burst = burst
    
    def check_limit(self, connection: ConnectionInfo) -> bool:
        """Check if message is allowed under rate limit"""
        now = time.time()
        elapsed = now - connection.last_activity
        
        # Refill tokens based on elapsed time
        connection.rate_limit_tokens = min(
            self.burst,
            connection.rate_limit_tokens + elapsed * self.rate
        )
        
        if connection.rate_limit_tokens >= 1.0:
            connection.rate_limit_tokens -= 1.0
            connection.last_activity = now
            return True
        
        return False


class MessageQueue:
    """Queue for offline message persistence"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.queues: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_size))
    
    def add_message(self, user_id: str, message: Dict[str, Any]) -> None:
        """Add message to user's queue"""
        self.queues[user_id].append({
            **message,
            "queued_at": time.time()
        })
    
    def get_messages(self, user_id: str) -> List[Dict[str, Any]]:
        """Get and clear user's queued messages"""
        messages = list(self.queues[user_id])
        self.queues[user_id].clear()
        return messages
    
    def clear_queue(self, user_id: str) -> None:
        """Clear user's message queue"""
        if user_id in self.queues:
            del self.queues[user_id]


class WebSocketManager:
    """
    Manages WebSocket connections and message routing
    """
    
    def __init__(
        self,
        ping_interval: int = 30,  # seconds
        connection_timeout: int = 300,  # seconds
        rate_limit_rate: float = 10.0,  # messages per second
        rate_limit_burst: float = 20.0,  # max burst
    ):
        # Connection storage
        self.active_connections: Dict[str, ConnectionInfo] = {}
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        self.room_connections: Dict[str, Set[str]] = defaultdict(set)
        
        # Message management
        self.message_queue = MessageQueue()
        self.rate_limiter = RateLimiter(rate_limit_rate, rate_limit_burst)
        
        # Settings
        self.ping_interval = ping_interval
        self.connection_timeout = connection_timeout
        
        # Statistics
        self.total_connections = 0
        self.total_messages = 0
        self.start_time = time.time()
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        session_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Accept and register a new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
            session_id: Session identifier
            metadata: Optional connection metadata
        
        Returns:
            Connection ID
        """
        await websocket.accept()
        
        # Generate connection ID
        connection_id = f"{user_id}:{session_id}:{int(time.time() * 1000)}"
        
        # Create connection info
        connection = ConnectionInfo(
            websocket=websocket,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata or {},
        )
        
        # Store connection
        self.active_connections[connection_id] = connection
        self.user_connections[user_id].add(connection_id)
        
        # Update statistics
        self.total_connections += 1
        
        # Send queued messages
        queued_messages = self.message_queue.get_messages(user_id)
        for message in queued_messages:
            await self.send_to_connection(connection_id, message)
        
        # Notify about connection
        await self.send_to_connection(connection_id, {
            "type": MessageType.SYSTEM,
            "data": {
                "message": "Connected successfully",
                "connection_id": connection_id,
                "queued_messages": len(queued_messages)
            }
        })
        
        logger.info(
            f"WebSocket connected: {connection_id} "
            f"(user: {user_id}, total: {len(self.active_connections)})"
        )
        
        return connection_id
    
    async def disconnect(self, connection_id: str) -> None:
        """
        Disconnect and clean up a WebSocket connection
        
        Args:
            connection_id: Connection identifier
        """
        if connection_id not in self.active_connections:
            return
        
        connection = self.active_connections[connection_id]
        connection.status = ConnectionStatus.DISCONNECTING
        
        # Remove from rooms
        for room in list(connection.rooms):
            await self.leave_room(connection_id, room)
        
        # Remove from user connections
        self.user_connections[connection.user_id].discard(connection_id)
        if not self.user_connections[connection.user_id]:
            del self.user_connections[connection.user_id]
        
        # Close WebSocket
        if connection.websocket.client_state == WebSocketState.CONNECTED:
            try:
                await connection.websocket.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket {connection_id}: {e}")
        
        # Remove connection
        del self.active_connections[connection_id]
        
        logger.info(
            f"WebSocket disconnected: {connection_id} "
            f"(user: {connection.user_id}, total: {len(self.active_connections)})"
        )
    
    async def send_to_connection(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        Send message to specific connection
        
        Args:
            connection_id: Target connection ID
            message: Message to send
        
        Returns:
            True if sent successfully
        """
        if connection_id not in self.active_connections:
            return False
        
        connection = self.active_connections[connection_id]
        
        if connection.websocket.client_state != WebSocketState.CONNECTED:
            return False
        
        try:
            await connection.websocket.send_json({
                **message,
                "timestamp": time.time()
            })
            connection.message_count += 1
            self.total_messages += 1
            return True
        except Exception as e:
            logger.error(f"Error sending to {connection_id}: {e}")
            await self.disconnect(connection_id)
            return False
    
    async def send_to_user(
        self,
        user_id: str,
        message: Dict[str, Any],
        exclude_connection: Optional[str] = None
    ) -> int:
        """
        Send message to all connections of a user
        
        Args:
            user_id: Target user ID
            message: Message to send
            exclude_connection: Connection ID to exclude
        
        Returns:
            Number of connections message was sent to
        """
        if user_id not in self.user_connections:
            # Queue message for offline user
            self.message_queue.add_message(user_id, message)
            return 0
        
        sent_count = 0
        for connection_id in list(self.user_connections[user_id]):
            if connection_id == exclude_connection:
                continue
            
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def send_to_room(
        self,
        room: str,
        message: Dict[str, Any],
        exclude_connection: Optional[str] = None
    ) -> int:
        """
        Broadcast message to all connections in a room
        
        Args:
            room: Room name
            message: Message to send
            exclude_connection: Connection ID to exclude
        
        Returns:
            Number of connections message was sent to
        """
        if room not in self.room_connections:
            return 0
        
        sent_count = 0
        for connection_id in list(self.room_connections[room]):
            if connection_id == exclude_connection:
                continue
            
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast(
        self,
        message: Dict[str, Any],
        exclude_connection: Optional[str] = None
    ) -> int:
        """
        Broadcast message to all connections
        
        Args:
            message: Message to send
            exclude_connection: Connection ID to exclude
        
        Returns:
            Number of connections message was sent to
        """
        sent_count = 0
        for connection_id in list(self.active_connections.keys()):
            if connection_id == exclude_connection:
                continue
            
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def join_room(self, connection_id: str, room: str) -> bool:
        """
        Add connection to a room
        
        Args:
            connection_id: Connection ID
            room: Room name
        
        Returns:
            True if joined successfully
        """
        if connection_id not in self.active_connections:
            return False
        
        connection = self.active_connections[connection_id]
        connection.rooms.add(room)
        self.room_connections[room].add(connection_id)
        
        # Notify room members
        await self.send_to_room(room, {
            "type": MessageType.USER_JOINED,
            "data": {
                "user_id": connection.user_id,
                "room": room,
                "member_count": len(self.room_connections[room])
            }
        }, exclude_connection=connection_id)
        
        logger.info(f"Connection {connection_id} joined room {room}")
        return True
    
    async def leave_room(self, connection_id: str, room: str) -> bool:
        """
        Remove connection from a room
        
        Args:
            connection_id: Connection ID
            room: Room name
        
        Returns:
            True if left successfully
        """
        if connection_id not in self.active_connections:
            return False
        
        connection = self.active_connections[connection_id]
        connection.rooms.discard(room)
        self.room_connections[room].discard(connection_id)
        
        # Clean up empty rooms
        if not self.room_connections[room]:
            del self.room_connections[room]
        else:
            # Notify remaining room members
            await self.send_to_room(room, {
                "type": MessageType.USER_LEFT,
                "data": {
                    "user_id": connection.user_id,
                    "room": room,
                    "member_count": len(self.room_connections[room])
                }
            })
        
        logger.info(f"Connection {connection_id} left room {room}")
        return True
    
    def check_rate_limit(self, connection_id: str) -> bool:
        """
        Check if connection is within rate limits
        
        Args:
            connection_id: Connection ID
        
        Returns:
            True if allowed
        """
        if connection_id not in self.active_connections:
            return False
        
        connection = self.active_connections[connection_id]
        return self.rate_limiter.check_limit(connection)
    
    async def handle_message(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> None:
        """
        Handle incoming WebSocket message
        
        Args:
            connection_id: Source connection ID
            message: Received message
        """
        if connection_id not in self.active_connections:
            return
        
        # Check rate limit
        if not self.check_rate_limit(connection_id):
            await self.send_to_connection(connection_id, {
                "type": MessageType.ERROR,
                "data": {
                    "error": "Rate limit exceeded",
                    "message": "Too many messages. Please slow down."
                }
            })
            return
        
        connection = self.active_connections[connection_id]
        message_type = message.get("type")
        
        # Handle ping/pong
        if message_type == MessageType.PING:
            connection.last_ping = time.time()
            await self.send_to_connection(connection_id, {
                "type": MessageType.PONG,
                "data": {"timestamp": time.time()}
            })
            return
        
        # Add metadata
        message["sender_id"] = connection.user_id
        message["connection_id"] = connection_id
        
        # Route message based on type
        # (This is where you'd integrate with your business logic)
        logger.debug(
            f"Received {message_type} from {connection_id}: "
            f"{json.dumps(message, default=str)[:100]}"
        )
    
    async def start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        if self._ping_task is None or self._ping_task.done():
            self._ping_task = asyncio.create_task(self._ping_loop())
        
        logger.info("WebSocket background tasks started")
    
    async def stop_background_tasks(self) -> None:
        """Stop background maintenance tasks"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self._ping_task:
            self._ping_task.cancel()
            try:
                await self._ping_task
            except asyncio.CancelledError:
                pass
        
        logger.info("WebSocket background tasks stopped")
    
    async def _cleanup_loop(self) -> None:
        """Background task to clean up stale connections"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                now = time.time()
                stale_connections = []
                
                for connection_id, connection in self.active_connections.items():
                    # Check for timeout
                    if now - connection.last_ping > self.connection_timeout:
                        stale_connections.append(connection_id)
                
                # Disconnect stale connections
                for connection_id in stale_connections:
                    logger.warning(f"Disconnecting stale connection: {connection_id}")
                    await self.disconnect(connection_id)
                
                if stale_connections:
                    logger.info(f"Cleaned up {len(stale_connections)} stale connections")
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _ping_loop(self) -> None:
        """Background task to ping all connections"""
        while True:
            try:
                await asyncio.sleep(self.ping_interval)
                
                for connection_id in list(self.active_connections.keys()):
                    await self.send_to_connection(connection_id, {
                        "type": MessageType.PING,
                        "data": {"timestamp": time.time()}
                    })
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ping loop: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        uptime = time.time() - self.start_time
        
        return {
            "active_connections": len(self.active_connections),
            "active_users": len(self.user_connections),
            "active_rooms": len(self.room_connections),
            "total_connections": self.total_connections,
            "total_messages": self.total_messages,
            "uptime_seconds": uptime,
            "messages_per_second": self.total_messages / uptime if uptime > 0 else 0,
        }
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific connection"""
        if connection_id not in self.active_connections:
            return None
        
        connection = self.active_connections[connection_id]
        return {
            "connection_id": connection_id,
            "user_id": connection.user_id,
            "session_id": connection.session_id,
            "connected_at": connection.connected_at,
            "last_ping": connection.last_ping,
            "last_activity": connection.last_activity,
            "status": connection.status,
            "message_count": connection.message_count,
            "rooms": list(connection.rooms),
            "metadata": connection.metadata,
        }


# Global WebSocket manager instance
ws_manager = WebSocketManager()
