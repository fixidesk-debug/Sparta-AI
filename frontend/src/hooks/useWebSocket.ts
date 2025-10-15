/**
 * WebSocket Hook for Real-time Communication
 * 
 * Enhanced React hook using the robust WebSocketClient with automatic
 * reconnection, message queuing, and comprehensive error handling.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { Message } from '../types/chat';
import {
  WebSocketClient,
  createWebSocketClient,
  ConnectionStatus,
  MessageType,
  WebSocketConfig,
} from '../utils/websocketClient';

interface UseWebSocketProps {
  url: string;
  token: string;
  room?: string;
  onMessage?: (message: Message) => void;
  onTyping?: (userId: string, username: string, isTyping: boolean) => void;
  onCodeOutput?: (executionId: string, output: string, type: 'stdout' | 'stderr') => void;
  onCodeComplete?: (executionId: string, result: any) => void;
  onFileUploadProgress?: (uploadId: string, progress: number, status: string) => void;
  onUserJoined?: (userId: string, room: string) => void;
  onUserLeft?: (userId: string, room: string) => void;
  onError?: (error: Error) => void;
  autoConnect?: boolean;
  debug?: boolean;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  status: ConnectionStatus;
  sendMessage: (message: string, options?: {
    room?: string;
    session_id?: number;
    file_id?: number;
    process_nlp?: boolean;
  }) => void;
  sendTyping: (isTyping: boolean, room?: string) => void;
  executeCode: (code: string, language?: string, executionId?: string) => void;
  reportFileUploadStart: (filename: string, size: number, uploadId: string) => void;
  joinRoom: (room: string) => void;
  leaveRoom: (room: string) => void;
  disconnect: () => void;
  reconnect: () => void;
  getStats: () => any;
  clearQueue: () => void;
  client: WebSocketClient | null;
}

export const useWebSocket = ({
  url,
  token,
  room,
  onMessage,
  onTyping,
  onCodeOutput,
  onCodeComplete,
  onFileUploadProgress,
  onUserJoined,
  onUserLeft,
  onError,
  autoConnect = true,
  debug = false,
}: UseWebSocketProps): UseWebSocketReturn => {
  const [isConnected, setIsConnected] = useState(false);
  const [status, setStatus] = useState<ConnectionStatus>(ConnectionStatus.DISCONNECTED);
  const clientRef = useRef<WebSocketClient | null>(null);
  const handlersRef = useRef<(() => void)[]>([]);

  // Initialize WebSocket client
  useEffect(() => {
    const config: WebSocketConfig = {
      url,
      token,
      room,
      autoConnect,
      reconnect: true,
      reconnectInterval: 1000,
      reconnectDecay: 1.5,
      maxReconnectInterval: 30000,
      maxReconnectAttempts: Infinity,
      pingInterval: 30000,
      pingTimeout: 5000,
      messageQueueSize: 100,
      debug,
    };

    const client = createWebSocketClient(config);
    clientRef.current = client;

    // Register status change handler
    const unsubStatus = client.onStatusChange((newStatus) => {
      setStatus(newStatus);
      setIsConnected(newStatus === ConnectionStatus.CONNECTED);
    });
    handlersRef.current.push(unsubStatus);

    // Register error handler
    const unsubError = client.onError((error) => {
      console.error('WebSocket error:', error);
      if (onError) {
        onError(error);
      }
    });
    handlersRef.current.push(unsubError);

    // Register message handlers
    if (onMessage) {
      const unsubChatMsg = client.on(MessageType.CHAT_MESSAGE, (msg) => {
        onMessage({
          id: msg.message_id || `${Date.now()}`,
          content: msg.data.message,
          role: msg.sender_id === 'ai_assistant' ? 'assistant' : 'user',
          timestamp: new Date(msg.timestamp || Date.now()),
          conversationId: msg.data.session_id || '',
          user: {
            id: msg.sender_id || '',
            name: msg.data.username || 'Unknown',
            email: '', // Email not available in WebSocket messages
          },
          status: 'sent',
          metadata: msg.data,
        });
      });
      handlersRef.current.push(unsubChatMsg);

      const unsubChatResp = client.on(MessageType.CHAT_RESPONSE, (msg) => {
        onMessage({
          id: msg.message_id || `${Date.now()}`,
          content: msg.data.message,
          role: 'assistant',
          timestamp: new Date(msg.timestamp || Date.now()),
          conversationId: msg.data.session_id || '',
          user: {
            id: 'ai_assistant',
            name: 'AI Assistant',
            email: '', // System user
          },
          status: 'sent',
          metadata: msg.data,
        });
      });
      handlersRef.current.push(unsubChatResp);
    }

    if (onTyping) {
      const unsubTypingStart = client.on(MessageType.TYPING_START, (msg) => {
        onTyping(msg.data.user_id, msg.data.username, true);
      });
      handlersRef.current.push(unsubTypingStart);

      const unsubTypingStop = client.on(MessageType.TYPING_STOP, (msg) => {
        onTyping(msg.data.user_id, msg.data.username, false);
      });
      handlersRef.current.push(unsubTypingStop);
    }

    if (onCodeOutput) {
      const unsubCodeOutput = client.on(MessageType.CODE_OUTPUT, (msg) => {
        onCodeOutput(
          msg.data.execution_id,
          msg.data.output,
          msg.data.type || 'stdout'
        );
      });
      handlersRef.current.push(unsubCodeOutput);
    }

    if (onCodeComplete) {
      const unsubCodeComplete = client.on(MessageType.CODE_COMPLETE, (msg) => {
        onCodeComplete(msg.data.execution_id, msg.data.result);
      });
      handlersRef.current.push(unsubCodeComplete);
    }

    if (onFileUploadProgress) {
      const unsubFileProgress = client.on(MessageType.FILE_UPLOAD_PROGRESS, (msg) => {
        onFileUploadProgress(
          msg.data.upload_id,
          msg.data.progress,
          msg.data.status
        );
      });
      handlersRef.current.push(unsubFileProgress);
    }

    if (onUserJoined) {
      const unsubUserJoined = client.on(MessageType.USER_JOINED, (msg) => {
        onUserJoined(msg.data.user_id, msg.data.room);
      });
      handlersRef.current.push(unsubUserJoined);
    }

    if (onUserLeft) {
      const unsubUserLeft = client.on(MessageType.USER_LEFT, (msg) => {
        onUserLeft(msg.data.user_id, msg.data.room);
      });
      handlersRef.current.push(unsubUserLeft);
    }

    // Register system message handler for logging
    const unsubSystem = client.on(MessageType.SYSTEM, (msg) => {
      console.log('System message:', msg.data.message);
    });
    handlersRef.current.push(unsubSystem);

    // Cleanup on unmount
    return () => {
      // Unsubscribe all handlers
      handlersRef.current.forEach(unsub => unsub());
      handlersRef.current = [];

      // Disconnect client
      if (clientRef.current) {
        clientRef.current.disconnect();
        clientRef.current = null;
      }
    };
  }, [
    url,
    token,
    room,
    autoConnect,
    debug,
    onMessage,
    onTyping,
    onCodeOutput,
    onCodeComplete,
    onFileUploadProgress,
    onUserJoined,
    onUserLeft,
    onError,
  ]);

  // Send message
  const sendMessage = useCallback((
    message: string,
    options?: {
      room?: string;
      session_id?: number;
      file_id?: number;
      process_nlp?: boolean;
    }
  ) => {
    if (clientRef.current) {
      clientRef.current.sendChatMessage(message, options);
    }
  }, []);

  // Send typing indicator
  const sendTyping = useCallback((isTyping: boolean, targetRoom?: string) => {
    if (clientRef.current) {
      clientRef.current.sendTypingIndicator(isTyping, targetRoom);
    }
  }, []);

  // Execute code
  const executeCode = useCallback((
    code: string,
    language: string = 'python',
    executionId?: string
  ) => {
    if (clientRef.current) {
      clientRef.current.executeCode(code, language, executionId);
    }
  }, []);

  // Report file upload start
  const reportFileUploadStart = useCallback((
    filename: string,
    size: number,
    uploadId: string
  ) => {
    if (clientRef.current) {
      clientRef.current.reportFileUploadStart(filename, size, uploadId);
    }
  }, []);

  // Join room
  const joinRoom = useCallback((targetRoom: string) => {
    if (clientRef.current) {
      clientRef.current.joinRoom(targetRoom);
    }
  }, []);

  // Leave room
  const leaveRoom = useCallback((targetRoom: string) => {
    if (clientRef.current) {
      clientRef.current.leaveRoom(targetRoom);
    }
  }, []);

  // Disconnect
  const disconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.disconnect();
    }
  }, []);

  // Reconnect
  const reconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.disconnect();
      setTimeout(() => {
        if (clientRef.current) {
          clientRef.current.connect();
        }
      }, 100);
    }
  }, []);

  // Get statistics
  const getStats = useCallback(() => {
    return clientRef.current?.getStats() || null;
  }, []);

  // Clear message queue
  const clearQueue = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.clearQueue();
    }
  }, []);

  return {
    isConnected,
    status,
    sendMessage,
    sendTyping,
    executeCode,
    reportFileUploadStart,
    joinRoom,
    leaveRoom,
    disconnect,
    reconnect,
    getStats,
    clearQueue,
    client: clientRef.current,
  };
};

