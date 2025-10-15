/**
 * WebSocket Client for Sparta AI
 * 
 * Robust WebSocket client with automatic reconnection, message queuing,
 * and comprehensive error handling.
 */

export enum ConnectionStatus {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error',
}

export enum MessageType {
  // Chat messages
  CHAT_MESSAGE = 'chat_message',
  CHAT_RESPONSE = 'chat_response',
  TYPING_START = 'typing_start',
  TYPING_STOP = 'typing_stop',
  
  // Code execution
  CODE_EXECUTE = 'code_execute',
  CODE_STATUS = 'code_status',
  CODE_OUTPUT = 'code_output',
  CODE_COMPLETE = 'code_complete',
  CODE_ERROR = 'code_error',
  
  // File operations
  FILE_UPLOAD_START = 'file_upload_start',
  FILE_UPLOAD_PROGRESS = 'file_upload_progress',
  FILE_UPLOAD_COMPLETE = 'file_upload_complete',
  FILE_UPLOAD_ERROR = 'file_upload_error',
  
  // Collaboration
  USER_JOINED = 'user_joined',
  USER_LEFT = 'user_left',
  USER_LIST = 'user_list',
  CURSOR_MOVE = 'cursor_move',
  
  // System
  PING = 'ping',
  PONG = 'pong',
  ERROR = 'error',
  SYSTEM = 'system',
  DISCONNECT = 'disconnect',
}

export interface WebSocketMessage {
  type: MessageType | string;
  data: Record<string, any>;
  room?: string;
  sender_id?: string;
  timestamp?: number;
  message_id?: string;
}

export interface WebSocketConfig {
  url: string;
  token: string;
  room?: string;
  autoConnect?: boolean;
  reconnect?: boolean;
  reconnectInterval?: number;
  reconnectDecay?: number;
  maxReconnectInterval?: number;
  maxReconnectAttempts?: number;
  pingInterval?: number;
  pingTimeout?: number;
  messageQueueSize?: number;
  debug?: boolean;
}

export type MessageHandler = (message: WebSocketMessage) => void;
export type StatusChangeHandler = (status: ConnectionStatus) => void;
export type ErrorHandler = (error: Error) => void;

interface QueuedMessage {
  message: WebSocketMessage;
  timestamp: number;
  retries: number;
}

/**
 * Robust WebSocket client with auto-reconnect and message queuing
 */
export class WebSocketClient {
  private config: Required<WebSocketConfig>;
  private ws: WebSocket | null = null;
  private status: ConnectionStatus = ConnectionStatus.DISCONNECTED;
  
  // Reconnection management
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private currentReconnectInterval: number;
  
  // Keep-alive
  private pingTimer: NodeJS.Timeout | null = null;
  private pingTimeoutTimer: NodeJS.Timeout | null = null;
  private lastPingTime = 0;
  private lastPongTime = 0;
  
  // Message queue
  private messageQueue: QueuedMessage[] = [];
  private messageHandlers: Map<MessageType | string, Set<MessageHandler>> = new Map();
  private statusHandlers: Set<StatusChangeHandler> = new Set();
  private errorHandlers: Set<ErrorHandler> = new Set();
  
  // Statistics
  private connectionTime = 0;
  private messagesSent = 0;
  private messagesReceived = 0;
  private reconnectCount = 0;
  
  constructor(config: WebSocketConfig) {
    const {
      room,
      autoConnect = true,
      reconnect = true,
      reconnectInterval = 1000,
      reconnectDecay = 1.5,
      maxReconnectInterval = 30000,
      maxReconnectAttempts = Infinity,
      pingInterval = 30000,
      pingTimeout = 5000,
      messageQueueSize = 100,
      debug = false,
      ...rest
    } = config;

    this.config = {
      ...rest,
      room: room || '',
      autoConnect,
      reconnect,
      reconnectInterval,
      reconnectDecay,
      maxReconnectInterval,
      maxReconnectAttempts,
      pingInterval,
      pingTimeout,
      messageQueueSize,
      debug,
    };
    
    this.currentReconnectInterval = this.config.reconnectInterval;
    
    if (this.config.autoConnect) {
      this.connect();
    }
  }
  
  /**
   * Connect to WebSocket server
   */
  public connect(): void {
    if (this.ws && (this.status === ConnectionStatus.CONNECTED || this.status === ConnectionStatus.CONNECTING)) {
      this.log('Already connected or connecting');
      return;
    }
    
    this.setStatus(
      this.reconnectAttempts > 0 ? ConnectionStatus.RECONNECTING : ConnectionStatus.CONNECTING
    );
    
    try {
      // Build WebSocket URL with query parameters
      const url = new URL(this.config.url);
      url.searchParams.set('token', this.config.token);
      if (this.config.room) {
        url.searchParams.set('room', this.config.room);
      }
      
      // Convert http(s) to ws(s)
      url.protocol = url.protocol.replace('http', 'ws');
      
      this.log('Connecting to:', url.toString().replace(this.config.token, '***'));
      
      // Create WebSocket connection
      this.ws = new WebSocket(url.toString());
      
      // Set up event handlers
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
    } catch (error) {
      this.log('Connection error:', error);
      this.handleError(error as Event);
    }
  }
  
