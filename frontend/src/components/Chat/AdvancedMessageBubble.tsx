/**
 * Advanced Message Bubble with Enhanced Features
 * Sophisticated message display with all requested features
 */

import React, { useMemo, useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Message, User, MessageType } from '../../types/chat.types';

/**
 * Handler invoked for message-level actions (edit, delete, reply, share).
 * Accepts the message ID for the target message.
 */
type MessageAction = (messageId: string) => void;

/**
 * Handler invoked for reaction actions. Receives message ID and the reaction emoji/type.
 */
type ReactionAction = (messageId: string, emoji: string) => void;

/**
 * Props for the AdvancedMessageBubble component.
 * Contains the message to render, the current user, optional global user list,
 * and a collection of optional handlers for user interactions.
 */
interface AdvancedMessageBubbleProps {
  message: Message;
  currentUser: User;
  allUsers?: User[];
  onEdit?: MessageAction;
  onDelete?: MessageAction;
  onReact?: ReactionAction;
  onReaction?: ReactionAction;
  onReply?: MessageAction;
  onShare?: MessageAction;
  showActions?: boolean;
  showThreadIndicator?: boolean;
  replyCount?: number;
}

export const AdvancedMessageBubble: React.FC<AdvancedMessageBubbleProps> = ({
  message,
  currentUser,
  allUsers,
  onEdit,
  onDelete,
  onReact,
  onReaction,
  onReply,
  onShare,
  showActions = true,
  showThreadIndicator,
  replyCount,
}) => {
  const [showActionMenu, setShowActionMenu] = useState(false);
  const isOwnMessage = message.sender.id === currentUser.id;
  const isAI = message.sender.role === 'ai';
  
  // Merge onReact and onReaction handlers (stable reference)
  const handleReaction = useMemo(() => onReaction || onReact, [onReaction, onReact]);

  // Memoize rendered content to avoid re-computing JSX each render
  const contentNodes = useMemo(
    () => renderMessageContent(message.content, message.mentions),
    [message.id, message.content, message.mentions?.length]
  );

  // Memoize reactions rendering
  const reactionNodes = useMemo(() => {
    if (!message.reactions || message.reactions.length === 0) return null;
    return renderReactions(message.reactions, currentUser.id, handleReaction as any, message.id);
  }, [message.id, message.reactions?.length, currentUser.id, handleReaction]);

  return (
    <MessageContainer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      $isOwnMessage={isOwnMessage}
      onMouseEnter={() => setShowActionMenu(true)}
      onMouseLeave={() => setShowActionMenu(false)}
    >
      {!isOwnMessage && (
        <AvatarWrapper>
          <Avatar
            src={message.sender.avatar || '/default-avatar.png'}
            alt={message.sender.name}
          />
          <StatusIndicator $status={message.sender.status} />
        </AvatarWrapper>
      )}

      <MessageContent $isOwnMessage={isOwnMessage}>
        <MessageHeader $isOwnMessage={isOwnMessage}>
          <SenderInfo>
            <SenderName $role={message.sender.role}>
              {message.sender.name}
              {message.sender.role === 'ai' && <AIBadge>AI</AIBadge>}
            </SenderName>
            <Timestamp>{formatTime(message.timestamp)}</Timestamp>
          </SenderInfo>
          <MessageMetadata>
            {message.isEdited && <EditedBadge>(edited)</EditedBadge>}
            {message.isPinned && <PinIcon>📌</PinIcon>}
            <StatusDot $status={message.status} />
          </MessageMetadata>
        </MessageHeader>

        {message.type !== 'query' && (
          <TypeBadge $type={message.type}>
            {getTypeIcon(message.type)} {message.type}
          </TypeBadge>
        )}

        <Bubble $isOwnMessage={isOwnMessage} $isAI={isAI} $type={message.type}>
          <MessageText>{contentNodes}</MessageText>

          {message.metadata && (
            <MetadataFooter>
              {message.metadata.modelUsed && (
                <MetadataItem>
                  <MetadataIcon>🤖</MetadataIcon>
                  {message.metadata.modelUsed}
                </MetadataItem>
              )}
              {message.metadata.tokensUsed && (
                <MetadataItem>
                  <MetadataIcon>🎯</MetadataIcon>
                  {message.metadata.tokensUsed.toLocaleString()} tokens
                </MetadataItem>
              )}
              {message.metadata.executionTime && (
                <MetadataItem>
                  <MetadataIcon>⚡</MetadataIcon>
                  {message.metadata.executionTime}ms
                </MetadataItem>
              )}
              {message.metadata.confidence && (
                <MetadataItem>
                  <MetadataIcon>📊</MetadataIcon>
                  {Math.round(message.metadata.confidence * 100)}% confidence
                </MetadataItem>
              )}
            </MetadataFooter>
          )}

          {reactionNodes && <ReactionsContainer>{reactionNodes}</ReactionsContainer>}
        </Bubble>

        {message.replyCount && message.replyCount > 0 && (
          <ThreadIndicator onClick={() => onReply?.(message.id)}>
            <ThreadIcon>💬</ThreadIcon>
            <ThreadCount>
              {message.replyCount} {message.replyCount === 1 ? 'reply' : 'replies'}
            </ThreadCount>
            <ThreadArrow>→</ThreadArrow>
          </ThreadIndicator>
        )}
      </MessageContent>

      <AnimatePresence>
        {showActions && showActionMenu && (
          <ActionMenu
            initial={{ opacity: 0, scale: 0.9, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -10 }}
            transition={{ duration: 0.15 }}
          >
            <ActionButton
              onClick={() => onReact?.(message.id, '👍')}
              title="React"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              👍
            </ActionButton>
            <ActionButton
              onClick={() => onReply?.(message.id)}
              title="Reply"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              💬
            </ActionButton>
            <ActionButton
              onClick={() => onShare?.(message.id)}
              title="Share"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              🔗
            </ActionButton>
            {isOwnMessage && (
              <>
                <ActionButton
                  onClick={() => onEdit?.(message.id)}
                  title="Edit"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                >
                  ✏️
                </ActionButton>
                <ActionButton
                  onClick={() => onDelete?.(message.id)}
                  title="Delete"
                  $danger
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                >
                  🗑️
                </ActionButton>
              </>
            )}
            <ActionButton
              title="More"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              ⋯
            </ActionButton>
          </ActionMenu>
        )}
      </AnimatePresence>

      {isOwnMessage && (
        <AvatarWrapper>
          <Avatar src={currentUser.avatar || '/default-avatar.png'} alt={currentUser.name} />
          <StatusIndicator $status={currentUser.status} />
        </AvatarWrapper>
      )}
    </MessageContainer>
  );
};

