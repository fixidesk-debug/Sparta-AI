/**
 * CodeBlock Component
 * Renders syntax-highlighted code with a copy button.
 * 
 * Dependencies:
 * - react-syntax-highlighter: `npm install react-syntax-highlighter`
 * - @types/react-syntax-highlighter: `npm install @types/react-syntax-highlighter`
 */
import React from 'react';
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
  const [isCopied, setIsCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(block.code);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <CodeWrapper>
      <Header>
        <span>{block.language}</span>
        <CopyButton onClick={handleCopy}>
          {isCopied ? 'Copied!' : 'Copy'}
        </CopyButton>
      </Header>
      <SyntaxHighlighter language={block.language} style={vscDarkPlus} customStyle={{ margin: 0 }}>
        {block.code}
      </SyntaxHighlighter>
    </CodeWrapper>
  );
};
