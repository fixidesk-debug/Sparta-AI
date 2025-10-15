import React from 'react';
import styled, { keyframes } from 'styled-components';
import { TypingUser } from './types';

const bounce = keyframes`
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
`;

const Container = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  width: fit-content;
`;

const DotsContainer = styled.div`
  display: flex;
  gap: 4px;
`;

const Dot = styled.div<{ $delay: number }>`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #60a5fa;
  animation: ${bounce} 1.4s infinite ease-in-out;
  animation-delay: ${p => p.$delay}s;
`;

const Text = styled.span`
  font-size: 13px;
  color: #cbd5e1;
`;

export const TypingIndicator: React.FC<{ users: TypingUser[] }> = ({ users }) => {
  if (users.length === 0) return null;

  const text = users.length === 1 
    ? `${users[0].userName} is typing...`
    : `${users.length} people are typing...`;

  return (
    <Container>
      <DotsContainer>
        <Dot $delay={0} />
        <Dot $delay={0.2} />
        <Dot $delay={0.4} />
      </DotsContainer>
      <Text>{text}</Text>
    </Container>
  );
};
