import React, { useState, useCallback } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Message, User } from '../../types/chat.types';
import { AdvancedMessageBubble } from './AdvancedMessageBubble';

// ==================== Types ====================

export interface ThreadedMessage extends Message {
  replies?: ThreadedMessage[];
  replyCount?: number;
  isThreadRoot?: boolean;
}

export interface MessageThreadProps {
  message: ThreadedMessage;
  currentUser: User;
  allUsers: User[];
  depth?: number;
  maxDepth?: number;
  onReply?: (parentId: string, content: string) => void;
  onEdit?: (messageId: string, content: string) => void;
  onDelete?: (messageId: string) => void;
  onReaction?: (messageId: string, emoji: string) => void;
  onThreadToggle?: (messageId: string, isExpanded: boolean) => void;
}

export interface ThreadViewProps {
  rootMessage: ThreadedMessage;
  currentUser: User;
  allUsers: User[];
  onClose?: () => void;
  onReply?: (parentId: string, content: string) => void;
  onEdit?: (messageId: string, content: string) => void;
  onDelete?: (messageId: string) => void;
  onReaction?: (messageId: string, emoji: string) => void;
}

// ==================== Styled Components ====================

const ThreadContainer = styled(motion.div)<{ $depth: number }>`
  margin-left: ${props => props.$depth > 0 ? '32px' : '0'};
  position: relative;

  ${props => props.$depth > 0 && `
    &::before {
      content: '';
      position: absolute;
      left: -20px;
      top: 0;
      bottom: 0;
      width: 2px;
      background: linear-gradient(
        to bottom,
        rgba(59, 130, 246, 0.3),
        rgba(139, 92, 246, 0.1)
      );
      border-radius: 2px;
    }
  `}

  @media (max-width: 768px) {
    margin-left: ${props => props.$depth > 0 ? '16px' : '0'};

    ${props => props.$depth > 0 && `
      &::before {
        left: -10px;
        width: 1px;
      }
    `}
  }
`;

const MessageWrapper = styled.div`
  margin-bottom: 12px;
`;

const ThreadToggle = styled(motion.button)`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin: 8px 0 8px 32px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(59, 130, 246, 0.5);
    transform: scale(1.02);
  }

  &:active {
    transform: scale(0.98);
  }

  svg {
    width: 16px;
    height: 16px;
    transition: transform 0.2s ease;
  }

  &[data-expanded="true"] svg {
    transform: rotate(90deg);
  }

  @media (max-width: 768px) {
    margin-left: 16px;
    padding: 6px 10px;
    font-size: 12px;
  }
`;

const ReplyCount = styled.span`
  padding: 2px 6px;
  background: rgba(59, 130, 246, 0.2);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: rgba(59, 130, 246, 1);
`;

const RepliesContainer = styled(motion.div)`
  margin-top: 8px;
`;

const ThreadDepthIndicator = styled.div<{ $depth: number }>`
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 8px 0 8px 32px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);

  @media (max-width: 768px) {
    margin-left: 16px;
  }
`;

const DepthDot = styled.div<{ $active: boolean }>`
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: ${props => props.$active 
    ? 'rgba(59, 130, 246, 0.6)' 
    : 'rgba(255, 255, 255, 0.2)'};
`;

const MaxDepthNotice = styled.div`
  margin: 8px 0 8px 32px;
  padding: 8px 12px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 8px;
  font-size: 12px;
  color: rgba(245, 158, 11, 1);

  @media (max-width: 768px) {
    margin-left: 16px;
  }
`;

// Thread View (Full Screen Modal)
const ThreadViewOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;

  @media (max-width: 768px) {
    padding: 0;
    align-items: flex-end;
  }
`;

const ThreadViewContainer = styled(motion.div)`
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  background: rgba(17, 24, 39, 0.95);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.4);

  @media (max-width: 768px) {
    max-width: 100%;
    max-height: 85vh;
    border-radius: 16px 16px 0 0;
  }
`;

const ThreadHeader = styled.div`
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.02);
`;

const ThreadTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ThreadIcon = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, 
    rgba(59, 130, 246, 0.2), 
    rgba(139, 92, 246, 0.2)
  );
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
`;

const ThreadTitleText = styled.div`
  h3 {
    font-size: 18px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.95);
    margin: 0 0 4px 0;
  }

  p {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.5);
    margin: 0;
  }
`;

const CloseButton = styled(motion.button)`
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.9);
  }
`;

const ThreadContent = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 24px;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;

    &:hover {
      background: rgba(255, 255, 255, 0.15);
    }
  }
`;

const Breadcrumb = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);

  span {
    color: rgba(255, 255, 255, 0.4);
  }

  strong {
    color: rgba(59, 130, 246, 0.9);
    font-weight: 500;
  }
`;

const ParticipantsList = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
`;

const ParticipantLabel = styled.span`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-right: 4px;
`;

const ParticipantAvatars = styled.div`
  display: flex;
  margin-left: -8px;

  > * {
    margin-left: -8px;
    border: 2px solid rgba(17, 24, 39, 0.95);
  }
`;

const ParticipantAvatar = styled.div<{ $color: string }>`
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: ${props => props.$color};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: white;
  position: relative;
  z-index: 1;
  transition: transform 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    z-index: 2;
  }
