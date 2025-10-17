"""
WebSocket endpoint for real-time communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
import json
import logging
import uuid
from datetime import datetime, timezone

from app.db.session import get_db
from app.db.models import User, ChatSession, Query as QueryModel
from app.core.security import decode_access_token
from app.services.nlp import process_natural_language_query
from app.services.websocket_manager import ws_manager, MessageType

router = APIRouter()
logger = logging.getLogger(__name__)


# Legacy ConnectionManager for backwards compatibility
class ConnectionManager:
    """Manage WebSocket connections (legacy)"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a new WebSocket client"""
        await websocket.accept()
        # Generate a random connection id to avoid exposing user-supplied identifiers
        connection_id = uuid.uuid4().hex
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")
        return connection_id
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Disconnect a WebSocket client"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_message(self, connection_id: str, message: dict):
        """Send message to a specific connection"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {e}")


manager = ConnectionManager()


async def get_current_user_ws(
    token: str = Query(..., description="JWT authentication token"),
    db: Session = Depends(get_db)
) -> dict:
    """
    WebSocket authentication dependency
    
    Args:
        token: JWT token from query parameter
        db: Database session
    
    Returns:
        User information dictionary
    
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        # Extract user info from token
        user_id = payload.get("user_id", payload.get("sub"))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        return {
            "user_id": str(user_id),
            "session_id": payload.get("session_id", str(user_id)),
            "username": payload.get("username", payload.get("email", "anonymous"))
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")


async def get_current_user_ws_legacy(token: str, db: Session) -> User:
    """Get current user from WebSocket token (legacy)"""
    payload = decode_access_token(token)
    if payload is None:
        raise ValueError("Invalid token")
    
    email = payload.get("sub")
    if email is None:
        raise ValueError("Invalid token payload")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise ValueError("User not found")
    
    return user


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
    room: Optional[str] = Query(None, description="Room to join"),
    db: Session = Depends(get_db)
):
    """
    Main WebSocket endpoint for real-time communication
    
    Query Parameters:
        token: JWT authentication token
        room: Optional room to join automatically
    
    Message Format:
        {
            "type": "message_type",
            "data": { ... },
            "room": "optional_room"
        }
    
    Supported Message Types:
        - chat_message: Send chat message
        - code_execute: Execute code
        - file_upload_start: Start file upload
        - typing_start/stop: Typing indicators
        - cursor_move: Cursor position (collaboration)
        - ping: Keep-alive ping
    
    Response Format:
        {
            "type": "message_type",
            "data": { ... },
            "timestamp": 1234567890.123,
            "sender_id": "user_id"
        }
    """
    connection_id = None
    
    try:
        # Authenticate user
        user_info = await get_current_user_ws(token, db)
        user_id = user_info["user_id"]
        session_id = user_info["session_id"]
        username = user_info["username"]
        
        # Connect to WebSocket manager
        connection_id = await ws_manager.connect(
            websocket=websocket,
            user_id=user_id,
            session_id=session_id,
            metadata={
                "username": username,
                "initial_room": room
            }
        )
        
        # Join initial room if specified
        if room:
            await ws_manager.join_room(connection_id, room)
        
        # Send welcome message
        await ws_manager.send_to_connection(connection_id, {
            "type": MessageType.SYSTEM,
            "data": {
                "message": f"Welcome {username}!",
                "connection_id": connection_id,
                "user_id": user_id
            }
        })
        
        # Main message loop
        while True:
            # Receive message
            try:
                message = await websocket.receive_json()
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from {connection_id}: {e}")
                await ws_manager.send_to_connection(connection_id, {
                    "type": MessageType.ERROR,
                    "data": {
                        "error": "Invalid JSON",
                        "message": "Message must be valid JSON"
                    }
                })
                continue
            
            # Validate message structure
            if not isinstance(message, dict) or "type" not in message:
                await ws_manager.send_to_connection(connection_id, {
                    "type": MessageType.ERROR,
                    "data": {
                        "error": "Invalid message format",
                        "message": "Message must have 'type' field"
                    }
                })
                continue
            
            message_type = message.get("type")
            message_data = message.get("data", {})
            target_room = message.get("room")
            
            # Handle different message types
            try:
                if message_type == MessageType.CHAT_MESSAGE:
                    await handle_chat_message(
                        connection_id, user_id, username, message_data, target_room, db
                    )
                
                elif message_type == MessageType.TYPING_START:
                    await handle_typing_indicator(
                        connection_id, user_id, username, True, target_room
                    )
                
                elif message_type == MessageType.TYPING_STOP:
                    await handle_typing_indicator(
                        connection_id, user_id, username, False, target_room
                    )
                
                elif message_type == MessageType.CODE_EXECUTE:
                    await handle_code_execution(
                        connection_id, user_id, message_data
                    )
                
                elif message_type == MessageType.FILE_UPLOAD_START:
                    await handle_file_upload_start(
                        connection_id, user_id, message_data
                    )
                
                elif message_type == MessageType.CURSOR_MOVE:
                    await handle_cursor_move(
                        connection_id, user_id, username, message_data, target_room
                    )
                
                elif message_type == "join_room":
                    room_name = message_data.get("room")
                    if room_name:
                        await ws_manager.join_room(connection_id, room_name)
                        await ws_manager.send_to_connection(connection_id, {
                            "type": MessageType.SYSTEM,
                            "data": {
                                "message": f"Joined room: {room_name}",
                                "room": room_name
                            }
                        })
                
                elif message_type == "leave_room":
                    room_name = message_data.get("room")
                    if room_name:
                        await ws_manager.leave_room(connection_id, room_name)
                        await ws_manager.send_to_connection(connection_id, {
                            "type": MessageType.SYSTEM,
                            "data": {
                                "message": f"Left room: {room_name}",
                                "room": room_name
                            }
                        })
                
                elif message_type == MessageType.PING:
                    # Handled by manager
                    await ws_manager.handle_message(connection_id, message)
                
                else:
                    # Unknown message type
                    await ws_manager.send_to_connection(connection_id, {
                        "type": MessageType.ERROR,
                        "data": {
                            "error": "Unknown message type",
                            "message": f"Message type '{message_type}' is not supported"
                        }
                    })
            
            except Exception as e:
                logger.error(
                    f"Error handling message type {message_type} "
                    f"from {connection_id}: {e}",
                    exc_info=True
                )
                await ws_manager.send_to_connection(connection_id, {
                    "type": MessageType.ERROR,
                    "data": {
                        "error": "Message handling error",
                        "message": str(e)
                    }
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {connection_id}")
    
    except HTTPException as e:
        logger.warning(f"WebSocket authentication failed: {e.detail}")
        try:
            await websocket.close(code=1008, reason=e.detail)
        except Exception as close_err:
            logger.warning(f"Failed to close websocket after HTTPException: {close_err}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception as close_err:
            logger.warning(f"Failed to close websocket after internal error: {close_err}", exc_info=True)
    
    finally:
        # Clean up connection
        if connection_id:
            await ws_manager.disconnect(connection_id)


async def handle_chat_message(
    connection_id: str,
    user_id: str,
    username: str,
    data: dict,
    room: Optional[str],
    db: Session
) -> None:
    """Handle chat message"""
    message_text = data.get("message", "").strip()
    chat_session_id = data.get("session_id")
    file_id = data.get("file_id")
    
    if not message_text:
        await ws_manager.send_to_connection(connection_id, {
            "type": MessageType.ERROR,
            "data": {
                "error": "Empty message",
                "message": "Message cannot be empty"
            }
        })
        return
    
    # Process with NLP if requested
    if data.get("process_nlp", False):
        try:
            # Convert user_id to int for NLP processing
            try:
                user_id_int = int(user_id)
            except (ValueError, TypeError):
                user_id_int = 0  # Use default for invalid user_id
            
            response_text = await process_natural_language_query(
                message_text,
                file_id,
                user_id_int,
                db
            )
            
            # Save to database if chat session provided
            if chat_session_id:
                db_query = QueryModel(
                    user_id=user_id,
                    file_id=file_id,
                    chat_session_id=chat_session_id,
                    query_text=message_text,
                    response=response_text,
                    execution_status="success"
                )
                db.add(db_query)
                db.commit()
                db.refresh(db_query)
            
            # Send AI response
            await ws_manager.send_to_connection(connection_id, {
                "type": MessageType.CHAT_RESPONSE,
                "data": {
                    "message": response_text,
                    "user_id": "ai_assistant",
                    "username": "AI Assistant",
                    "query_id": db_query.id if chat_session_id else None
                }
            })
        except Exception as e:
            logger.error(f"Error processing NLP query: {e}")
            await ws_manager.send_to_connection(connection_id, {
                "type": MessageType.ERROR,
                "data": {
                    "error": "Processing error",
                    "message": str(e)
                }
            })
        return
    
    # Regular chat message - broadcast to room
    response = {
        "type": MessageType.CHAT_MESSAGE,
        "data": {
            "message": message_text,
            "user_id": user_id,
            "username": username,
            "room": room
        }
    }
    
    if room:
        await ws_manager.send_to_room(room, response, exclude_connection=connection_id)
    else:
        await ws_manager.send_to_connection(connection_id, response)
    
    logger.info(f"Chat message from {username} in room {room}: {message_text[:50]}")


async def handle_typing_indicator(
    connection_id: str,
    user_id: str,
    username: str,
    is_typing: bool,
    room: Optional[str] = None
) -> None:
    """Handle typing indicator"""
    message = {
        "type": MessageType.TYPING_START if is_typing else MessageType.TYPING_STOP,
        "data": {
            "user_id": user_id,
            "username": username,
            "room": room
        }
    }
    
    if room:
        await ws_manager.send_to_room(room, message, exclude_connection=connection_id)
    else:
        await ws_manager.broadcast(message, exclude_connection=connection_id)


async def handle_code_execution(
    connection_id: str,
    user_id: str,
    data: dict
) -> None:
    """Handle code execution request"""
    code = data.get("code", "").strip()
    execution_id = data.get("execution_id")
    
    if not code:
        await ws_manager.send_to_connection(connection_id, {
            "type": MessageType.CODE_ERROR,
            "data": {
                "error": "Empty code",
                "message": "Code cannot be empty",
                "execution_id": execution_id
            }
        })
        return
    
    # Send status update
    await ws_manager.send_to_connection(connection_id, {
        "type": MessageType.CODE_STATUS,
        "data": {
            "status": "queued",
            "message": "Code execution queued",
            "execution_id": execution_id
        }
    })
    
    # TODO: Integrate with code executor service
    logger.info(f"Code execution requested by {user_id}: {code[:50]}")

    # Prepare streaming execution
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from app.services.code_executor import CodeExecutor
    from app.services.notebook_db import NotebookDB

    loop = asyncio.get_event_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def stdout_collector_factory():
        # collect writes into a list and put incremental chunks onto the asyncio queue
        buffer: list[str] = []

        def write(s: str):
            try:
                buffer.append(s)
                # push to async queue
                asyncio.run_coroutine_threadsafe(queue.put(s), loop)
            except Exception:
                pass

        def getvalue():
            return ''.join(buffer)

        return write, getvalue

    stdout_write, stdout_get = stdout_collector_factory()
    stderr_write, stderr_get = stdout_collector_factory()

    def run_code():
        try:
            executor = CodeExecutor(timeout_seconds=30, max_memory_mb=512)
            # provide a db helper in context
            context = {"db": NotebookDB(user_id=int(user_id))}
            result = executor.execute(code, context=context, stdout_writer=stdout_write, stderr_writer=stderr_write)
            return result
        except Exception as e:
            return {"success": False, "output": "", "error": str(e), "execution_time": 0.0, "images": [], "plotly_figures": [], "variables": {}, "timestamp": ""}

    # Start background thread for execution
    executor_pool = ThreadPoolExecutor(max_workers=1)
    future = executor_pool.submit(run_code)

    # send running status
    await ws_manager.send_to_connection(connection_id, {
        "type": MessageType.CODE_STATUS,
        "data": {"status": "running", "execution_id": execution_id}
    })

    # Stream output as it becomes available
    try:
        while True:
            try:
                chunk = await asyncio.wait_for(queue.get(), timeout=0.5)
                await ws_manager.send_to_connection(connection_id, {
                    "type": MessageType.CODE_OUTPUT,
                    "data": {"chunk": chunk, "execution_id": execution_id}
                })
            except asyncio.TimeoutError:
                # check if finished
                if future.done():
                    break
                continue

        # Execution completed, get result
        result = future.result()

        # Send final complete message
        await ws_manager.send_to_connection(connection_id, {
            "type": MessageType.CODE_COMPLETE,
            "data": {"result": result, "execution_id": execution_id}
        })

    except Exception as e:
        logger.exception("Streaming execution failed: %s", e)
        await ws_manager.send_to_connection(connection_id, {
            "type": MessageType.CODE_ERROR,
            "data": {"error": str(e), "execution_id": execution_id}
        })
    finally:
        try:
            executor_pool.shutdown(wait=False)
        except Exception:
            pass


async def handle_file_upload_start(
    connection_id: str,
    user_id: str,
    data: dict
) -> None:
    """Handle file upload start"""
    filename = data.get("filename")
    file_size = data.get("size")
    upload_id = data.get("upload_id")
    
    if not filename or not file_size:
        await ws_manager.send_to_connection(connection_id, {
            "type": MessageType.FILE_UPLOAD_ERROR,
            "data": {
                "error": "Invalid upload data",
                "message": "Filename and size are required",
                "upload_id": upload_id
            }
        })
        return
    
    # Send acknowledgment
    await ws_manager.send_to_connection(connection_id, {
        "type": MessageType.FILE_UPLOAD_PROGRESS,
        "data": {
            "status": "started",
            "filename": filename,
            "size": file_size,
            "progress": 0,
            "upload_id": upload_id
        }
    })
    
    logger.info(f"File upload started by {user_id}: {filename} ({file_size} bytes)")


async def handle_cursor_move(
    connection_id: str,
    user_id: str,
    username: str,
    data: dict,
    room: Optional[str] = None
) -> None:
    """Handle cursor movement for collaboration"""
    position = data.get("position")
    
    if not position:
        return
    
    message = {
        "type": MessageType.CURSOR_MOVE,
        "data": {
            "user_id": user_id,
            "username": username,
            "position": position,
            "room": room
        }
    }
    
    if room:
        await ws_manager.send_to_room(room, message, exclude_connection=connection_id)
    else:
        await ws_manager.broadcast(message, exclude_connection=connection_id)


@router.websocket("/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    session_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """
    Legacy WebSocket endpoint for chat (backwards compatibility)
    
    Query Parameters:
        token: JWT authentication token
        session_id: Optional chat session ID to continue existing conversation
    
    Note: This endpoint is maintained for backwards compatibility.
    New clients should use /ws endpoint with enhanced features.
    """
    connection_id = None
    
    try:
        # Authenticate user
        user = await get_current_user_ws_legacy(token, db)
        user_id: int = user.id  # type: ignore
        
        # Connect WebSocket
        connection_id = await manager.connect(websocket, user_id)
        
        # Get or create chat session
        if session_id:
            chat_session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            ).first()
            if not chat_session:
                await websocket.send_json({
                    "type": "error",
                    "message": "Chat session not found"
                })
                return
        else:
            # Create new chat session
            chat_session = ChatSession(
                user_id=user_id,
                title=f"Chat {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
                context={}
            )
            db.add(chat_session)
            db.commit()
            db.refresh(chat_session)
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": chat_session.id,
            "message": "Connected to chat session"
        })
        
        # Handle messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "query":
                message = data.get("message", "")
                file_id = data.get("file_id")
                
                logger.info(f"Received query from user {user_id}: {message[:50]}...")
                
                # Send acknowledgment
                await websocket.send_json({
                    "type": "processing",
                    "message": "Processing your query..."
                })
                
                try:
                    # Process the query
                    response_text = await process_natural_language_query(
                        message,
                        file_id,
                        user_id,
                        db
                    )
                    
                    # Save query to database
                    db_query = QueryModel(
                        user_id=user_id,
                        file_id=file_id,
                        chat_session_id=chat_session.id,
                        query_text=message,
                        response=response_text,
                        execution_status="success"
                    )
                    db.add(db_query)
                    db.commit()
                    db.refresh(db_query)
                    
                    # Send response
                    await websocket.send_json({
                        "type": "response",
                        "message": response_text,
                        "query_id": db_query.id,
                        "timestamp": db_query.created_at.isoformat()
                    })
                    
                except Exception as e:
                    logger.exception(f"Error processing query: {e}")
                    
                    # Save failed query
                    db_query = QueryModel(
                        user_id=user_id,
                        file_id=file_id,
                        chat_session_id=chat_session.id,
                        query_text=message,
                        execution_status="failed",
                        error_message=str(e)
                    )
                    db.add(db_query)
                    db.commit()
                    
                    # Send error response
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error processing query: {str(e)}"
                    })
            
            elif data.get("type") == "ping":
                # Handle ping/keepalive
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally: {connection_id}")
    except ValueError as e:
        logger.error(f"Authentication error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except WebSocketDisconnect:
            # Client already disconnected; nothing to send back
            logger.info("Client disconnected before error message could be sent")
        except Exception as send_err:
            # Log unexpected errors when trying to send the error message
            logger.exception(f"Failed to send error message to websocket: {send_err}")
    except Exception as e:
        logger.exception(f"WebSocket error: {e}")
    finally:
        if connection_id:
            manager.disconnect(connection_id)


@router.get("/sessions")
async def list_chat_sessions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List all chat sessions for the authenticated user"""
    # This would need authentication, simplified for now
    sessions = db.query(ChatSession).filter(
        ChatSession.is_active
    ).order_by(ChatSession.updated_at.desc()).offset(skip).limit(limit).all()
    
    return sessions


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get all messages for a specific chat session"""
    queries = db.query(QueryModel).filter(
        QueryModel.chat_session_id == session_id
    ).order_by(QueryModel.created_at.asc()).all()
    
    return queries


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket statistics"""
    return ws_manager.get_stats()


@router.get("/ws/connections")
async def get_active_connections():
    """Get list of active connections"""
    connections = []
    for connection_id in list(ws_manager.active_connections.keys()):
        info = ws_manager.get_connection_info(connection_id)
        if info:
            connections.append(info)
    
    return {
        "total": len(connections),
        "connections": connections
    }
