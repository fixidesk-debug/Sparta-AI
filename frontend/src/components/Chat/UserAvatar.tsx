/**
 * User Avatar Component
 * Displays user avatar with online status indicator
 */

import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { User, UserStatus } from '../../types/chat.types';

interface UserAvatarProps {
  user: User;
  size?: number;
  showStatus?: boolean;
  onClick?: () => void;
  className?: string;
}

export const UserAvatar: React.FC<UserAvatarProps> = ({
  user,
  size = 40,
  showStatus = true,
  onClick,
  className,
}) => {
  const getInitials = (name: string): string => {
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const getStatusColor = (status: UserStatus): string => {
    switch (status) {
      case 'online':
        return '#10b981'; // green
      case 'away':
        return '#f59e0b'; // amber
      case 'busy':
        return '#ef4444'; // red
      case 'offline':
        return '#64748b'; // gray
      default:
        return '#64748b';
    }
  };

  const getStatusLabel = (status: UserStatus): string => {
    switch (status) {
      case 'online':
        return 'Online';
      case 'away':
        return 'Away';
      case 'busy':
        return 'Busy';
      case 'offline':
        return 'Offline';
      default:
        return 'Unknown';
    }
  };

  return (
    <AvatarContainer
      size={size}
      onClick={onClick}
      className={className}
      $clickable={!!onClick}
      whileHover={onClick ? { scale: 1.05 } : undefined}
      whileTap={onClick ? { scale: 0.95 } : undefined}
      title={`${user.name} - ${getStatusLabel(user.status)}`}
    >
      {user.avatar ? (
        <AvatarImage src={user.avatar} alt={user.name} loading="lazy" />
      ) : (
        <AvatarFallback $color={user.color || '#3b82f6'}>
          {getInitials(user.name)}
        </AvatarFallback>
      )}
      
      {showStatus && (
        <StatusRing $color={getStatusColor(user.status)}>
          <StatusDot $color={getStatusColor(user.status)} />
        </StatusRing>
      )}

      {user.isTyping && (
        <TypingBadge
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          exit={{ scale: 0 }}
        >
          ✏️
        </TypingBadge>
      )}
    </AvatarContainer>
  );
};

// Styled Components
const AvatarContainer = styled(motion.div)<{ size: number; $clickable: boolean }>`
  position: relative;
  width: ${({ size }) => size}px;
  height: ${({ size }) => size}px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  cursor: ${({ $clickable }) => ($clickable ? 'pointer' : 'default')};
`;

const AvatarImage = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
`;

const AvatarFallback = styled.div<{ $color: string }>`
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${({ $color }) => $color};
  color: white;
  font-weight: 600;
  font-size: 14px;
  user-select: none;
`;

const StatusRing = styled.div<{ $color: string }>`
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: rgba(30, 41, 59, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 8px ${({ $color }) => $color}40;
`;

const StatusDot = styled.div<{ $color: string }>`
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: ${({ $color }) => $color};
  box-shadow: 0 0 6px ${({ $color }) => $color};
  animation: pulse 2s ease-in-out infinite;

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.7;
    }
  }
`;

const TypingBadge = styled(motion.div)`
  position: absolute;
  top: -4px;
  left: -4px;
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
  border: 2px solid rgba(30, 41, 59, 1);
`;
