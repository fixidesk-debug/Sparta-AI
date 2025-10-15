import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

const CodeContainer = styled.div`
  background: rgba(10, 14, 39, 0.8);
  backdrop-filter: blur(12px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
`;

const CodeHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

const Language = styled.span`
  font-size: 12px;
  color: #60a5fa;
  font-weight: 500;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 8px;
`;

const IconButton = styled.button`
  background: transparent;
  border: none;
  color: #cbd5e1;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  transition: all 150ms;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #f8fafc;
  }
`;

const CodeContent = styled.pre<{ $collapsed: boolean }>`
  margin: 0;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  line-height: 1.5;
  color: #e2e8f0;
  overflow-x: auto;
  max-height: ${p => p.$collapsed ? '0' : '400px'};
  transition: max-height 300ms;
`;

const CopyNotification = styled(motion.div)`
  position: absolute;
  top: 8px;
  right: 8px;
  background: #10b981;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
`;

interface CodeBlockProps {
  language: string;
  code: string;
  runnable: boolean;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ language, code, runnable }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <CodeContainer style={{ position: 'relative' }}>
      <CodeHeader>
        <Language>{language}</Language>
        <ButtonGroup>
          <IconButton onClick={() => setCollapsed(!collapsed)}>
            {collapsed ? 'Expand' : 'Collapse'}
          </IconButton>
          <IconButton onClick={handleCopy}>Copy</IconButton>
          {runnable && <IconButton>▶ Run</IconButton>}
        </ButtonGroup>
      </CodeHeader>
      <CodeContent $collapsed={collapsed}>{code}</CodeContent>
      
      <AnimatePresence>
        {copied && (
          <CopyNotification
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            Copied!
          </CopyNotification>
        )}
      </AnimatePresence>
    </CodeContainer>
  );
};
