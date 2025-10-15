/**
 * Multi-User Presence Panel Component
 * Shows all active users with their status
 */

import React, { useState, useMemo, useCallback } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { User, UserStatus } from '../../types/chat.types';
import { UserAvatar } from './UserAvatar';

interface UserPresencePanelProps {
  users: User[];
  currentUserId: string;
  onUserClick?: (user: User) => void;
  maxVisible?: number;
  showExpanded?: boolean;
}

export const UserPresencePanel: React.FC<UserPresencePanelProps> = ({
  users,
  currentUserId,
  onUserClick,
  maxVisible = 5,
  showExpanded = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(showExpanded);

  // Memoize sorted users to avoid re-sorting on every render
  const sortedUsers = useMemo(() => {
    const arr = [...users];
    const statusPriority: Record<UserStatus, number> = { online: 0, away: 1, busy: 2, offline: 3 };
    arr.sort((a, b) => {
      const aPriority = statusPriority[a.status];
      const bPriority = statusPriority[b.status];
      if (aPriority !== bPriority) return aPriority - bPriority;
      return a.name.localeCompare(b.name);
    });
    return arr;
  }, [users]);

  const visibleUsers = useMemo(() => (isExpanded ? sortedUsers : sortedUsers.slice(0, maxVisible)), [isExpanded, sortedUsers, maxVisible]);
  const hiddenCount = useMemo(() => Math.max(0, sortedUsers.length - maxVisible), [sortedUsers, maxVisible]);

  // Compute status counts once per users change
  const statusCounts = useMemo(() => {
    const counts: Record<UserStatus, number> = { online: 0, away: 0, busy: 0, offline: 0 };
    for (const u of users) {
      counts[u.status] = (counts[u.status] || 0) + 1;
    }
    return counts;
  }, [users]);

  const getStatusCount = useCallback((status: UserStatus) => statusCounts[status] || 0, [statusCounts]);

  const formatLastSeen = useCallback((lastSeen?: Date): string => {
    if (!lastSeen) return 'Never';
    const now = new Date();
    const diff = now.getTime() - lastSeen.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return lastSeen.toLocaleDateString();
  }, []);

  return (
    <PanelContainer>
      <PanelHeader>
        <HeaderTitle>
          👥 Active Users
          <UserCount>{users.length}</UserCount>
        </HeaderTitle>
        
        <StatusSummary>
          <StatusBadge $status="online">
            <StatusDot $status="online" />
            {getStatusCount('online')}
          </StatusBadge>
          <StatusBadge $status="away">
            <StatusDot $status="away" />
            {getStatusCount('away')}
          </StatusBadge>
          <StatusBadge $status="busy">
            <StatusDot $status="busy" />
            {getStatusCount('busy')}
          </StatusBadge>
        </StatusSummary>
      </PanelHeader>

      <UserList>
        <AnimatePresence>
          {visibleUsers.map((user, index) => (
            <UserItem
              key={user.id}
              onClick={() => onUserClick?.(user)}
              $clickable={!!onUserClick}
              $isCurrentUser={user.id === currentUserId}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ delay: index * 0.03 }}
              whileHover={onUserClick ? { x: 4 } : undefined}
            >
              <UserAvatar user={user} size={36} showStatus={true} />
              
              <UserInfo>
                <UserName>
                  {user.name}
                  {user.id === currentUserId && <YouBadge>You</YouBadge>}
                  {user.role === 'ai' && <AIBadge>AI</AIBadge>}
                  {user.role === 'admin' && <AdminBadge>Admin</AdminBadge>}
                </UserName>
                <UserMeta>
                  {user.email && <UserEmail>{user.email}</UserEmail>}
                  {user.status === 'offline' && (
                    <LastSeen>Last seen {formatLastSeen(user.lastSeen)}</LastSeen>
                  )}
                  {user.isTyping && <TypingLabel>✏️ Typing...</TypingLabel>}
                </UserMeta>
              </UserInfo>

              {user.status === 'online' && <OnlinePulse />}
            </UserItem>
          ))}
        </AnimatePresence>
      </UserList>

      {!isExpanded && hiddenCount > 0 && (
        <ExpandButton
          onClick={() => setIsExpanded(true)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Show {hiddenCount} more user{hiddenCount > 1 ? 's' : ''}
        </ExpandButton>
      )}

      {isExpanded && sortedUsers.length > maxVisible && (
        <CollapseButton
          onClick={() => setIsExpanded(false)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          Show less
        </CollapseButton>
      )}
    </PanelContainer>
  );
};

// Styled Components
const PanelContainer = styled.div`
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
`;

const PanelHeader = styled.div`
  padding: 16px;
  background: rgba(10, 14, 39, 0.4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
`;

const HeaderTitle = styled.h3`
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #f8fafc;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const UserCount = styled.span`
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
`;

const StatusSummary = styled.div`
  display: flex;
  gap: 8px;
`;

const StatusBadge = styled.div<{ $status: UserStatus }>`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
`;

const StatusDot = styled.div<{ $status: UserStatus }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${({ $status }) => {
    switch ($status) {
      case 'online': return '#10b981';
      case 'away': return '#f59e0b';
      case 'busy': return '#ef4444';
      case 'offline': return '#64748b';
    }
  }};
`;

const UserList = styled.div`
  padding: 8px;
  max-height: 400px;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;

    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
`;

const UserItem = styled(motion.div)<{ $clickable: boolean; $isCurrentUser: boolean }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 8px;
  cursor: ${({ $clickable }) => ($clickable ? 'pointer' : 'default')};
  transition: background 150ms ease;
  position: relative;
  background: ${({ $isCurrentUser }) => 
    $isCurrentUser ? 'rgba(59, 130, 246, 0.1)' : 'transparent'};
  border: 1px solid ${({ $isCurrentUser }) => 
    $isCurrentUser ? 'rgba(59, 130, 246, 0.2)' : 'transparent'};

  &:hover {
    background: ${({ $isCurrentUser }) => 
      $isCurrentUser ? 'rgba(59, 130, 246, 0.15)' : 'rgba(255, 255, 255, 0.05)'};
  }
`;

const UserInfo = styled.div`
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const UserName = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
`;

const YouBadge = styled.span`
  font-size: 10px;
  padding: 2px 6px;
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
  border-radius: 4px;
  font-weight: 600;
`;

const AIBadge = styled.span`
  font-size: 10px;
  padding: 2px 6px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
  color: white;
  border-radius: 4px;
  font-weight: 600;
`;

const AdminBadge = styled.span`
  font-size: 10px;
  padding: 2px 6px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border-radius: 4px;
  font-weight: 600;
`;

const UserMeta = styled.div`
  font-size: 12px;
  color: #64748b;
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const UserEmail = styled.span`
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const LastSeen = styled.span`
  font-style: italic;
`;

const TypingLabel = styled.span`
  color: #3b82f6;
  font-weight: 500;
`;

const OnlinePulse = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
  animation: pulse 2s ease-in-out infinite;

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.5;
      transform: scale(1.2);
    }
  }
`;

const ExpandButton = styled(motion.button)`
  width: 100%;
  padding: 10px;
  background: rgba(59, 130, 246, 0.1);
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  color: #3b82f6;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 150ms ease;

  &:hover {
    background: rgba(59, 130, 246, 0.15);
  }
`;

const CollapseButton = styled(ExpandButton)``;
