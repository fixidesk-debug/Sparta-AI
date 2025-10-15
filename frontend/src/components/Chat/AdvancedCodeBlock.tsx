/**
 * Advanced Code Block Component
 * Syntax highlighting with copy, collapse, and execute functionality
 */

import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CodeBlock as CodeBlockType } from '../../types/chat.types';

interface AdvancedCodeBlockProps {
  codeBlock: CodeBlockType;
  onExecute?: (code: string, language: string) => Promise<string>;
  onCopy?: () => void;
  messageId?: string;
}

export const AdvancedCodeBlock: React.FC<AdvancedCodeBlockProps> = ({
  codeBlock,
  onExecute,
  onCopy,
  messageId,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(codeBlock.isCollapsed);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionOutput, setExecutionOutput] = useState(codeBlock.output);
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(codeBlock.code);
      setIsCopied(true);
      onCopy?.();
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  const handleExecute = async () => {
    if (!onExecute || !codeBlock.canExecute) return;

    setIsExecuting(true);
    try {
      const output = await onExecute(codeBlock.code, codeBlock.language);
      setExecutionOutput(output);
    } catch (error) {
      setExecutionOutput(`Error: ${error}`);
    } finally {
      setIsExecuting(false);
    }
  };

  const getLanguageLabel = (lang: string): string => {
    const labels: Record<string, string> = {
      javascript: 'JavaScript',
      typescript: 'TypeScript',
      python: 'Python',
      jsx: 'React JSX',
      tsx: 'React TSX',
      sql: 'SQL',
      bash: 'Bash',
      json: 'JSON',
      css: 'CSS',
      html: 'HTML',
      markdown: 'Markdown',
    };
    return labels[lang] || lang.toUpperCase();
  };

  const lineCount = codeBlock.code.split('\n').length;
  const isLarge = lineCount > 20;

  return (
    <CodeBlockContainer>
      <CodeBlockHeader>
        <LeftSection>
          <LanguageBadge>
            <LanguageIcon>{getLanguageIcon(codeBlock.language)}</LanguageIcon>
            <LanguageLabel>{getLanguageLabel(codeBlock.language)}</LanguageLabel>
          </LanguageBadge>
          {codeBlock.fileName && (
            <FileName title={codeBlock.fileName}>
              📄 {codeBlock.fileName}
            </FileName>
          )}
          <LineCount>{lineCount} lines</LineCount>
        </LeftSection>

        <RightSection>
          {isLarge && (
            <IconButton
              onClick={() => setIsCollapsed(!isCollapsed)}
              title={isCollapsed ? 'Expand code' : 'Collapse code'}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isCollapsed ? '⬇️' : '⬆️'}
            </IconButton>
          )}
          {codeBlock.canExecute && (
            <ExecuteButton
              onClick={handleExecute}
              disabled={isExecuting}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {isExecuting ? (
                <>
                  <Spinner />
                  Running...
                </>
              ) : (
                <>
                  ▶️ Run
                </>
              )}
            </ExecuteButton>
          )}
          <IconButton
            onClick={handleCopy}
            title={isCopied ? 'Copied!' : 'Copy code'}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            $success={isCopied}
          >
            {isCopied ? '✅' : '📋'}
          </IconButton>
        </RightSection>
      </CodeBlockHeader>

      <AnimatePresence>
        {!isCollapsed && (
          <CodeContent
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <StyledSyntaxHighlighter
              language={codeBlock.language}
              style={vscDarkPlus}
              showLineNumbers
              customStyle={{
                margin: 0,
                padding: '16px',
                background: 'transparent',
                fontSize: '14px',
                lineHeight: '1.6',
              }}
              lineNumberStyle={{
                color: '#64748b',
                paddingRight: '16px',
                minWidth: '3em',
              }}
            >
              {codeBlock.code}
            </StyledSyntaxHighlighter>
          </CodeContent>
        )}
      </AnimatePresence>

      {isCollapsed && (
        <CollapsedPreview onClick={() => setIsCollapsed(false)}>
          <PreviewText>{codeBlock.code.split('\n').slice(0, 3).join('\n')}</PreviewText>
          <ExpandPrompt>Click to expand {lineCount} lines...</ExpandPrompt>
        </CollapsedPreview>
      )}

      {executionOutput && (
        <OutputContainer
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          <OutputHeader>
            <OutputLabel>
              ⚡ Output
              {codeBlock.executionTime && (
                <ExecutionTime>({codeBlock.executionTime}ms)</ExecutionTime>
              )}
            </OutputLabel>
            <IconButton
              onClick={() => setExecutionOutput(undefined)}
              title="Clear output"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              ❌
            </IconButton>
          </OutputHeader>
          <OutputContent>
            <OutputText>{executionOutput}</OutputText>
          </OutputContent>
        </OutputContainer>
      )}
    </CodeBlockContainer>
  );
};