// Helper functions
const formatTime = (date: Date): string => {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);

  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (minutes < 1440) {
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  }
  
  const dateStr = date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  return `${dateStr} at ${timeStr}`;
};

const getTypeIcon = (type: MessageType): string => {
  const icons: Record<MessageType, string> = {
    query: '💬',
    analysis: '🔍',
    result: '✅',
    error: '❌',
    system: 'ℹ️',
  };
  return icons[type];
};

// Small sanitizer for rendering attributes and trimmed display names
const _sanitize = (v: unknown, max = 120) =>
  String(v ?? '')
    .replace(/[\r\n]+/g, ' ')
    .replace(/[\x00-\x1F\x7F]/g, '')
    .trim()
    .slice(0, max);

const renderMessageContent = (content: string, mentions?: any[]): React.ReactNode => {
  if (!mentions || mentions.length === 0) return content;

  try {
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;

    // Do NOT mutate incoming mentions array; copy before sorting
    const sorted = [...mentions].sort((a, b) => (a.startIndex || 0) - (b.startIndex || 0));

    sorted.forEach((mention, i) => {
      const start = Math.max(0, mention.startIndex || 0);
      const end = Math.max(start, mention.endIndex || start);

      if (lastIndex < start) {
        parts.push(content.substring(lastIndex, start));
      }

      const name = _sanitize(mention.userName || mention.displayName || 'user', 64);
      const key = mention.id || `mention-${start}-${i}`;

      parts.push(
        <MentionHighlight key={key} title={`@${name}`}>
          @{name}
        </MentionHighlight>
      );

      lastIndex = Math.max(lastIndex, end);
    });

    if (lastIndex < content.length) {
      parts.push(content.substring(lastIndex));
    }

    return parts;
  } catch (err) {
    // Don't allow a malformed mentions array to break rendering
    // eslint-disable-next-line no-console
    console.error('renderMessageContent error:', String(err ?? 'unknown'));
    return content;
  }
};

