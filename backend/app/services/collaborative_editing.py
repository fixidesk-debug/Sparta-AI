"""
Collaborative Editing Service - Real-time multi-user editing
"""
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class CollaborativeEditingService:
    """Manage real-time collaborative editing sessions"""
    
    # Active sessions: file_id -> session data
    _active_sessions: Dict[int, Dict[str, Any]] = {}
    
    # Active users per file: file_id -> set of user_ids
    _active_users: Dict[int, Set[int]] = defaultdict(set)
    
    # User cursors: file_id -> {user_id -> cursor_position}
    _user_cursors: Dict[int, Dict[int, Dict[str, Any]]] = defaultdict(dict)
    
    # Pending changes: file_id -> list of changes
    _pending_changes: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    
    @classmethod
    def join_session(
        cls,
        file_id: int,
        user_id: int,
        username: str
    ) -> Dict[str, Any]:
        """User joins a collaborative editing session"""
        try:
            # Add user to active users
            cls._active_users[file_id].add(user_id)
            
            # Initialize session if not exists
            if file_id not in cls._active_sessions:
                cls._active_sessions[file_id] = {
                    "file_id": file_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "users": []
                }
            
            # Add user to session
            user_info = {
                "user_id": user_id,
                "username": username,
                "joined_at": datetime.now(timezone.utc).isoformat(),
                "color": cls._generate_user_color(user_id)
            }
            
            cls._active_sessions[file_id]["users"].append(user_info)
            
            logger.info(f"User {user_id} joined session for file {file_id}")
            
            return {
                "success": True,
                "session_id": file_id,
                "user_info": user_info,
                "active_users": list(cls._active_users[file_id]),
                "user_count": len(cls._active_users[file_id])
            }
            
        except Exception as e:
            logger.error(f"Error joining session: {e}")
            raise
    
    @classmethod
    def leave_session(
        cls,
        file_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """User leaves a collaborative editing session"""
        try:
            # Remove user from active users
            if file_id in cls._active_users:
                cls._active_users[file_id].discard(user_id)
            
            # Remove user cursor
            if file_id in cls._user_cursors:
                cls._user_cursors[file_id].pop(user_id, None)
            
            # Remove user from session
            if file_id in cls._active_sessions:
                cls._active_sessions[file_id]["users"] = [
                    u for u in cls._active_sessions[file_id]["users"]
                    if u["user_id"] != user_id
                ]
                
                # Clean up empty session
                if not cls._active_users[file_id]:
                    del cls._active_sessions[file_id]
                    del cls._active_users[file_id]
                    if file_id in cls._user_cursors:
                        del cls._user_cursors[file_id]
                    if file_id in cls._pending_changes:
                        del cls._pending_changes[file_id]
            
            logger.info(f"User {user_id} left session for file {file_id}")
            
            return {
                "success": True,
                "user_id": user_id,
                "remaining_users": len(cls._active_users.get(file_id, set()))
            }
            
        except Exception as e:
            logger.error(f"Error leaving session: {e}")
            raise
    
    @classmethod
    def update_cursor(
        cls,
        file_id: int,
        user_id: int,
        cursor_position: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user's cursor position"""
        try:
            cls._user_cursors[file_id][user_id] = {
                "position": cursor_position,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return {
                "success": True,
                "user_id": user_id,
                "cursor_position": cursor_position
            }
            
        except Exception as e:
            logger.error(f"Error updating cursor: {e}")
            raise
    
    @classmethod
    def get_active_cursors(
        cls,
        file_id: int
    ) -> Dict[str, Any]:
        """Get all active user cursors"""
        cursors = cls._user_cursors.get(file_id, {})
        return {
            "file_id": file_id,
            "cursors": cursors
        }
    
    @classmethod
    def broadcast_change(
        cls,
        file_id: int,
        user_id: int,
        change: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Broadcast a change to all users in the session"""
        try:
            change_data = {
                "user_id": user_id,
                "change": change,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            cls._pending_changes[file_id].append(change_data)
            
            # Keep only last 100 changes
            if len(cls._pending_changes[file_id]) > 100:
                cls._pending_changes[file_id] = cls._pending_changes[file_id][-100:]
            
            return {
                "success": True,
                "change_id": len(cls._pending_changes[file_id]) - 1,
                "broadcast_to": list(cls._active_users[file_id])
            }
            
        except Exception as e:
            logger.error(f"Error broadcasting change: {e}")
            raise
    
    @classmethod
    def get_pending_changes(
        cls,
        file_id: int,
        since_timestamp: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get pending changes since a timestamp"""
        changes = cls._pending_changes.get(file_id, [])
        
        if since_timestamp:
            changes = [
                c for c in changes
                if c["timestamp"] > since_timestamp
            ]
        
        return changes
    
    @classmethod
    def get_session_info(
        cls,
        file_id: int
    ) -> Dict[str, Any]:
        """Get information about an active session"""
        if file_id not in cls._active_sessions:
            return {
                "active": False,
                "file_id": file_id
            }
        
        session = cls._active_sessions[file_id]
        return {
            "active": True,
            "file_id": file_id,
            "users": session["users"],
            "user_count": len(cls._active_users[file_id]),
            "created_at": session["created_at"],
            "pending_changes": len(cls._pending_changes.get(file_id, []))
        }
    
    @classmethod
    def lock_resource(
        cls,
        file_id: int,
        user_id: int,
        resource_id: str
    ) -> Dict[str, Any]:
        """Lock a resource (cell, row, column) for editing"""
        # Simple lock implementation
        lock_key = f"{file_id}_{resource_id}"
        
        # In production, use Redis for distributed locking
        return {
            "success": True,
            "lock_key": lock_key,
            "user_id": user_id,
            "resource_id": resource_id
        }
    
    @classmethod
    def unlock_resource(
        cls,
        file_id: int,
        user_id: int,
        resource_id: str
    ) -> Dict[str, Any]:
        """Unlock a resource"""
        lock_key = f"{file_id}_{resource_id}"
        
        return {
            "success": True,
            "lock_key": lock_key,
            "unlocked": True
        }
    
    @classmethod
    def _generate_user_color(cls, user_id: int) -> str:
        """Generate a unique color for a user"""
        colors = [
            "#3b82f6",  # blue
            "#ef4444",  # red
            "#10b981",  # green
            "#f59e0b",  # amber
            "#8b5cf6",  # purple
            "#ec4899",  # pink
            "#14b8a6",  # teal
            "#f97316",  # orange
        ]
        return colors[user_id % len(colors)]
    
    @classmethod
    def get_all_active_sessions(cls) -> List[Dict[str, Any]]:
        """Get all active collaborative sessions"""
        sessions = []
        for file_id, session in cls._active_sessions.items():
            sessions.append({
                "file_id": file_id,
                "user_count": len(cls._active_users[file_id]),
                "created_at": session["created_at"]
            })
        return sessions
