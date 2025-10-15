/**
 * ErrorBoundary Component
 * Catches and handles React component errors with graceful fallback
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  // Small sanitizer for console logs to mitigate log injection (CWE-117).
  // Removes CR/LF and other control characters and truncates very long values.
  private static sanitizeForLog(value: unknown): string {
    try {
      let s: string;
      if (typeof value === 'string') {
        s = value;
      } else if (value instanceof Error) {
        // prefer message for errors to avoid huge stacks in logs
        s = value.message || String(value);
      } else {
        try {
          s = JSON.stringify(value);
        } catch {
          s = String(value);
        }
      }

      // strip CR/LF and other non-printable control characters
      s = s.replace(/[\r\n\x00-\x1F\x7F]+/g, ' ');

      // truncate to avoid extremely long log entries
      const MAX = 1000;
      if (s.length > MAX) s = s.slice(0, MAX) + '...';
      return s;
    } catch (e) {
      // Fallback to a safe string
      return '[unserializable]';
    }
  }

  // Sanitizer suitable for developer-facing display where newlines are useful.
  // This preserves newline characters but removes other control characters.
  private static sanitizeForDisplay(value: unknown): string {
    try {
      let s = '';
      if (typeof value === 'string') s = value;
      else if (value instanceof Error) s = (value.stack || value.message || String(value));
      else {
        try {
          s = JSON.stringify(value, null, 2);
        } catch {
          s = String(value);
        }
      }

      // remove control characters except LF (\n) and TAB (\t)
      s = s.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]+/g, '');

      const MAX_DISPLAY = 20000;
      if (s.length > MAX_DISPLAY) s = s.slice(0, MAX_DISPLAY) + '\n...[truncated]';
      return s;
    } catch (e) {
      return '[unserializable]';
    }
  }
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Sanitize any user-controllable content before logging to mitigate log injection
    try {
      const errMsg = ErrorBoundary.sanitizeForLog(error);
      const infoMsg = ErrorBoundary.sanitizeForLog(errorInfo?.componentStack);
      console.error('ErrorBoundary caught error:', errMsg, infoMsg);
    } catch (e) {
      // best-effort fallback
      console.error('ErrorBoundary caught error (unable to sanitize):', String(error));
    }
    
    this.setState({
      error,
      errorInfo,
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div 
          role="alert" 
          className="flex flex-col items-center justify-center min-h-[400px] p-8 bg-red-50 rounded-lg border-2 border-red-200"
        >
          <div className="text-center max-w-2xl">
            <svg
              className="w-16 h-16 mx-auto mb-4 text-red-500"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            
            <h2 className="text-2xl font-bold text-red-800 mb-2">
              Oops! Something went wrong
            </h2>
            
            <p className="text-red-600 mb-6">
              We encountered an unexpected error. Please try again or contact support if the problem persists.
            </p>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="text-left mb-6 p-4 bg-white rounded border border-red-300">
                <summary className="font-semibold cursor-pointer text-red-700 mb-2">
                  Error Details (Development Mode)
                </summary>
                <pre className="text-xs overflow-auto p-2 bg-gray-50 rounded">
                  <code className="text-red-600">
                            {ErrorBoundary.sanitizeForDisplay(this.state.error)}
                            {this.state.errorInfo ? '\n' + ErrorBoundary.sanitizeForDisplay(this.state.errorInfo.componentStack) : ''}
                  </code>
                </pre>
              </details>
            )}

            <button
              onClick={this.handleReset}
              className="px-6 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
              aria-label="Try again"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
