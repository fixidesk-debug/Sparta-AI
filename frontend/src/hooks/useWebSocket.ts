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

  // Helpers
  const sanitizeForLog = (value: unknown, maxLen = 300): string => {
    try {
      if (value == null) return '';
      const s = String(value);
      // collapse whitespace and remove non-printable chars to avoid log injection
      const cleaned = s.replace(/\s+/g, ' ').replace(/[^\x20-\x7E]/g, '');
      return cleaned.length > maxLen ? cleaned.slice(0, maxLen) + '...' : cleaned;
    } catch {
      return '';
    }
  };

  const safeGet = (obj: any, path: string[], fallback: any = undefined) => {
    try {
      return path.reduce((acc, k) => (acc && acc[k] !== undefined ? acc[k] : undefined), obj) ?? fallback;
    } catch {
      return fallback;
    }
  };

  const MAX_CODE_LENGTH = 10000;
  const bannedCodePatterns = /(\beval\s*\(|\bnew\s+Function\b|\brequire\s*\(|process\.|child_process|exec\s*\()/i;

  const isSafeCode = (code: unknown): { ok: boolean; reason?: string } => {
    if (typeof code !== 'string') return { ok: false, reason: 'Code must be a string' };
    if (code.length === 0) return { ok: false, reason: 'Code is empty' };
    if (code.length > MAX_CODE_LENGTH) return { ok: false, reason: 'Code too large' };
    if (bannedCodePatterns.test(code)) return { ok: false, reason: 'Code contains unsafe patterns' };
    return { ok: true };
  };

  // Register a handler and push its unsubscribe into handlersRef
  const registerHandler = (type: MessageType | string, cb: (msg: any) => void) => {
    if (!clientRef.current) return;
    const unsub = clientRef.current.on(type as any, (msg: any) => {
      try {
        cb(msg);
      } catch (err) {
        const m = sanitizeForLog((err as any)?.message || err);
        // eslint-disable-next-line no-console
        console.error(`WebSocket handler error [${String(type)}]: ${m}`);
        if (onError) onError(new Error(m || 'WebSocket handler error'));
      }
    });
    handlersRef.current.push(unsub);
  };

  // Initialize WebSocket client
  // Keep stable refs to callbacks so we don't need to include them in useEffect deps
  const onMessageRef = useRef(onMessage);
  const onTypingRef = useRef(onTyping);
  const onCodeOutputRef = useRef(onCodeOutput);
  const onCodeCompleteRef = useRef(onCodeComplete);
  const onFileUploadProgressRef = useRef(onFileUploadProgress);
  const onUserJoinedRef = useRef(onUserJoined);
  const onUserLeftRef = useRef(onUserLeft);
  const onErrorRef = useRef(onError);

  // update refs when callbacks change
  useEffect(() => { onMessageRef.current = onMessage; onTypingRef.current = onTyping; onCodeOutputRef.current = onCodeOutput; onCodeCompleteRef.current = onCodeComplete; onFileUploadProgressRef.current = onFileUploadProgress; onUserJoinedRef.current = onUserJoined; onUserLeftRef.current = onUserLeft; onErrorRef.current = onError; }, [onMessage, onTyping, onCodeOutput, onCodeComplete, onFileUploadProgress, onUserJoined, onUserLeft, onError]);

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

    // Register error handler (sanitize error before logging)
    const unsubError = client.onError((error) => {
      const msg = sanitizeForLog((error as any)?.message || error);
      // eslint-disable-next-line no-console
      console.error('WebSocket error:', msg);
      if (onError) onError(new Error(msg || 'WebSocket error'));
    });
    handlersRef.current.push(unsubError);

    // Register message handlers and wrap parsing with validation
    const effectiveOnMessage = onMessageRef.current;
    const effectiveOnTyping = onTypingRef.current;
    const effectiveOnCodeOutput = onCodeOutputRef.current;
    const effectiveOnCodeComplete = onCodeCompleteRef.current;
    const effectiveOnFileUploadProgress = onFileUploadProgressRef.current;
    const effectiveOnUserJoined = onUserJoinedRef.current;
    const effectiveOnUserLeft = onUserLeftRef.current;
    const effectiveOnError = onErrorRef.current;

    if (effectiveOnMessage) {
      registerHandler(MessageType.CHAT_MESSAGE, (msg) => {
        const data = safeGet(msg, ['data'], {});
        effectiveOnMessage({
          id: msg.message_id || `${Date.now()}`,
          content: safeGet(data, ['message'], ''),
          role: msg.sender_id === 'ai_assistant' ? 'assistant' : 'user',
          timestamp: new Date(safeGet(msg, ['timestamp'], Date.now())),
          conversationId: safeGet(data, ['session_id'], ''),
          user: {
            id: msg.sender_id || '',
            name: safeGet(data, ['username'], 'Unknown'),
            email: '',
          },
          status: 'sent',
          metadata: data,
        });
      });

      registerHandler(MessageType.CHAT_RESPONSE, (msg) => {
        const data = safeGet(msg, ['data'], {});
        effectiveOnMessage({
          id: msg.message_id || `${Date.now()}`,
          content: safeGet(data, ['message'], ''),
          role: 'assistant',
          timestamp: new Date(safeGet(msg, ['timestamp'], Date.now())),
          conversationId: safeGet(data, ['session_id'], ''),
          user: {
            id: 'ai_assistant',
            name: 'AI Assistant',
            email: '',
          },
          status: 'sent',
          metadata: data,
        });
      });
    }

    if (effectiveOnTyping) {
      registerHandler(MessageType.TYPING_START, (msg) => {
        const data = safeGet(msg, ['data'], {});
        effectiveOnTyping(safeGet(data, ['user_id'], ''), safeGet(data, ['username'], ''), true);
      });

      registerHandler(MessageType.TYPING_STOP, (msg) => {
        const data = safeGet(msg, ['data'], {});
        effectiveOnTyping(safeGet(data, ['user_id'], ''), safeGet(data, ['username'], ''), false);
      });
    }

    if (effectiveOnCodeOutput) {
      registerHandler(MessageType.CODE_OUTPUT, (msg) => {
        const data = safeGet(msg, ['data'], {});
        effectiveOnCodeOutput(safeGet(data, ['execution_id'], ''), safeGet(data, ['output'], ''), safeGet(data, ['type'], 'stdout'));
      });
    }

    if (effectiveOnCodeComplete) {
      registerHandler(MessageType.CODE_COMPLETE, (msg) => {
        const data = safeGet(msg, ['data'], {});
        effectiveOnCodeComplete(safeGet(data, ['execution_id'], ''), safeGet(data, ['result'], null));
      });
    }

    if (effectiveOnFileUploadProgress) {
      registerHandler(MessageType.FILE_UPLOAD_PROGRESS, (msg) => {
        const data = safeGet(msg, ['data'], {});
        effectiveOnFileUploadProgress(safeGet(data, ['upload_id'], ''), Number(safeGet(data, ['progress'], 0)), safeGet(data, ['status'], ''));
      });
    }

    if (effectiveOnUserJoined) {
      registerHandler(MessageType.USER_JOINED, (msg) => {
        const data = safeGet(msg, ['data'], {});
        effectiveOnUserJoined(safeGet(data, ['user_id'], ''), safeGet(data, ['room'], ''));
      });
    }

    if (effectiveOnUserLeft) {
      registerHandler(MessageType.USER_LEFT, (msg) => {
        const data = safeGet(msg, ['data'], {});
        effectiveOnUserLeft(safeGet(data, ['user_id'], ''), safeGet(data, ['room'], ''));
      });
    }

    // Register system message handler for logging (sanitize user-controlled content)
    registerHandler(MessageType.SYSTEM, (msg) => {
      const msgText = sanitizeForLog(safeGet(msg, ['data', 'message'], ''));
      // eslint-disable-next-line no-console
      console.log('System message:', msgText);
    });

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
  }, [url, token, room, autoConnect, debug]);

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

  // Execute code - validate for unsafe patterns before sending
  const executeCode = useCallback((code: string, language = 'python', executionId?: string) => {
    const safe = isSafeCode(code);
    if (!safe.ok) {
      const reason = sanitizeForLog(safe.reason || 'Unsafe code');
      // eslint-disable-next-line no-console
      console.warn('executeCode rejected:', reason);
      return;
    }

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

  // Reconnect with short randomized backoff to avoid tight loops
  const reconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.disconnect();
      const delay = Math.min(1000, 100 + Math.floor(Math.random() * 400));
      setTimeout(() => {
        if (clientRef.current) {
          clientRef.current.connect();
        }
      }, delay);
    }
  }, []);

  // Get statistics
  const getStats = useCallback(() => clientRef.current?.getStats() || null, []);

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

