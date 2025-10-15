/**
 * ChatContainer Component
 * Main orchestrator for the Sparta AI chat interface
 */

import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { ErrorBoundary } from './ErrorBoundary';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';
import { Message, Attachment, User, WebSocketMessage } from '../types/chat';
import { v4 as uuidv4 } from 'uuid';

interface ChatContainerProps {
  userId: string;
  userName: string;
  userEmail: string;
  conversationId?: string;
  wsUrl?: string;
  token?: string;
  className?: string;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  userId,
  userName,
  userEmail,
  conversationId: initialConversationId,
  wsUrl = 'ws://localhost:8000/ws/chat',
  token,
  className = '',
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId] = useState<string>(
    initialConversationId || uuidv4()
  );
  const [isAITyping, setIsAITyping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentUser: User = useMemo(
    () => ({
      id: userId,
      email: userEmail,
      name: userName,
    }),
    [userId, userEmail, userName]
  );

  const aiUser: User = useMemo(
    () => ({
      id: 'ai-assistant',
      email: 'ai@sparta.ai',
      name: 'Sparta AI',
    }),
    []
  );

  // Small sanitizer to avoid log injection (CWE-117) and limit log size
  const sanitizeForLog = (value: unknown): string => {
    try {
      let s: string;
      if (typeof value === 'string') s = value;
      else if (value instanceof Error) s = value.message || String(value);
      else {
        try {
          s = JSON.stringify(value);
        } catch {
          s = String(value);
        }
      }
      s = s.replace(/[\r\n\x00-\x1F\x7F]+/g, ' ');
      const MAX = 1000;
      if (s.length > MAX) s = s.slice(0, MAX) + '...';
      return s;
    } catch {
      return '[unserializable]';
    }
  };

  // Handle incoming WebSocket messages
  const handleWebSocketMessage = useCallback(
    (wsMessage: WebSocketMessage) => {
      switch (wsMessage.type) {
        case 'message':
          // Add AI response to messages
          const aiMessage: Message = {
            id: wsMessage.payload.id || uuidv4(),
            conversationId,
            user: aiUser,
            role: 'assistant',
            content: wsMessage.payload.content || '',
            timestamp: new Date(wsMessage.timestamp),
            status: 'sent',
            codeBlocks: wsMessage.payload.codeBlocks,
            visualizations: wsMessage.payload.visualizations,
            attachments: wsMessage.payload.attachments,
            metadata: wsMessage.payload.metadata,
          };
          setMessages((prev) => [...prev, aiMessage]);
          setIsAITyping(false);
          setError(null);
          break;

        case 'typing':
          setIsAITyping(wsMessage.payload.isTyping === true);
          break;

        case 'error':
          setError(wsMessage.payload.message || 'An error occurred');
          setIsAITyping(false);
          // Update last message with error if it's still sending
          setMessages((prev) => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg && lastMsg.status === 'sending') {
              return [
                ...prev.slice(0, -1),
                { ...lastMsg, status: 'error', error: wsMessage.payload.message },
              ];
            }
            return prev;
          });
          break;

        case 'status':
          // Update message status
          if (wsMessage.payload.messageId) {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === wsMessage.payload.messageId
                  ? { ...msg, status: wsMessage.payload.status }
                  : msg
              )
            );
          }
          break;

        default:
          console.log('Unknown WebSocket message type:', sanitizeForLog(wsMessage.type));
      }
    },
    [conversationId, aiUser]
  );

  // Handle typing indicator from WebSocket
  const handleTypingIndicator = useCallback((isTyping: boolean) => {
    setIsAITyping(isTyping);
  }, []);



  // Initialize WebSocket connection
  const { isConnected, sendMessage: wsSendMessage } = useWebSocket({
    url: wsUrl,
    token: token || '',
    onMessage: (message: Message) => {
      const wsMessage: WebSocketMessage = {
        type: 'message',
        payload: message,
        timestamp: message.timestamp.toISOString()
      };
      handleWebSocketMessage(wsMessage);
    },
    onTyping: (userId: string, username: string, isTyping: boolean) => {
      handleTypingIndicator(isTyping);
    },
    onError: (error: Error) => {
      console.error('WebSocket error:', sanitizeForLog(error));
      setError('Connection error. Please check your network.');
      setIsAITyping(false);
    },
  });

  // Send message to AI
  const handleSendMessage = useCallback(
    (content: string, attachments?: Attachment[]) => {
      // Create user message
      const userMessage: Message = {
        id: uuidv4(),
        conversationId,
        user: currentUser,
        role: 'user',
        content,
        timestamp: new Date(),
        status: 'sending',
        attachments,
      };

      // Add to messages
      setMessages((prev) => [...prev, userMessage]);
      setError(null);

      // Send via WebSocket
      if (isConnected) {
        try {
          wsSendMessage(content, {
            process_nlp: true,
            // Note: id, conversationId, attachments are passed in metadata but not part of options type
          });
        } catch (err) {
          console.error('Failed to send message via WebSocket:', sanitizeForLog(err));
          setError('Failed to send message. Please try again.');
        }

        // Update message status to sent
        setTimeout(() => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === userMessage.id ? { ...msg, status: 'sent' } : msg
            )
          );
        }, 100);

        // Show AI typing indicator
        setIsAITyping(true);
      } else {
        // Connection lost - mark as error
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === userMessage.id
              ? { ...msg, status: 'error', error: 'Not connected to server' }
              : msg
          )
        );
        setError('Not connected to server. Please check your connection.');
      }
    },
    [conversationId, currentUser, isConnected, wsSendMessage]
  );

  // Handle code execution
  const handleExecuteCode = useCallback(
    (code: string) => {
      // Send code execution request via WebSocket
      if (isConnected) {
        try {
          // For code execution, we should use the executeCode method instead
          // which properly handles the WebSocket protocol
          // For now, send as a regular message
          wsSendMessage(code);
          setIsAITyping(true);
        } catch (err) {
          console.error('Failed to execute code via WebSocket:', sanitizeForLog(err));
          setError('Failed to execute code. Please try again.');
        }
      } else {
        setError('Cannot execute code: Not connected to server');
      }
    },
    [isConnected, wsSendMessage]
  );

  // Load conversation history on mount
  useEffect(() => {
    const loadConversationHistory = async () => {
      try {
        // TODO: Implement API call to load conversation history
        // const response = await fetch(`/api/v1/conversations/${conversationId}/messages`);
        // const data = await response.json();
        // setMessages(data.messages);
      } catch (err) {
        console.error('Failed to load conversation history:', sanitizeForLog(err));
      }
    };

    if (conversationId) {
      loadConversationHistory();
    }
  }, [conversationId]);

  return (
    <ErrorBoundary>
      <div className={`chat-container flex flex-col h-full bg-gray-50 ${className}`}>
        {/* Header */}
        <div className="chat-header flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200 shadow-sm">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Sparta AI Assistant</h1>
            <p className="text-sm text-gray-500">
              {isConnected ? (
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  Connected
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-red-500 rounded-full" />
                  Disconnected
                </span>
              )}
            </p>
          </div>

          {/* Info button */}
          <button
            type="button"
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Info"
            title="Info"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </button>
        </div>

        {/* Error banner */}
        {error && (
          <div
            className="error-banner flex items-center gap-2 px-6 py-3 bg-red-50 border-b border-red-200"
            role="alert"
          >
            <svg className="w-5 h-5 text-red-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-sm text-red-800">{error}</p>
            <button
              type="button"
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700 focus:outline-none"
              aria-label="Dismiss error"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-hidden">
          <MessageList
            messages={messages}
            currentUserId={userId}
            isLoading={isAITyping}
            onExecuteCode={handleExecuteCode}
          />
        </div>

        {/* Typing indicator */}
        {isAITyping && <TypingIndicator isTyping={isAITyping} userName="Sparta AI" />}

        {/* Input */}
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={!isConnected || isAITyping}
          allowAttachments={true}
        />
      </div>
    </ErrorBoundary>
  );
};
