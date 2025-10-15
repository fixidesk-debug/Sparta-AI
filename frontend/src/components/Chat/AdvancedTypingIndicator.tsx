/**
 * Advanced Typing Indicator Component
 * Shows elegant animation when users are typing with multi-user support
 */

import React, { useMemo } from 'react';
import styled, { keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { User } from '../../types/chat.types';
import { UserAvatar } from './UserAvatar';

interface AdvancedTypingIndicatorProps {
  typingUsers: User[];
  maxDisplayed?: number;
  showAvatars?: boolean;
  variant?: 'compact' | 'full';
}

export const AdvancedTypingIndicator: React.FC<AdvancedTypingIndicatorProps> = ({
  typingUsers,
  maxDisplayed = 3,
  showAvatars = true,
  variant = 'full',
}) => {
  const hasTyping = typingUsers && typingUsers.length > 0;
  if (!hasTyping) return null;

  const sanitize = (s: unknown, max = 40) =>
    String(s ?? '')
      .replace(/[\r\n]+/g, ' ')
      .replace(/[\x00-\x1F\x7F]/g, '')
      .trim()
      .slice(0, max) || 'Someone';

  const displayedUsers = useMemo(() => typingUsers.slice(0, maxDisplayed), [typingUsers, maxDisplayed]);
  const remainingCount = useMemo(() => Math.max(0, typingUsers.length - maxDisplayed), [typingUsers.length, maxDisplayed]);

  const getTypingText = useMemo(() => {
    try {
      const names = displayedUsers.map(u => sanitize(u?.name));
      if (typingUsers.length === 1) return `${names[0]} is typing...`;
      if (typingUsers.length === 2) return `${names[0]} and ${names[1]} are typing...`;
      if (typingUsers.length === 3) return `${names[0]}, ${names[1]}, and ${names[2]} are typing...`;
      return `${names[0]}, ${names[1]}, and ${Math.max(typingUsers.length - 2, 1)} others are typing...`;
    } catch (err) {
      // Avoid throwing inside render — fall back to a generic string
      // eslint-disable-next-line no-console
      console.error('getTypingText failed:', String(err ?? 'unknown'));
      return 'Someone is typing...';
    }
  }, [displayedUsers, typingUsers.length]);

  const Dots = useMemo(
    () => (
      <DotsContainer>
        <Dot $delay={0} />
        <Dot $delay={0.15} />
        <Dot $delay={0.3} />
      </DotsContainer>
    ),
    []
  );

  if (variant === 'compact') {
    return (
      <AnimatePresence>
        <CompactContainer
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.2 }}
        >
          {Dots}
        </CompactContainer>
      </AnimatePresence>
    );
  }

  return (
    <AnimatePresence>
      <TypingContainer
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        transition={{ duration: 0.2 }}
      >
        {showAvatars && (
          <AvatarGroup>
            {displayedUsers.map((user, index) => {
              const id = sanitize(user?.id, 24) || `u-${index}`;
              return (
                <AvatarWrapper
                  key={id}
                  $index={index}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <UserAvatar user={user} size={28} showStatus={false} />
                </AvatarWrapper>
              );
            })}
            {remainingCount > 0 && (
              <RemainingCount
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                exit={{ scale: 0 }}
              >
                +{remainingCount}
              </RemainingCount>
            )}
          </AvatarGroup>
        )}

        <TypingContent>
          <TypingText>{getTypingText}</TypingText>
          {Dots}
        </TypingContent>
      </TypingContainer>
    </AnimatePresence>
  );
};

// Animations
const bounce = keyframes`
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-8px);
  }
`;

// Styled Components
const TypingContainer = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin: 8px 0;
  max-width: fit-content;
`;

const CompactContainer = styled(motion.div)`
  display: inline-flex;
  padding: 8px 12px;
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const AvatarGroup = styled.div`
  display: flex;
  align-items: center;
  position: relative;
`;

const AvatarWrapper = styled(motion.div)<{ $index: number }>`
  margin-left: ${({ $index }) => ($index > 0 ? '-8px' : '0')};
  position: relative;
  z-index: ${({ $index }) => 10 - $index};
  border: 2px solid rgba(30, 41, 59, 1);
  border-radius: 50%;
`;

const RemainingCount = styled(motion.div)`
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.3);
  border: 2px solid rgba(30, 41, 59, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: #f8fafc;
  margin-left: -8px;
  z-index: 1;
`;

const TypingContent = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TypingText = styled.span`
  font-size: 13px;
  color: #94a3b8;
  font-weight: 500;
`;

const DotsContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 0 4px;
`;

const Dot = styled.div<{ $delay: number }>`
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #3b82f6;
  animation: ${bounce} 1.4s ease-in-out infinite;
  animation-delay: ${({ $delay }) => $delay}s;
`;
