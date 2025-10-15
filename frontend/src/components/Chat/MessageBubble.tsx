import React, { useMemo } from 'react';
import styled, { css } from 'styled-components';
import { motion } from 'framer-motion';
import { Message, User } from '../../types/chat';
import { Avatar } from './Avatar';
import { CodeBlock } from './CodeBlock';

interface MessageBubbleProps {
  message: Message;
  currentUser: User;
}

const MessageWrapper = styled(motion.div)<{ $isCurrentUser: boolean }>`
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  margin-bottom: var(--spacing-2);
  max-width: 85%;
  
  ${props =>
    props.$isCurrentUser
      ? css`
          align-self: flex-end;
          flex-direction: row-reverse;
        `
      : css`
          align-self: flex-start;
        `}
`;

const Bubble = styled.div<{
  $isCurrentUser: boolean;
}>`
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-xl);
  position: relative;

  p {
    margin: 0;
    color: var(--text-primary);
  }

  ${props =>
    props.$isCurrentUser
      ? css`
          border-bottom-right-radius: var(--radius-sm);
          background: var(--accent);
          color: var(--btn-primary-text);
          p { color: var(--btn-primary-text); }
        `
      : css`
          border-bottom-left-radius: var(--radius-sm);
          background: var(--glass-bg);
          border: 1px solid var(--glass-border);
          box-shadow: var(--glass-shadow);
          backdrop-filter: blur(12px);
        `}
`;

const AvatarContainer = styled.div<{$isCurrentUser: boolean}>`
    margin: ${props => props.$isCurrentUser ? '0 0 0 12px' : '0 12px 0 0'};
`;

const MessageBubbleInner: React.FC<MessageBubbleProps> = ({ message, currentUser }) => {
  const isCurrentUser = message.user.id === currentUser.id;

  const content = useMemo(() => {
    if (message.codeBlocks && message.codeBlocks.length > 0) {
      return <CodeBlock block={message.codeBlocks[0]} />;
    }
    return <p>{message.content}</p>;
  }, [message.codeBlocks, message.content]);

  return (
    <MessageWrapper
      $isCurrentUser={isCurrentUser}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <AvatarContainer $isCurrentUser={isCurrentUser}>
        <Avatar src={message.user.avatar || ''} alt={message.user.name || 'User'} isOnline={true} />
      </AvatarContainer>
      <Bubble $isCurrentUser={isCurrentUser}>{content}</Bubble>
    </MessageWrapper>
  );
};

export const MessageBubble = React.memo(MessageBubbleInner, (prev, next) => {
  // Fast bail-out: same id and same content means no re-render
  if (prev.message.id !== next.message.id) return false;
  if (prev.message.content !== next.message.content) return false;
  if ((prev.message.codeBlocks?.length || 0) !== (next.message.codeBlocks?.length || 0)) return false;
  if (prev.currentUser.id !== next.currentUser.id) return false;
  return true;
});
