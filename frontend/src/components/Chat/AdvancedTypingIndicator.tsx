/**
 * Advanced Typing Indicator Component
 * Shows elegant animation when users are typing with multi-user support
 */

import React from 'react';
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
  if (typingUsers.length === 0) return null;

  const displayedUsers = typingUsers.slice(0, maxDisplayed);
  const remainingCount = typingUsers.length - maxDisplayed;

  const getTypingText = (): string => {
    if (typingUsers.length === 1) {
      return `${typingUsers[0].name} is typing...`;
    } else if (typingUsers.length === 2) {
      return `${typingUsers[0].name} and ${typingUsers[1].name} are typing...`;
    } else if (typingUsers.length === 3) {
      return `${typingUsers[0].name}, ${typingUsers[1].name}, and ${typingUsers[2].name} are typing...`;
    } else {
      return `${typingUsers[0].name}, ${typingUsers[1].name}, and ${typingUsers.length - 2} others are typing...`;
    }
  };

  if (variant === 'compact') {
    return (
      <AnimatePresence>
        <CompactContainer
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.2 }}
        >
          <DotsContainer>
            <Dot $delay={0} />
            <Dot $delay={0.15} />
            <Dot $delay={0.3} />
          </DotsContainer>
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
            {displayedUsers.map((user, index) => (
              <AvatarWrapper
                key={user.id}
                $index={index}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                exit={{ scale: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <UserAvatar user={user} size={28} showStatus={false} />
              </AvatarWrapper>
            ))}
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
          <TypingText>{getTypingText()}</TypingText>
          <DotsContainer>
            <Dot $delay={0} />
            <Dot $delay={0.15} />
            <Dot $delay={0.3} />
          </DotsContainer>
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
