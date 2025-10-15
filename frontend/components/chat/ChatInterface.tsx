import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Paperclip,
  Mic,
  Smile,
  MoreVertical,
  ChevronLeft,
  ChevronRight,
  Copy,
  Check,
  AlertCircle,
  RefreshCw,
  Maximize2,
  Download,
  X
} from '../icons';
import './ChatInterface.scss';

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  status?: 'sending' | 'sent' | 'delivered' | 'read' | 'error';
  type?: 'text' | 'code' | 'chart' | 'image' | 'file';
  metadata?: {
    language?: string;
    fileName?: string;
    fileUrl?: string;
    chartData?: any;
  };
  reactions?: { emoji: string; count: number }[];
}

export interface Conversation {
  id: string;
  title: string;
  lastMessage?: string;
  timestamp: Date;
  unreadCount?: number;
}

interface ChatInterfaceProps {
  messages?: Message[];
  conversations?: Conversation[];
  currentConversationId?: string;
  onSendMessage?: (content: string, files?: File[]) => void;
  onSelectConversation?: (id: string) => void;
  onVoiceInput?: () => void;
  isTyping?: boolean;
  isProcessing?: boolean;
  isOnline?: boolean;
  userName?: string;
  aiName?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages = [],
  conversations = [],
  currentConversationId,
  onSendMessage,
  onSelectConversation,
  onVoiceInput,
  isTyping = false,
  isProcessing = false,
  isOnline = true,
  userName = 'You',
  aiName = 'Sparta AI'
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [showScrollHint, setShowScrollHint] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShowScrollHint(!isNearBottom);
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSendMessage = () => {
    if (!inputValue.trim() && selectedFiles.length === 0) return;

    if (onSendMessage) {
      onSendMessage(inputValue, selectedFiles);
    }

    setInputValue('');
    setSelectedFiles([]);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const handleCopyMessage = (messageId: string, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedMessageId(messageId);
    setTimeout(() => setCopiedMessageId(null), 2000);
  };

  const handleVoiceInput = () => {
    setIsRecording(!isRecording);
    if (onVoiceInput) {
      onVoiceInput();
    }
  };

  const renderMessageContent = (message: Message) => {
    switch (message.type) {
      case 'code':
        return (
          <div className="message-code">
            <div className="message-code__header">
              <span className="message-code__language">
                {message.metadata?.language || 'code'}
              </span>
              <button
                className="message-code__copy"
                onClick={() => handleCopyMessage(message.id, message.content)}
                title="Copy code"
              >
                {copiedMessageId === message.id ? (
                  <Check size={14} />
                ) : (
                  <Copy size={14} />
                )}
              </button>
            </div>
            <pre className="message-code__content">
              <code>{message.content}</code>
            </pre>
          </div>
        );

      case 'file':
        return (
          <div className="message-file">
            <div className="message-file__icon">
              <Paperclip size={20} />
            </div>
            <div className="message-file__info">
              <span className="message-file__name">{message.metadata?.fileName}</span>
              <button className="message-file__download" title="Download file">
                <Download size={16} />
              </button>
            </div>
          </div>
        );

      case 'chart':
        return (
          <div className="message-chart">
            <div className="message-chart__preview">
              <span>📊 Chart Visualization</span>
            </div>
            <button className="message-chart__expand" title="Expand chart">
              <Maximize2 size={16} />
            </button>
          </div>
        );

      default:
        return <p className="message-text">{message.content}</p>;
    }
  };

  const renderMessage = (message: Message, index: number) => {
    const isUser = message.sender === 'user';
    const showTimestamp = index === 0 || 
      messages[index - 1].sender !== message.sender;

    return (
      <div
        key={message.id}
        className={`message ${isUser ? 'message--user' : 'message--ai'}`}
        style={{ animationDelay: `${index * 0.05}s` }}
      >
        {!isUser && (
          <div className="message__avatar">
            <span className="message__avatar-text">{aiName[0]}</span>
          </div>
        )}

        <div className="message__content-wrapper">
          {showTimestamp && (
            <div className={`message__sender ${isUser ? 'message__sender--right' : ''}`}>
              {isUser ? userName : aiName}
            </div>
          )}

          <div className="message__bubble">
            {renderMessageContent(message)}

            {message.status === 'error' && (
              <div className="message__error">
                <AlertCircle size={14} />
                <span>Failed to send</span>
                <button className="message__retry" title="Retry">
                  <RefreshCw size={14} />
                </button>
              </div>
            )}

            <div className="message__footer">
              <span className="message__timestamp">
                {message.timestamp.toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </span>

              {isUser && message.status && message.status !== 'error' && (
                <span className={`message__status message__status--${message.status}`}>
                  {message.status === 'read' && '✓✓'}
                  {message.status === 'delivered' && '✓✓'}
                  {message.status === 'sent' && '✓'}
                </span>
              )}
            </div>

            {!isUser && (
              <button
                className="message__actions"
                onClick={() => handleCopyMessage(message.id, message.content)}
                title="Copy message"
              >
                {copiedMessageId === message.id ? (
                  <Check size={16} />
                ) : (
                  <Copy size={16} />
                )}
              </button>
            )}
          </div>

          {message.reactions && message.reactions.length > 0 && (
            <div className="message__reactions">
              {message.reactions.map((reaction, idx) => (
                <button key={idx} className="message__reaction">
                  <span>{reaction.emoji}</span>
                  <span>{reaction.count}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {isUser && (
          <div className="message__avatar">
            <span className="message__avatar-text">{userName[0]}</span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="chat-interface">
      {/* Offline Banner */}
      {!isOnline && (
        <div className="chat-interface__offline-banner">
          <AlertCircle size={16} />
          <span>You are currently offline</span>
        </div>
      )}

      {/* Sidebar */}
      <aside className={`chat-sidebar ${isSidebarCollapsed ? 'chat-sidebar--collapsed' : ''}`}>
        <div className="chat-sidebar__header">
          <h2 className="chat-sidebar__title">
            {!isSidebarCollapsed && 'Conversations'}
          </h2>
          <button
            className="chat-sidebar__toggle"
            onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            title={isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isSidebarCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
          </button>
        </div>

        <div className="chat-sidebar__conversations">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              className={`conversation ${currentConversationId === conv.id ? 'conversation--active' : ''}`}
              onClick={() => onSelectConversation?.(conv.id)}
            >
              {!isSidebarCollapsed && (
                <>
                  <div className="conversation__content">
                    <h3 className="conversation__title">{conv.title}</h3>
                    <p className="conversation__preview">{conv.lastMessage}</p>
                  </div>
                  <div className="conversation__meta">
                    <span className="conversation__time">
                      {conv.timestamp.toLocaleDateString([], { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </span>
                    {conv.unreadCount && conv.unreadCount > 0 && (
                      <span className="conversation__badge">{conv.unreadCount}</span>
                    )}
                  </div>
                </>
              )}
              {isSidebarCollapsed && conv.unreadCount && conv.unreadCount > 0 && (
                <span className="conversation__dot" />
              )}
            </button>
          ))}
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="chat-main">
        {/* Messages Container */}
        <div className="chat-messages" ref={messagesContainerRef}>
          {messages.length === 0 ? (
            <div className="chat-empty">
              <div className="chat-empty__icon">💬</div>
              <h3 className="chat-empty__title">Start a conversation</h3>
              <p className="chat-empty__text">
                Ask me anything about your data or how I can help you today.
              </p>
              <div className="chat-empty__suggestions">
                <button className="chat-suggestion">
                  Analyze my sales data
                </button>
                <button className="chat-suggestion">
                  Create a visualization
                </button>
                <button className="chat-suggestion">
                  Generate a report
                </button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => renderMessage(message, index))}
              
              {isTyping && (
                <div className="message message--ai message--typing">
                  <div className="message__avatar">
                    <span className="message__avatar-text">{aiName[0]}</span>
                  </div>
                  <div className="message__content-wrapper">
                    <div className="message__bubble">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}

          {showScrollHint && messages.length > 0 && (
            <div className="chat-scroll-hint">
              <button onClick={scrollToBottom} title="Scroll to bottom">
                ↓
              </button>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="chat-input-area">
          {selectedFiles.length > 0 && (
            <div className="chat-attachments">
              {selectedFiles.map((file, index) => (
                <div key={index} className="chat-attachment">
                  <Paperclip size={14} />
                  <span className="chat-attachment__name">{file.name}</span>
                  <button
                    className="chat-attachment__remove"
                    onClick={() => setSelectedFiles(files => files.filter((_, i) => i !== index))}
                    title="Remove file"
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}

          <div className="chat-input-wrapper">
            <button
              className="chat-input-button"
              onClick={() => fileInputRef.current?.click()}
              title="Attach file"
              disabled={!isOnline}
            >
              <Paperclip size={20} />
            </button>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              aria-label="Attach files"
            />

            <textarea
              ref={inputRef}
              className="chat-input"
              placeholder={
                isProcessing 
                  ? 'Processing...' 
                  : isRecording 
                    ? 'Listening...' 
                    : 'Type your message...'
              }
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={!isOnline || isProcessing}
              aria-label="Message input"
            />

            {inputValue.length > 900 && (
              <span className="chat-input-counter">
                {inputValue.length}/1000
              </span>
            )}

            <button
              className="chat-input-button"
              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
              title="Add emoji"
              disabled={!isOnline}
            >
              <Smile size={20} />
            </button>

            <button
              className={`chat-input-button chat-input-button--voice ${isRecording ? 'chat-input-button--recording' : ''}`}
              onClick={handleVoiceInput}
              title={isRecording ? 'Stop recording' : 'Voice input'}
              disabled={!isOnline}
            >
              <Mic size={20} />
            </button>

            <button
              className="chat-send-button"
              onClick={handleSendMessage}
              disabled={!isOnline || isProcessing || (!inputValue.trim() && selectedFiles.length === 0)}
              title="Send message"
            >
              <Send size={20} />
            </button>
          </div>

          {showEmojiPicker && (
            <div className="emoji-picker">
              <div className="emoji-picker__header">
                <button className="emoji-picker__tab emoji-picker__tab--active">
                  😀
                </button>
                <button className="emoji-picker__tab">🎉</button>
                <button className="emoji-picker__tab">❤️</button>
                <button className="emoji-picker__tab">👍</button>
              </div>
              <div className="emoji-picker__content">
                {['😀', '😂', '😍', '🤔', '👍', '👏', '🎉', '❤️', '🔥', '✨', '💯', '🚀'].map(emoji => (
                  <button
                    key={emoji}
                    className="emoji-picker__emoji"
                    onClick={() => {
                      setInputValue(prev => prev + emoji);
                      setShowEmojiPicker(false);
                      inputRef.current?.focus();
                    }}
                  >
                    {emoji}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>

      {isProcessing && (
        <div className="chat-processing-overlay">
          <div className="chat-processing-spinner" />
          <span>Processing your request...</span>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;