`;

// ==================== Helper Functions ====================

const getUniqueParticipants = (message: ThreadedMessage): User[] => {
  const participantMap = new Map<string, User>();
  
  const addParticipant = (msg: ThreadedMessage) => {
    participantMap.set(msg.sender.id, msg.sender);
    msg.replies?.forEach(addParticipant);
  };
  
  addParticipant(message);
  return Array.from(participantMap.values());
};

const countTotalReplies = (message: ThreadedMessage): number => {
  if (!message.replies || message.replies.length === 0) return 0;
  return message.replies.reduce((total, reply) => {
    return total + 1 + countTotalReplies(reply);
  }, 0);
};

const getUserColor = (userId: string): string => {
  const colors = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  ];
  const index = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
  return colors[index];
};

// ==================== MessageThread Component ====================

export const MessageThread: React.FC<MessageThreadProps> = ({
  message,
  currentUser,
  allUsers,
  depth = 0,
  maxDepth = 5,
  onReply,
  onEdit,
  onDelete,
  onReaction,
  onThreadToggle,
}) => {
  const [isExpanded, setIsExpanded] = useState(depth < 2); // Auto-expand first 2 levels
  const hasReplies = message.replies && message.replies.length > 0;
  const replyCount = message.replyCount || countTotalReplies(message);
  const isMaxDepth = depth >= maxDepth;

  const handleToggle = useCallback(() => {
    const newExpanded = !isExpanded;
    setIsExpanded(newExpanded);
    onThreadToggle?.(message.id, newExpanded);
  }, [isExpanded, message.id, onThreadToggle]);

  return (
    <ThreadContainer
      $depth={depth}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
    >
      <MessageWrapper>
        <AdvancedMessageBubble
          message={message}
          currentUser={currentUser}
          allUsers={allUsers}
          onEdit={onEdit ? (id) => onEdit(id, '') : undefined}
          onDelete={onDelete}
          onReaction={onReaction}
          onReply={onReply ? (id) => onReply(id, '') : undefined}
          showThreadIndicator={hasReplies}
          replyCount={replyCount}
        />
      </MessageWrapper>

      {hasReplies && (
        <>
          <ThreadToggle
            onClick={handleToggle}
            data-expanded={isExpanded}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <svg viewBox="0 0 16 16" fill="currentColor">
              <path d="M6 4l4 4-4 4" stroke="currentColor" strokeWidth="2" fill="none" />
            </svg>
            {isExpanded ? 'Hide' : 'Show'} {replyCount} {replyCount === 1 ? 'reply' : 'replies'}
            {!isExpanded && <ReplyCount>{replyCount}</ReplyCount>}
          </ThreadToggle>

          {depth > 0 && depth < maxDepth && (
            <ThreadDepthIndicator $depth={depth}>
              {Array.from({ length: maxDepth }).map((_, i) => (
                <DepthDot key={i} $active={i <= depth} />
              ))}
              <span>Level {depth}</span>
            </ThreadDepthIndicator>
          )}

          <AnimatePresence>
            {isExpanded && (
              <RepliesContainer
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                {message.replies!.map((reply) => (
                  isMaxDepth ? (
                    <MaxDepthNotice key={reply.id}>
                      ⚠️ Maximum thread depth reached. View in thread view for deeper conversations.
                    </MaxDepthNotice>
                  ) : (
                    <MessageThread
                      key={reply.id}
                      message={reply}
                      currentUser={currentUser}
                      allUsers={allUsers}
                      depth={depth + 1}
                      maxDepth={maxDepth}
                      onReply={onReply}
                      onEdit={onEdit}
                      onDelete={onDelete}
                      onReaction={onReaction}
                      onThreadToggle={onThreadToggle}
                    />
                  )
                ))}
              </RepliesContainer>
            )}
          </AnimatePresence>
        </>
      )}
    </ThreadContainer>
  );
};

// ==================== ThreadView Component (Full Screen) ====================

export const ThreadView: React.FC<ThreadViewProps> = ({
  rootMessage,
  currentUser,
  allUsers,
  onClose,
  onReply,
  onEdit,
  onDelete,
  onReaction,
}) => {
  const participants = getUniqueParticipants(rootMessage);
  const totalReplies = countTotalReplies(rootMessage);

  return (
    <ThreadViewOverlay
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <ThreadViewContainer
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <ThreadHeader>
          <ThreadTitle>
            <ThreadIcon>💬</ThreadIcon>
            <ThreadTitleText>
              <h3>Thread</h3>
              <p>{totalReplies} {totalReplies === 1 ? 'reply' : 'replies'} • {participants.length} {participants.length === 1 ? 'participant' : 'participants'}</p>
            </ThreadTitleText>
          </ThreadTitle>
          <CloseButton
            onClick={onClose}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" />
            </svg>
          </CloseButton>
        </ThreadHeader>

        <ThreadContent>
          <Breadcrumb>
            <span>📍</span> Started by <strong>{rootMessage.sender.name}</strong> <span>•</span> {new Date(rootMessage.timestamp).toLocaleString()}
          </Breadcrumb>

          <MessageThread
            message={rootMessage}
            currentUser={currentUser}
            allUsers={allUsers}
            depth={0}
            maxDepth={99} // No depth limit in thread view
            onReply={onReply}
            onEdit={onEdit}
            onDelete={onDelete}
            onReaction={onReaction}
          />

          {participants.length > 0 && (
            <ParticipantsList>
              <ParticipantLabel>Participants:</ParticipantLabel>
              <ParticipantAvatars>
                {participants.map(user => (
                  <ParticipantAvatar
                    key={user.id}
                    $color={getUserColor(user.id)}
                    title={user.name}
                  >
                    {user.name.charAt(0).toUpperCase()}
                  </ParticipantAvatar>
                ))}
              </ParticipantAvatars>
            </ParticipantsList>
          )}
        </ThreadContent>
      </ThreadViewContainer>
    </ThreadViewOverlay>
  );
};

export default MessageThread;
