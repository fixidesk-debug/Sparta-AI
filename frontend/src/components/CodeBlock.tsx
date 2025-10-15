/**
 * CodeBlock Component
 * Displays syntax-highlighted code with copy functionality
 */

import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CodeBlock as CodeBlockType } from '../types/chat';

interface CodeBlockProps {
  code: CodeBlockType;
  theme?: 'light' | 'dark';
  showLineNumbers?: boolean;
  showCopyButton?: boolean;
  onExecute?: (code: string) => void;
  className?: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({
  code,
  theme = 'dark',
  showLineNumbers = true,
  showCopyButton = true,
  onExecute,
  className = '',
}) => {
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code.code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy code:', error);
    }
  };

  const handleExecute = () => {
    if (onExecute) {
      onExecute(code.code);
    }
  };

  const codeStyle = theme === 'dark' ? vscDarkPlus : vs;
  const shouldTruncate = code.code.split('\n').length > 20;

  return (
    <div className={`code-block-wrapper ${className}`} role="region" aria-label="Code block">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 text-gray-200 rounded-t-lg border-b border-gray-700">
        <div className="flex items-center gap-2">
          <svg
            className="w-5 h-5"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
          <span className="font-mono text-sm font-semibold">
            {code.language.toUpperCase()}
          </span>
          {code.filename && (
            <span className="text-sm text-gray-400">• {code.filename}</span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {code.isValid === false && code.error && (
            <span 
              className="text-xs text-red-400 flex items-center gap-1"
              role="alert"
              aria-label={`Code validation error: ${code.error}`}
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              Invalid
            </span>
          )}

          {shouldTruncate && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-xs text-blue-400 hover:text-blue-300 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1"
              {...(shouldTruncate ? { 'aria-expanded': isExpanded } : {})}
              aria-label={isExpanded ? 'Collapse code' : 'Expand code'}
            >
              {isExpanded ? 'Collapse' : 'Expand'}
            </button>
          )}

          {onExecute && code.isValid !== false && (
            <button
              onClick={handleExecute}
              className="text-xs text-green-400 hover:text-green-300 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 rounded px-2 py-1 flex items-center gap-1"
              aria-label="Execute code"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
              Run
            </button>
          )}

          {showCopyButton && (
            <button
              onClick={handleCopy}
              className="text-xs text-gray-400 hover:text-gray-200 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 rounded px-2 py-1"
              aria-label={copied ? 'Copied!' : 'Copy code to clipboard'}
            >
              {copied ? (
                <span className="flex items-center gap-1 text-green-400">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Copied!
                </span>
              ) : (
                <span className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy
                </span>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Code Display */}
      <div className={`relative ${shouldTruncate && !isExpanded ? 'max-h-96 overflow-hidden' : ''}`}>
        <SyntaxHighlighter
          language={code.language}
          style={codeStyle}
          showLineNumbers={showLineNumbers}
          wrapLines
          customStyle={{
            margin: 0,
            borderRadius: '0 0 0.5rem 0.5rem',
            fontSize: '0.875rem',
          }}
          codeTagProps={{
            style: {
              fontFamily: 'Menlo, Monaco, "Courier New", monospace',
            },
          }}
        >
          {code.code}
        </SyntaxHighlighter>
        
        {shouldTruncate && !isExpanded && (
          <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-gray-900 to-transparent pointer-events-none" />
        )}
      </div>

      {/* Error Display */}
      {code.error && code.isValid === false && (
        <div className="px-4 py-3 bg-red-900 bg-opacity-20 border-t border-red-800 rounded-b-lg" role="alert">
          <p className="text-sm text-red-400 font-mono">{code.error}</p>
        </div>
      )}
    </div>
  );
};