  /**
   * Disconnect from WebSocket server
   */
  public disconnect(): void {
    this.log('Disconnecting...');
    this.config.reconnect = false;
    this.stopReconnect();
    this.stopPing();
    
    if (this.ws) {
      try {
        this.ws.close(1000, 'Client disconnect');
      } catch (error) {
        this.log('Error closing WebSocket:', error);
      }
      this.ws = null;
    }
    
    this.setStatus(ConnectionStatus.DISCONNECTED);
  }
  
  /**
   * Send message to server
   */
  public send(message: WebSocketMessage): boolean {
    // Add to queue if not connected
    if (this.status !== ConnectionStatus.CONNECTED) {
      this.queueMessage(message);
      return false;
    }
    
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.queueMessage(message);
      return false;
    }
    
    try {
      const messageStr = JSON.stringify(message);
      this.ws.send(messageStr);
      this.messagesSent++;
      this.log('Sent:', message.type, message.data);
      return true;
    } catch (error) {
      this.log('Error sending message:', error);
      this.queueMessage(message);
      this.notifyError(error as Error);
      return false;
    }
  }
  
  /**
   * Send chat message
   */
  public sendChatMessage(
    message: string,
    options?: {
      room?: string;
      session_id?: number;
      file_id?: number;
      process_nlp?: boolean;
    }
  ): void {
    this.send({
      type: MessageType.CHAT_MESSAGE,
      data: {
        message,
        ...options,
      },
      room: options?.room,
    });
  }
  
  /**
   * Send typing indicator
   */
  public sendTypingIndicator(isTyping: boolean, room?: string): void {
    this.send({
      type: isTyping ? MessageType.TYPING_START : MessageType.TYPING_STOP,
      data: {},
      room,
    });
  }
  
  /**
   * Execute code
   */
  public executeCode(
    code: string,
    language: string = 'python',
    executionId?: string
  ): void {
    this.send({
      type: MessageType.CODE_EXECUTE,
      data: {
        code,
        language,
        execution_id: executionId || `exec_${Date.now()}`,
      },
    });
  }
  
  /**
   * Report file upload start
   */
  public reportFileUploadStart(
    filename: string,
    size: number,
    uploadId: string
  ): void {
    this.send({
      type: MessageType.FILE_UPLOAD_START,
      data: {
        filename,
        size,
        upload_id: uploadId,
      },
    });
  }
  
  /**
   * Join a room
   */
  public joinRoom(room: string): void {
    this.send({
      type: 'join_room',
      data: { room },
    });
  }
  
  /**
   * Leave a room
   */
  public leaveRoom(room: string): void {
    this.send({
      type: 'leave_room',
      data: { room },
    });
  }
  
  /**
   * Register message handler
   */
  public on(type: MessageType | string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }
    this.messageHandlers.get(type)!.add(handler);
    
    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(type);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.messageHandlers.delete(type);
        }
      }
    };
  }
  
  /**
   * Register status change handler
   */
  public onStatusChange(handler: StatusChangeHandler): () => void {
    this.statusHandlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.statusHandlers.delete(handler);
    };
  }
  
  /**
   * Register error handler
   */
  public onError(handler: ErrorHandler): () => void {
    this.errorHandlers.add(handler);
    
    // Return unsubscribe function
    return () => {
      this.errorHandlers.delete(handler);
    };
  }
  
  /**
   * Remove all event handlers
   */
  public removeAllHandlers(): void {
    this.messageHandlers.clear();
    this.statusHandlers.clear();
    this.errorHandlers.clear();
  }
  
  /**
   * Get current connection status
   */
  public getStatus(): ConnectionStatus {
    return this.status;
  }
  
  /**
   * Check if connected
   */
  public isConnected(): boolean {
    return this.status === ConnectionStatus.CONNECTED;
  }
  
  /**
   * Get connection statistics
   */
  public getStats() {
    const now = Date.now();
    const uptime = this.status === ConnectionStatus.CONNECTED
      ? now - this.connectionTime
      : 0;
    
    return {
      status: this.status,
      uptime,
      messagesSent: this.messagesSent,
      messagesReceived: this.messagesReceived,
      queuedMessages: this.messageQueue.length,
      reconnectAttempts: this.reconnectAttempts,
      reconnectCount: this.reconnectCount,
      lastPing: this.lastPingTime,
      lastPong: this.lastPongTime,
      latency: this.lastPongTime - this.lastPingTime,
    };
  }
  
  /**
   * Clear message queue
   */
  public clearQueue(): void {
    this.messageQueue = [];
    this.log('Message queue cleared');
  }
  
  // Private methods
  
  private handleOpen(event: Event): void {
    this.log('WebSocket connected');
    this.setStatus(ConnectionStatus.CONNECTED);
    this.connectionTime = Date.now();
    this.reconnectAttempts = 0;
    this.currentReconnectInterval = this.config.reconnectInterval;
    
    // Start ping/pong keep-alive
    this.startPing();
    
    // Send queued messages
    this.processQueue();
  }
  
  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      this.messagesReceived++;
      
      this.log('Received:', message.type, message.data);
      
      // Handle pong
      if (message.type === MessageType.PONG) {
        this.lastPongTime = Date.now();
        this.clearPingTimeout();
        return;
      }
      
      // Notify handlers
      const handlers = this.messageHandlers.get(message.type);
      if (handlers) {
        handlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            this.log('Error in message handler:', error);
          }
        });
      }
      
      // Notify wildcard handlers
      const wildcardHandlers = this.messageHandlers.get('*');
      if (wildcardHandlers) {
        wildcardHandlers.forEach(handler => {
          try {
            handler(message);
          } catch (error) {
            this.log('Error in wildcard handler:', error);
          }
        });
      }
    } catch (error) {
      this.log('Error parsing message:', error);
      this.notifyError(error as Error);
    }
  }
  
  private handleError(event: Event): void {
    this.log('WebSocket error:', event);
    this.setStatus(ConnectionStatus.ERROR);
    this.notifyError(new Error('WebSocket error'));
  }
  
  private handleClose(event: CloseEvent): void {
    this.log('WebSocket closed:', event.code, event.reason);
    this.stopPing();
    this.ws = null;
    
    if (event.code === 1000) {
      // Normal closure
      this.setStatus(ConnectionStatus.DISCONNECTED);
    } else {
      this.setStatus(ConnectionStatus.ERROR);
      
      // Attempt reconnection if enabled
      if (this.config.reconnect && this.reconnectAttempts < this.config.maxReconnectAttempts) {
        this.scheduleReconnect();
      }
    }
  }
  
  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return;
    }
    
    this.reconnectAttempts++;
    this.reconnectCount++;
    
    this.log(
      `Scheduling reconnect attempt ${this.reconnectAttempts} ` +
      `in ${this.currentReconnectInterval}ms`
    );
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, this.currentReconnectInterval);
    
    // Increase reconnect interval with exponential backoff
    this.currentReconnectInterval = Math.min(
      this.currentReconnectInterval * this.config.reconnectDecay,
      this.config.maxReconnectInterval
    );
  }
  
  private stopReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.reconnectAttempts = 0;
    this.currentReconnectInterval = this.config.reconnectInterval;
  }
  
  private startPing(): void {
    this.stopPing();
    
    this.pingTimer = setInterval(() => {
      if (this.status === ConnectionStatus.CONNECTED && this.ws) {
        this.lastPingTime = Date.now();
        this.send({
          type: MessageType.PING,
          data: { timestamp: this.lastPingTime },
        });
        
        // Set timeout for pong response
        this.pingTimeoutTimer = setTimeout(() => {
          this.log('Ping timeout - no pong received');
          this.ws?.close(1000, 'Ping timeout');
        }, this.config.pingTimeout);
      }
    }, this.config.pingInterval);
  }
  
  private stopPing(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
    this.clearPingTimeout();
  }
  
  private clearPingTimeout(): void {
    if (this.pingTimeoutTimer) {
      clearTimeout(this.pingTimeoutTimer);
      this.pingTimeoutTimer = null;
    }
  }
  
  private queueMessage(message: WebSocketMessage): void {
    // Add to queue
    this.messageQueue.push({
      message,
      timestamp: Date.now(),
      retries: 0,
    });
    
    // Limit queue size
    if (this.messageQueue.length > this.config.messageQueueSize) {
      const removed = this.messageQueue.shift();
      this.log('Message queue full, removed oldest message:', removed?.message.type);
    }
    
    this.log('Message queued:', message.type, `(queue size: ${this.messageQueue.length})`);
  }
  
  private processQueue(): void {
    if (this.messageQueue.length === 0) {
      return;
    }
    
    this.log(`Processing ${this.messageQueue.length} queued messages`);
    
    const queue = [...this.messageQueue];
    this.messageQueue = [];
    
    for (const item of queue) {
      const sent = this.send(item.message);
      
      if (!sent) {
        // Re-queue if send failed
        item.retries++;
        if (item.retries < 3) {
          this.messageQueue.push(item);
        } else {
          this.log('Message dropped after 3 retries:', item.message.type);
        }
      }
    }
  }
  
  private setStatus(status: ConnectionStatus): void {
    if (this.status === status) {
      return;
    }
    
    this.log('Status changed:', this.status, '->', status);
    this.status = status;
    
    // Notify handlers
    this.statusHandlers.forEach(handler => {
      try {
        handler(status);
      } catch (error) {
        this.log('Error in status handler:', error);
      }
    });
  }
  
  private notifyError(error: Error): void {
    this.errorHandlers.forEach(handler => {
      try {
        handler(error);
      } catch (err) {
        this.log('Error in error handler:', err);
      }
    });
  }
  
  private log(...args: any[]): void {
    if (this.config.debug) {
      console.log('[WebSocketClient]', ...args);
    }
  }
}

/**
 * Create WebSocket client instance
 */
export function createWebSocketClient(config: WebSocketConfig): WebSocketClient {
  return new WebSocketClient(config);
}
