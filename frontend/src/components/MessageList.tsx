/**
 * MessageList Component
 * Virtualized scrollable message display with auto-scroll and date grouping
 * 
 * Dependencies required (install with npm):
 * - react-window
 * - react-virtualized-auto-sizer
 * - @types/react-window
 * - @types/react-virtualized-auto-sizer
 */

import React, { useRef, useEffect, useCallback } from 'react';
// @ts-ignore - Install: npm install react-window @types/react-window
import { VariableSizeList as List } from 'react-window';
// @ts-ignore - Install: npm install react-virtualized-auto-sizer @types/react-virtualized-auto-sizer
import AutoSizer from 'react-virtualized-auto-sizer';
import { Message, MessageStatus } from '../types/chat';
import { CodeBlock } from './CodeBlock';
import { ChartDisplay } from './ChartDisplay';

interface MessageListProps {
  messages: Message[];
  currentUserId: string;
  isLoading?: boolean;
  onExecuteCode?: (code: string) => void;
  className?: string;
}

// Format timestamp
const formatTime = (timestamp: Date): string => {
  return new Date(timestamp).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });
};

// Get status icon
const getStatusIcon = (status: MessageStatus): JSX.Element | null => {
  switch (status) {
    case 'sending':
      return (
        <svg className="w-4 h-4 text-gray-400 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      );
    case 'sent':
      return (
        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      );
    case 'error':
      return (
        <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      );
    default:
      return null;
  }
};

// Individual message component
const MessageItem: React.FC<{
  message: Message;
  isOwnMessage: boolean;
  onExecuteCode?: (code: string) => void;
}> = ({ message, isOwnMessage, onExecuteCode }) => {
  const messageClass = isOwnMessage
    ? 'ml-auto bg-blue-500 text-white'
    : 'mr-auto bg-gray-100 text-gray-900';

  return (
    <div className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className="max-w-[70%]">
        {/* Sender info */}
        {!isOwnMessage && (
          <div className="flex items-center gap-2 mb-1 px-1">
            <span className="text-sm font-medium text-gray-700">{message.user.name}</span>
            <span className="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
          </div>
        )}

        {/* Message bubble */}
        <div className={`rounded-lg px-4 py-2 ${messageClass}`}>
          {/* Text content */}
          {message.content && <p className="whitespace-pre-wrap break-words">{message.content}</p>}

          {/* Code blocks */}
          {message.codeBlocks && message.codeBlocks.length > 0 && (
            <div className="mt-2 space-y-2">
              {message.codeBlocks.map((codeBlock, index) => (
                <CodeBlock
                  key={`${message.id}-code-${index}`}
                  code={codeBlock}
                  onExecute={codeBlock.isValid && onExecuteCode ? () => onExecuteCode(codeBlock.code) : undefined}
                />
              ))}
            </div>
          )}

          {/* Visualizations */}
          {message.visualizations && message.visualizations.length > 0 && (
            <div className="mt-2 space-y-2">
              {message.visualizations.map((viz, index) => (
                <ChartDisplay key={`${message.id}-viz-${index}`} visualization={viz} />
              ))}
            </div>
          )}

          {/* Attachments */}
          {message.attachments && message.attachments.length > 0 && (
            <div className="mt-2 space-y-1">
              {message.attachments.map((attachment, index) => (
                <a
                  key={`${message.id}-attachment-${index}`}
                  href={attachment.url}
                  download={attachment.filename}
                  className="flex items-center gap-2 p-2 bg-white bg-opacity-10 rounded hover:bg-opacity-20 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  <span className="text-sm">{attachment.filename}</span>
                  <span className="text-xs opacity-70">({Math.round(attachment.size / 1024)} KB)</span>
                </a>
              ))}
            </div>
          )}

          {/* Error message */}
          {message.error && (
            <div className="mt-2 p-2 bg-red-100 text-red-800 rounded text-sm">
              <strong>Error:</strong> {message.error}
            </div>
          )}
        </div>

        {/* Status and timestamp for own messages */}
        {isOwnMessage && (
          <div className="flex items-center justify-end gap-1 mt-1 px-1">
            <span className="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
            {getStatusIcon(message.status)}
          </div>
        )}
      </div>
    </div>
  );
};

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  currentUserId,
  isLoading = false,
  onExecuteCode,
  className = '',
}) => {
  const listRef = useRef<List>(null);
  const shouldAutoScrollRef = useRef(true);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (shouldAutoScrollRef.current && listRef.current && messages.length > 0) {
      listRef.current.scrollToItem(messages.length - 1, 'end');
    }
  }, [messages.length]);

  // Track if user is scrolled to bottom
  const handleScroll = useCallback(({ scrollOffset, scrollUpdateWasRequested }: any) => {
    // Only update auto-scroll if user manually scrolled
    if (!scrollUpdateWasRequested) {
      const list = listRef.current;
      if (list) {
        const { scrollHeight } = (list as any)._outerRef;
        const isAtBottom = scrollHeight - scrollOffset - 600 < 100; // 100px threshold
        shouldAutoScrollRef.current = isAtBottom;
      }
    }
  }, []);

  // Scroll to bottom manually
  const scrollToBottom = useCallback(() => {
    if (listRef.current && messages.length > 0) {
      listRef.current.scrollToItem(messages.length - 1, 'end');
      shouldAutoScrollRef.current = true;
    }
  }, [messages.length]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className={`message-list-empty flex flex-col items-center justify-center h-full text-gray-500 ${className}`}>
        <svg className="w-16 h-16 mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
        <p className="text-lg font-medium">No messages yet</p>
        <p className="text-sm">Start a conversation to analyze your data</p>
      </div>
    );
  }

  return (
    <div className={`message-list-container relative h-full ${className}`}>
      <AutoSizer>
        {({ height, width }: { height: number; width: number }) => (
          <List
            ref={listRef}
            height={height}
            itemCount={messages.length}
            itemSize={() => 150} // Estimated size, adjust as needed
            width={width}
            onScroll={handleScroll}
            className="message-list-scroll px-4"
          >
            {({ index, style }: { index: number; style: React.CSSProperties }) => {
              const message = messages[index];
              const isOwnMessage = message.user.id === currentUserId;

              return (
                // NOTE: Inline style is required by react-window for dynamic positioning
                // Do not remove - this is how virtualization calculates item positions
                // eslint-disable-next-line react/forbid-dom-props
                <div style={style}>
                  <MessageItem message={message} isOwnMessage={isOwnMessage} onExecuteCode={onExecuteCode} />
                </div>
              );
            }}
          </List>
        )}
      </AutoSizer>

      {/* Loading indicator */}
      {isLoading && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 px-4 py-2 bg-gray-800 text-white rounded-full shadow-lg flex items-center gap-2">
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span className="text-sm">Processing...</span>
        </div>
      )}

      {/* Scroll to bottom button */}
      {!shouldAutoScrollRef.current && (
        <button
          type="button"
          onClick={scrollToBottom}
          className="absolute bottom-4 right-4 p-3 bg-blue-500 text-white rounded-full shadow-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          aria-label="Scroll to bottom"
          title="Scroll to bottom"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>
      )}
    </div>
  );
};