const renderReactions = (
  reactions: any[],
  currentUserId: string,
  onReact?: (messageId: string, reaction: string) => void,
  messageId?: string
): React.ReactNode => {
  try {
    // Group reactions by type without creating many intermediate objects
    const grouped: Record<string, any[]> = Object.create(null);
    for (let i = 0; i < reactions.length; i++) {
      const reaction = reactions[i];
      const type = reaction?.type || 'unknown';
      if (!grouped[type]) grouped[type] = [];
      grouped[type].push(reaction);
    }

    const out: React.ReactNode[] = [];
    for (const type of Object.keys(grouped)) {
      const reactionList = grouped[type];
      const hasReacted = reactionList.some((r: any) => r.userId === currentUserId);
      const userNames = reactionList.map((r: any) => _sanitize(r.userName || r.displayName || '')).join(', ');

      out.push(
        <ReactionBubble
          key={type}
          $active={hasReacted}
          onClick={() => messageId && onReact?.(messageId, type)}
          title={userNames}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <ReactionEmoji>{type}</ReactionEmoji>
          <ReactionCount>{reactionList.length}</ReactionCount>
        </ReactionBubble>
      );
    }

    return out;
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('renderReactions error:', String(err ?? 'unknown'));
    return null;
  }
};

// Styled Components
const MessageContainer = styled(motion.div)<{ $isOwnMessage: boolean }>`
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  flex-direction: ${({ $isOwnMessage }) => ($isOwnMessage ? 'row-reverse' : 'row')};
  align-items: flex-end;
  position: relative;
  padding: 0 16px;

  @media (max-width: 768px) {
    padding: 0 8px;
  }
`;

const AvatarWrapper = styled.div`
  position: relative;
  flex-shrink: 0;
`;

const Avatar = styled.img`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(135deg, #2a304d 0%, #1a1f3a 100%);
`;

const StatusIndicator = styled.div<{ $status: string }>`
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #0a0e27;
  background: ${({ $status }) => {
    switch ($status) {
      case 'online': return '#10b981';
      case 'away': return '#f59e0b';
      case 'busy': return '#ef4444';
      default: return '#64748b';
    }
  }};
  box-shadow: 0 0 8px ${({ $status }) => {
    switch ($status) {
      case 'online': return 'rgba(16, 185, 129, 0.5)';
      case 'away': return 'rgba(245, 158, 11, 0.5)';
      case 'busy': return 'rgba(239, 68, 68, 0.5)';
      default: return 'transparent';
    }
  }};
`;

const MessageContent = styled.div<{ $isOwnMessage: boolean }>`
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 70%;
  align-items: ${({ $isOwnMessage }) => ($isOwnMessage ? 'flex-end' : 'flex-start')};
  flex: 1;

  @media (max-width: 768px) {
    max-width: 75%;
  }
`;

const MessageHeader = styled.div<{ $isOwnMessage: boolean }>`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 8px;
  flex-direction: ${({ $isOwnMessage }) => ($isOwnMessage ? 'row-reverse' : 'row')};
`;

const SenderInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SenderName = styled.span<{ $role: string }>`
  font-weight: 600;
  font-size: 14px;
  color: ${({ $role }) => ($role === 'ai' ? '#3b82f6' : '#f8fafc')};
  display: flex;
  align-items: center;
  gap: 6px;
`;

const AIBadge = styled.span`
  font-size: 10px;
  padding: 2px 6px;
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  border-radius: 6px;
  font-weight: 700;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const Timestamp = styled.span`
  font-size: 12px;
  color: #94a3b8;
`;

const MessageMetadata = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
`;

const EditedBadge = styled.span`
  font-size: 11px;
  color: #94a3b8;
  font-style: italic;
`;

const PinIcon = styled.span`
  font-size: 12px;
`;

const StatusDot = styled.div<{ $status: string }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${({ $status }) => {
    switch ($status) {
      case 'read': return '#10b981';
      case 'delivered': return '#3b82f6';
      case 'sent': return '#94a3b8';
      case 'sending': return '#f59e0b';
      case 'failed': return '#ef4444';
      default: return '#64748b';
    }
  }};
  box-shadow: 0 0 6px ${({ $status }) => {
    switch ($status) {
      case 'read': return 'rgba(16, 185, 129, 0.4)';
      case 'delivered': return 'rgba(59, 130, 246, 0.4)';
      default: return 'transparent';
    }
  }};
`;

const TypeBadge = styled.div<{ $type: MessageType }>`
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  background: ${({ $type }) => {
    switch ($type) {
      case 'analysis': return 'rgba(139, 92, 246, 0.2)';
      case 'result': return 'rgba(16, 185, 129, 0.2)';
      case 'error': return 'rgba(239, 68, 68, 0.2)';
      case 'system': return 'rgba(59, 130, 246, 0.2)';
      default: return 'rgba(255, 255, 255, 0.1)';
    }
  }};
  color: ${({ $type }) => {
    switch ($type) {
      case 'analysis': return '#a78bfa';
      case 'result': return '#10b981';
      case 'error': return '#ef4444';
      case 'system': return '#3b82f6';
      default: return '#f8fafc';
    }
  }};
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 1px solid ${({ $type }) => {
    switch ($type) {
      case 'analysis': return 'rgba(139, 92, 246, 0.3)';
      case 'result': return 'rgba(16, 185, 129, 0.3)';
      case 'error': return 'rgba(239, 68, 68, 0.3)';
      case 'system': return 'rgba(59, 130, 246, 0.3)';
      default: return 'rgba(255, 255, 255, 0.2)';
    }
  }};
