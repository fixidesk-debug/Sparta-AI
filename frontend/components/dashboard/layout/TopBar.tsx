import React from 'react';
import styled from 'styled-components';

const TopBarContainer = styled.header`
  height: 64px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: fixed;
  top: 0;
  left: 280px;
  right: 0;
  z-index: 90;
`;

const SearchBar = styled.div`
  flex: 1;
  max-width: 600px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  
  input {
    flex: 1;
    background: transparent;
    border: none;
    color: #f8fafc;
    font-size: 14px;
    outline: none;
    
    &::placeholder { color: #64748b; }
  }
`;

const Actions = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const IconButton = styled.button`
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #cbd5e1;
  cursor: pointer;
  transition: all 150ms;
  position: relative;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #f8fafc;
  }
`;

const NotificationDot = styled.span`
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
  border: 2px solid #0a0e27;
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  cursor: pointer;
`;

export const TopBar: React.FC = () => (
  <TopBarContainer>
    <SearchBar>
      <span>🔍</span>
      <input placeholder="Search conversations, files, or ask AI..." />
      <kbd style={{ fontSize: '11px', color: '#64748b' }}>⌘K</kbd>
    </SearchBar>

    <Actions>
      <IconButton>
        <span>➕</span>
      </IconButton>
      <IconButton>
        <span>🔔</span>
        <NotificationDot />
      </IconButton>
      <IconButton>
        <span>⚡</span>
      </IconButton>
      <Avatar />
    </Actions>
  </TopBarContainer>
);
