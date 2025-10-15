/**
 * User Avatar Component
 * Displays user avatar with online status indicator
 */

import React, { useCallback, useMemo, useState } from 'react';
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
  // Small sanitizer to limit length and remove newlines for attributes/logs
  const sanitizeForAttr = (value: unknown, max = 100) => {
    const s = String(value ?? '')
      .replace(/[\r\n]+/g, ' ')
      .trim();
    return s.length > max ? s.slice(0, max) : s;
  };

  const getInitials = useCallback((name: string): string => {
    const safeName = sanitizeForAttr(name, 60) || 'U';
    const parts = safeName.split(' ').filter(Boolean);
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return safeName.substring(0, 2).toUpperCase();
  }, []);

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

  const getStatusLabel = useCallback((status: UserStatus): string => {
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
  }, []);

  const [imageError, setImageError] = useState(false);

  // Guarded click to prevent external callback errors from bubbling
  const handleClick = useCallback(() => {
    if (!onClick) return;
    try {
      onClick();
    } catch (err) {
      // sanitize for logs
      // eslint-disable-next-line no-console
      console.error('UserAvatar onClick error:', String(err ?? 'unknown'));
    }
  }, [onClick]);

  return (
    <AvatarContainer
      size={size}
      onClick={handleClick}
      className={className}
      $clickable={!!onClick}
      whileHover={onClick ? { scale: 1.05 } : undefined}
      whileTap={onClick ? { scale: 0.95 } : undefined}
      title={`${sanitizeForAttr(user?.name || 'Unknown')} - ${getStatusLabel(
        user?.status || 'offline'
      )}`}
    >
      {user?.avatar && !imageError && typeof user.avatar === 'string' ? (
        <AvatarImage
          src={user.avatar}
          alt={sanitizeForAttr(user.name || 'Avatar')}
          loading="lazy"
          onError={() => setImageError(true)}
        />
      ) : (
        <AvatarFallback $color={user?.color || '#3b82f6'}>
          {getInitials(user?.name || 'U')}
        </AvatarFallback>
      )}
      
      {showStatus && (
        <StatusRing $color={getStatusColor(user?.status || 'offline')}>
          <StatusDot $color={getStatusColor(user?.status || 'offline')} />
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