`;

const Bubble = styled.div<{ $isOwnMessage: boolean; $isAI: boolean; $type: MessageType }>`
  padding: 16px;
  border-radius: 12px;
  background: ${({ $isOwnMessage, $isAI, $type }) => {
    if ($type === 'error') return 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
    if ($isOwnMessage) return 'linear-gradient(135deg, #2563eb 0%, #1e40af 100%)';
    if ($isAI) {
      return `
        rgba(255, 255, 255, 0.08);
      `;
    }
    return 'rgba(10, 14, 39, 0.4)';
  }};
  ${({ $isAI }) => $isAI && `
    backdrop-filter: blur(12px) saturate(150%);
    -webkit-backdrop-filter: blur(12px) saturate(150%);
    border: 1px solid rgba(255, 255, 255, 0.18);
  `}
  color: #f8fafc;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 8px 32px rgba(10, 14, 39, 0.2);
  position: relative;
  word-wrap: break-word;
  transition: all 200ms cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1), 0 8px 32px rgba(10, 14, 39, 0.3);
    transform: translateY(-1px);
  }
`;

const MessageText = styled.div`
  font-size: 16px;
  line-height: 1.75;
  white-space: pre-wrap;
  word-break: break-word;
`;

const MentionHighlight = styled.span`
  color: #60a5fa;
  font-weight: 600;
  background: rgba(37, 99, 235, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(37, 99, 235, 0.3);
  cursor: pointer;
  transition: all 150ms ease;

  &:hover {
    background: rgba(37, 99, 235, 0.3);
    border-color: rgba(37, 99, 235, 0.5);
  }
`;

const MetadataFooter = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 12px;
  opacity: 0.8;
`;

const MetadataItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const MetadataIcon = styled.span`
  font-size: 14px;
`;

const ReactionsContainer = styled.div`
  display: flex;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
`;

const ReactionBubble = styled(motion.button)<{ $active: boolean }>`
  padding: 4px 10px;
  border-radius: 16px;
  background: ${({ $active }) =>
    $active
      ? 'linear-gradient(135deg, #2563eb 0%, #1e40af 100%)'
      : 'rgba(255, 255, 255, 0.1)'};
  border: 1px solid ${({ $active }) =>
    $active ? '#2563eb' : 'rgba(255, 255, 255, 0.2)'};
  color: #f8fafc;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 150ms ease;

  &:hover {
    background: ${({ $active }) =>
      $active
        ? 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)'
        : 'rgba(255, 255, 255, 0.15)'};
    border-color: ${({ $active }) => ($active ? '#1e40af' : 'rgba(255, 255, 255, 0.3)')};
  }
`;

const ReactionEmoji = styled.span`
  font-size: 14px;
`;

const ReactionCount = styled.span`
  font-size: 12px;
  font-weight: 600;
`;

const ThreadIndicator = styled.button`
  padding: 8px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #60a5fa;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 200ms ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: #3b82f6;
    transform: translateX(4px);
  }
`;

const ThreadIcon = styled.span`
  font-size: 14px;
`;

const ThreadCount = styled.span``;

const ThreadArrow = styled.span`
  opacity: 0.6;
`;

const ActionMenu = styled(motion.div)`
  display: flex;
  gap: 4px;
  padding: 6px;
  background: rgba(10, 14, 39, 0.95);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 12px;
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15), 0 8px 32px rgba(10, 14, 39, 0.4);
  position: absolute;
  top: -48px;
  right: 0;
  z-index: 100;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const ActionButton = styled(motion.button)<{ $danger?: boolean }>`
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 150ms ease;
  position: relative;

  &:hover {
    background: ${({ $danger }) =>
      $danger ? 'rgba(239, 68, 68, 0.2)' : 'rgba(255, 255, 255, 0.1)'};
  }

  &:active {
    transform: scale(0.9);
  }

  &::before {
    content: attr(title);
    position: absolute;
    bottom: -24px;
    left: 50%;
    transform: translateX(-50%);
    padding: 2px 8px;
    background: rgba(0, 0, 0, 0.9);
    color: white;
    font-size: 11px;
    border-radius: 4px;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity 150ms ease;
  }

  &:hover::before {
    opacity: 1;
  }
`;
