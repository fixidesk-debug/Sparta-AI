import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const SidebarContainer = styled(motion.aside)<{ $collapsed: boolean }>`
  width: ${p => p.$collapsed ? '72px' : '280px'};
  height: 100vh;
  background: rgba(10, 14, 39, 0.8);
  backdrop-filter: blur(16px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  transition: width 300ms cubic-bezier(0.4, 0, 0.2, 1);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
`;

const Logo = styled.div<{ $collapsed: boolean }>`
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  h1 {
    font-size: 20px;
    color: #f8fafc;
    margin: 0;
    opacity: ${p => p.$collapsed ? 0 : 1};
    transition: opacity 200ms;
  }
`;

const Nav = styled.nav`
  flex: 1;
  padding: 16px 12px;
  overflow-y: auto;
`;

const NavItem = styled.div<{ $active?: boolean; $collapsed: boolean }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 4px;
  border-radius: 12px;
  color: ${p => p.$active ? '#f8fafc' : '#cbd5e1'};
  background: ${p => p.$active ? 'rgba(37, 99, 235, 0.15)' : 'transparent'};
  border-left: 3px solid ${p => p.$active ? '#2563eb' : 'transparent'};
  cursor: pointer;
  transition: all 200ms;
  position: relative;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #f8fafc;
  }
  
  span {
    opacity: ${p => p.$collapsed ? 0 : 1};
    white-space: nowrap;
  }
`;

const Badge = styled.span`
  background: #ef4444;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: auto;
`;

const Section = styled.div<{ $collapsed: boolean }>`
  margin: 24px 0 12px;
  padding: 0 16px;
  font-size: 11px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: ${p => p.$collapsed ? 0 : 1};
`;

const ResourceIndicator = styled.div`
  padding: 16px;
  margin: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const ResourceBar = styled.div<{ $value: number }>`
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  margin-top: 8px;
  overflow: hidden;
  
  &::after {
    content: '';
    display: block;
    width: ${p => p.$value}%;
    height: 100%;
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    transition: width 300ms;
  }
`;

export const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <SidebarContainer $collapsed={collapsed}>
      <Logo $collapsed={collapsed}>
        <span style={{ fontSize: '24px' }}>⚡</span>
        <h1>Sparta AI</h1>
      </Logo>

      <Nav>
        <NavItem $active $collapsed={collapsed}>
          <span>💬</span>
          <span>Chat</span>
          <Badge>3</Badge>
        </NavItem>
        <NavItem $collapsed={collapsed}>
          <span>📊</span>
          <span>Analytics</span>
        </NavItem>
        <NavItem $collapsed={collapsed}>
          <span>📁</span>
          <span>Files</span>
        </NavItem>
        <NavItem $collapsed={collapsed}>
          <span>🤖</span>
          <span>Models</span>
        </NavItem>

        <Section $collapsed={collapsed}>Workspaces</Section>
        <NavItem $collapsed={collapsed}>
          <span>👥</span>
          <span>Team Alpha</span>
        </NavItem>
        <NavItem $collapsed={collapsed}>
          <span>🔬</span>
          <span>Research</span>
        </NavItem>

        <Section $collapsed={collapsed}>Data Sources</Section>
        <NavItem $collapsed={collapsed}>
          <span>🟢</span>
          <span>PostgreSQL</span>
        </NavItem>
        <NavItem $collapsed={collapsed}>
          <span>🟡</span>
          <span>MongoDB</span>
        </NavItem>
      </Nav>

      {!collapsed && (
        <ResourceIndicator>
          <div style={{ fontSize: '11px', color: '#cbd5e1', marginBottom: '4px' }}>
            CPU: 45% | RAM: 62%
          </div>
          <ResourceBar $value={45} />
          <ResourceBar $value={62} />
        </ResourceIndicator>
      )}

      <div style={{ padding: '16px', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <NavItem $collapsed={collapsed}>
          <span>⚙️</span>
          <span>Settings</span>
        </NavItem>
      </div>
    </SidebarContainer>
  );
};
