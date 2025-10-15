/**
 * TypingIndicator Component
 * Displays animated typing indicator for real-time feedback
 */

import React from 'react';

interface TypingIndicatorProps {
  isTyping: boolean;
  userName?: string;
  className?: string;
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({
  isTyping,
  userName = 'AI',
  className = '',
}) => {
  if (!isTyping) return null;

  return (
    <div
      className={`typing-indicator flex items-center gap-2 px-4 py-2 ${className}`}
      role="status"
      aria-live="polite"
      aria-label={`${userName} is typing`}
    >
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-500">{userName} is typing</span>
        <div className="flex gap-1">
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
          <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  );
};
