import React from 'react';
import styled from 'styled-components';

const InputWrapper = styled.div`
  padding: var(--spacing-2) var(--spacing-3);
  background: rgba(0,0,0,0.2);
  border-top: 1px solid var(--glass-border);
`;

const Input = styled.input`
  width: 100%;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: var(--font-size-base);
  padding: var(--spacing-2);

  &:focus {
    outline: none;
  }
`;

export const MessageInput: React.FC = () => {
  return (
    <InputWrapper>
      <Input placeholder="Ask Sparta AI..." />
    </InputWrapper>
  );
};
