import React from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';

const TypingAnimation = keyframes`
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
`;

const TypingIndicatorWrapper = styled(motion.div)`
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: var(--glass-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
`;

const Dot = styled.div`
  width: 8px;
  height: 8px;
  margin: 0 2px;
  background-color: var(--text-secondary);
  border-radius: 50%;
  animation: ${TypingAnimation} 1.4s infinite ease-in-out both;

  &:nth-child(1) { animation-delay: -0.32s; }
  &:nth-child(2) { animation-delay: -0.16s; }
`;

export const TypingIndicator: React.FC = () => {
  return (
    <TypingIndicatorWrapper
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
    >
      <Dot />
      <Dot />
      <Dot />
    </TypingIndicatorWrapper>
  );
};