// Helper function
const getLanguageIcon = (language: string): string => {
  const icons: Record<string, string> = {
    javascript: '🟨',
    typescript: '🔷',
    python: '🐍',
    jsx: '⚛️',
    tsx: '⚛️',
    sql: '🗄️',
    bash: '💻',
    json: '📦',
    css: '🎨',
    html: '🌐',
    markdown: '📝',
  };
  return icons[language] || '📄';
};

// Styled Components
const CodeBlockContainer = styled.div`
  margin: 12px 0;
  border-radius: 12px;
  overflow: hidden;
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 8px 32px rgba(10, 14, 39, 0.2);
`;

const CodeBlockHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(10, 14, 39, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  gap: 12px;
  flex-wrap: wrap;

  @media (max-width: 640px) {
    flex-direction: column;
    align-items: stretch;
  }
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;

  @media (max-width: 640px) {
    justify-content: flex-end;
  }
`;

const LanguageBadge = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: white;
`;

const LanguageIcon = styled.span`
  font-size: 14px;
`;

const LanguageLabel = styled.span``;

const FileName = styled.div`
  font-size: 13px;
  color: #94a3b8;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const LineCount = styled.div`
  font-size: 12px;
  color: #64748b;
`;

const IconButton = styled(motion.button)<{ $success?: boolean }>`
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: ${({ $success }) => ($success ? 'rgba(16, 185, 129, 0.2)' : 'transparent')};
  border: 1px solid ${({ $success }) => ($success ? '#10b981' : 'rgba(255, 255, 255, 0.2)')};
  color: ${({ $success }) => ($success ? '#10b981' : '#f8fafc')};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 150ms ease;

  &:hover {
    background: ${({ $success }) =>
      $success ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255, 255, 255, 0.1)'};
    border-color: ${({ $success }) => ($success ? '#10b981' : 'rgba(255, 255, 255, 0.3)')};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ExecuteButton = styled(motion.button)`
  padding: 6px 14px;
  border-radius: 8px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: 1px solid #10b981;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  transition: all 150ms ease;

  &:hover:not(:disabled) {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const Spinner = styled.div`
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
`;

const CodeContent = styled(motion.div)`
  overflow: hidden;
`;

const StyledSyntaxHighlighter = styled(SyntaxHighlighter)`
  && {
    background: #0f172a !important;
    font-family: 'JetBrains Mono', 'Fira Code', 'Monaco', monospace !important;
  }

  code {
    font-family: 'JetBrains Mono', 'Fira Code', 'Monaco', monospace !important;
  }
`;

const CollapsedPreview = styled.div`
  padding: 16px;
  background: #0f172a;
  cursor: pointer;
  transition: background 200ms ease;
  position: relative;

  &:hover {
    background: #1e293b;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 40px;
    background: linear-gradient(to bottom, transparent, #0f172a);
  }
`;

const PreviewText = styled.pre`
  margin: 0;
  font-family: 'JetBrains Mono', 'Fira Code', 'Monaco', monospace;
  font-size: 14px;
  color: #94a3b8;
  line-height: 1.6;
  overflow: hidden;
`;

const ExpandPrompt = styled.div`
  margin-top: 8px;
  font-size: 13px;
  color: #3b82f6;
  font-weight: 600;
  text-align: center;
`;

const OutputContainer = styled(motion.div)`
  margin-top: 1px;
  background: rgba(10, 14, 39, 0.8);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
`;

const OutputHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: rgba(16, 185, 129, 0.1);
  border-bottom: 1px solid rgba(16, 185, 129, 0.2);
`;

const OutputLabel = styled.div`
  font-size: 13px;
  font-weight: 600;
  color: #10b981;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ExecutionTime = styled.span`
  font-size: 11px;
  color: #64748b;
  font-weight: 400;
`;

const OutputContent = styled.div`
  padding: 16px;
  max-height: 300px;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;

    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
`;

const OutputText = styled.pre`
  margin: 0;
  font-family: 'JetBrains Mono', 'Fira Code', 'Monaco', monospace;
  font-size: 13px;
  color: #f8fafc;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
`;
