/**
 * MessageInput Component
 * Text input with auto-resize, file attachment, and keyboard shortcuts
 */

import React, { useState, useRef, useCallback, KeyboardEvent, ChangeEvent } from 'react';
import { FileUpload } from './FileUpload';
import { Attachment } from '../types/chat';

interface MessageInputProps {
  onSendMessage: (content: string, attachments?: Attachment[]) => void;
  onTyping?: () => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
  allowAttachments?: boolean;
  className?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  onTyping,
  disabled = false,
  placeholder = 'Type your message...',
  maxLength = 5000,
  allowAttachments = true,
  className = '',
}) => {
  const [message, setMessage] = useState('');
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-resize textarea
  const adjustTextareaHeight = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, []);

  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLTextAreaElement>) => {
      const newValue = e.target.value;
      if (newValue.length <= maxLength) {
        setMessage(newValue);
        adjustTextareaHeight();

        // Trigger typing indicator
        if (onTyping && newValue.length > 0) {
          onTyping();
          
          // Debounce typing indicator
          if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
          }
          typingTimeoutRef.current = setTimeout(() => {
            // Stop typing indicator after 2 seconds of no input
          }, 2000);
        }
      }
    },
    [maxLength, onTyping, adjustTextareaHeight]
  );

  const handleSend = useCallback(() => {
    const trimmedMessage = message.trim();
    if (trimmedMessage || attachments.length > 0) {
      onSendMessage(trimmedMessage, attachments.length > 0 ? attachments : undefined);
      setMessage('');
      setAttachments([]);
      setShowFileUpload(false);
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  }, [message, attachments, onSendMessage]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      // Send on Ctrl+Enter or Cmd+Enter
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleSend();
      }
      // Allow Shift+Enter for new line
      else if (e.shiftKey && e.key === 'Enter') {
        // Default behavior - insert new line
      }
      // Send on Enter (without Shift)
      else if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const handleFileSelect = useCallback((files: File[]) => {
    // Convert File[] to Attachment[]
    const newAttachments: Attachment[] = files.map((file) => ({
      id: `${Date.now()}-${file.name}`,
      filename: file.name,
      name: file.name,
      size: file.size,
      type: file.type || 'application/octet-stream',
      uploadProgress: 0,
      uploadStatus: 'pending' as const,
    }));
    
    setAttachments((prev) => [...prev, ...newAttachments]);
    setShowFileUpload(false);
  }, []);

  const handleRemoveAttachment = useCallback((index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const characterCount = message.length;
  const isOverLimit = characterCount > maxLength;
  const canSend = (message.trim().length > 0 || attachments.length > 0) && !disabled && !isOverLimit;

  return (
    <div className={`message-input-container bg-white border-t border-gray-200 ${className}`}>
      {/* Attachments preview */}
      {attachments.length > 0 && (
        <div className="attachments-preview px-4 py-2 bg-gray-50 border-b border-gray-200">
          <div className="flex flex-wrap gap-2">
            {attachments.map((attachment, index) => (
              <div
                key={`${attachment.id}-${index}`}
                className="flex items-center gap-2 px-3 py-1 bg-white border border-gray-300 rounded-full text-sm"
              >
                <span className="text-gray-700 truncate max-w-xs">{attachment.filename}</span>
                <button
                  type="button"
                  onClick={() => handleRemoveAttachment(index)}
                  className="text-red-500 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
                  aria-label={`Remove ${attachment.filename}`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* File upload modal */}
      {showFileUpload && (
        <div className="file-upload-modal px-4 py-3 border-b border-gray-200">
          <FileUpload
            onFileSelect={handleFileSelect}
            maxFiles={5}
            className="mb-2"
          />
          <button
            type="button"
            onClick={() => setShowFileUpload(false)}
            className="text-sm text-gray-600 hover:text-gray-800 focus:outline-none focus:underline"
          >
            Cancel
          </button>
        </div>
      )}

      {/* Input area */}
      <div className="input-area flex items-end gap-2 px-4 py-3">
        {/* Attachment button */}
        {allowAttachments && (
          <button
            type="button"
            onClick={() => setShowFileUpload(!showFileUpload)}
            disabled={disabled}
            className="attachment-button flex-shrink-0 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Attach file"
            title="Attach file"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
              />
            </svg>
          </button>
        )}

        {/* Textarea */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={placeholder}
            rows={1}
            maxLength={maxLength}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed min-h-[44px]"
            aria-label="Message input"
          />
          
          {/* Character count */}
          {characterCount > maxLength * 0.8 && (
            <div
              className={`absolute bottom-1 right-2 text-xs ${
                isOverLimit ? 'text-red-500' : 'text-gray-400'
              }`}
              role="status"
              aria-live="polite"
            >
              {characterCount}/{maxLength}
            </div>
          )}
        </div>

        {/* Send button */}
        <button
          type="button"
          onClick={handleSend}
          disabled={!canSend}
          className="send-button flex-shrink-0 p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          aria-label="Send message"
          title="Send message (Enter or Ctrl+Enter)"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>

      {/* Keyboard shortcuts hint */}
      <div className="px-4 pb-2 text-xs text-gray-500">
        Press <kbd className="px-1 py-0.5 bg-gray-100 border border-gray-300 rounded">Enter</kbd> to send, 
        <kbd className="px-1 py-0.5 bg-gray-100 border border-gray-300 rounded ml-1">Shift+Enter</kbd> for new line
      </div>
    </div>
  );
};
