import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Message } from './types';
import { CodeBlock } from './CodeBlock';
import { ChartPreview } from './ChartPreview';

const MessageWrapper = styled(motion.div)<{ $isUser: boolean }>`
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  flex-direction: ${p => p.$isUser ? 'row-reverse' : 'row'};
  align-items: flex-start;
`;

const Avatar = styled.div<{ $isOnline: boolean }>`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  position: relative;
  flex-shrink: 0;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    right: 0;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: ${p => p.$isOnline ? '#10b981' : '#6b7280'};
    border: 2px solid #0a0e27;
  }
`;

const BubbleContainer = styled.div<{ $isUser: boolean; $type: string }>`
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Bubble = styled.div<{ $isUser: boolean; $type: string }>`
  padding: 16px;
  border-radius: 12px;
  background: ${p => {
    if (p.$isUser) return 'linear-gradient(135deg, #2563eb, #3b82f6)';
    if (p.$type === 'error') return 'rgba(239, 68, 68, 0.1)';
    return 'rgba(255, 255, 255, 0.08)';
  }};
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #f8fafc;
  font-size: 14px;
  line-height: 1.6;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transition: all 250ms cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    background: ${p => p.$isUser ? 'linear-gradient(135deg, #3b82f6, #60a5fa)' : 'rgba(255, 255, 255, 0.12)'};
    transform: translateY(-1px);
  }
`;

const MessageActions = styled.div`
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 200ms;
  
  ${MessageWrapper}:hover & {
    opacity: 1;
  }
`;

const ActionButton = styled.button`
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 6px;
  padding: 4px 8px;
  color: #cbd5e1;
  font-size: 12px;
  cursor: pointer;
  transition: all 150ms;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    color: #f8fafc;
  }
`;

const Timestamp = styled.span`
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
`;

export const ChatMessage: React.FC<{ message: Message }> = ({ message }) => {
  const [showActions, setShowActions] = useState(false);
  const isUser = message.sender.id !== 'ai';

  return (
    <MessageWrapper
      $isUser={isUser}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <Avatar $isOnline={message.sender.isOnline} />
      
      <BubbleContainer $isUser={isUser}>
        <Bubble $isUser={isUser} $type={message.type}>
          {message.content}
        </Bubble>
        
        {message.codeBlocks?.map((block, i) => (
          <CodeBlock key={i} {...block} />
        ))}
        
        {message.charts?.map((chart, i) => (
          <ChartPreview key={i} {...chart} />
        ))}
        
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <Timestamp>{new Date(message.timestamp).toLocaleTimeString()}</Timestamp>
          {showActions && (
            <MessageActions>
              <ActionButton>Edit</ActionButton>
              <ActionButton>React</ActionButton>
              <ActionButton>Reply</ActionButton>
              <ActionButton>Share</ActionButton>
            </MessageActions>
          )}
        </div>
      </BubbleContainer>
    </MessageWrapper>
  );
};
