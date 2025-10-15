/**
 * CodeBlock Component
 * Renders syntax-highlighted code with a copy button.
 * 
 * Dependencies:
 * - react-syntax-highlighter: `npm install react-syntax-highlighter`
 * - @types/react-syntax-highlighter: `npm install @types/react-syntax-highlighter`
 */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import styled from 'styled-components';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CodeBlock as CodeBlockType } from '../../types/chat';

interface CodeBlockProps {
  block: CodeBlockType;
}

const CodeWrapper = styled.div`
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  margin: var(--spacing-2) 0;
  background-color: #1a1f3a; /* Fallback */
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-1) var(--spacing-2);
  background-color: rgba(0,0,0,0.2);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
`;

const CopyButton = styled.button`
  background: var(--glass-bg);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  padding: 4px 8px;
  cursor: pointer;
  transition: background-color var(--transition-fast);

  &:hover {
    background-color: var(--accent);
    color: var(--btn-primary-text);
  }
`;

export const CodeBlock: React.FC<CodeBlockProps> = ({ block }) => {
  const [isCopied, setIsCopied] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Small sanitizer for attributes and text shown to users
  const sanitize = (s: unknown, max = 200) =>
    String(s ?? '')
      .replace(/[\r\n]+/g, ' ')
      .trim()
      .slice(0, max);

  const customStyle = useMemo(() => ({ margin: 0 as const }), []);

  const doFallbackCopy = (text: string) => {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'absolute';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    const sel = document.getSelection();
    const prevRange = sel && sel.rangeCount > 0 ? sel.getRangeAt(0) : null;
    ta.select();
    try {
      document.execCommand('copy');
    } finally {
      document.body.removeChild(ta);
      if (prevRange && sel) {
        sel.removeAllRanges();
        sel.addRange(prevRange);
      }
    }
  };

  const handleCopy = useCallback(async () => {
    const code = String(block.code ?? '');
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(code);
      } else {
        doFallbackCopy(code);
      }
      setIsCopied(true);
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      // Don't throw to avoid breaking UI; log sanitized error for diagnostics
      // eslint-disable-next-line no-console
      console.error('CodeBlock copy failed:', String(err ?? 'unknown'));
      // Attempt fallback once more
      try {
        doFallbackCopy(code);
        setIsCopied(true);
        if (timerRef.current) clearTimeout(timerRef.current);
        timerRef.current = setTimeout(() => setIsCopied(false), 2000);
      } catch (e) {
        // final silent failure
      }
    }
  }, [block.code]);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    };
  }, []);

  const highlighted = useMemo(
    () => (
      <SyntaxHighlighter language={sanitize(block.language)} style={vscDarkPlus} customStyle={customStyle}>
        {String(block.code ?? '')}
      </SyntaxHighlighter>
    ),
    [block.code, block.language, customStyle]
  );

  return (
    <CodeWrapper>
      <Header>
        <span>{sanitize(block.language)}</span>
        <CopyButton onClick={handleCopy} aria-label={`Copy ${sanitize(block.language)} code`}>
          {isCopied ? 'Copied!' : 'Copy'}
        </CopyButton>
      </Header>
      {highlighted}
    </CodeWrapper>
  );
};
