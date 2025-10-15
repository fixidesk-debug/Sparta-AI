import React from 'react';
import styled from 'styled-components';
import { Message, User } from '../../types/chat';
import { MessageBubble } from './MessageBubble';

interface MessageListProps {
  messages: Message[];
  currentUser: User;
}

const MessageListWrapper = styled.div`
  display: flex;
  flex-direction: column;
  padding: var(--spacing-3);
  overflow-y: auto;
  flex-grow: 1;
`;

export const MessageList: React.FC<MessageListProps> = ({ messages, currentUser }) => {
  return (
    <MessageListWrapper>
      {messages.map(msg => (
        <MessageBubble key={msg.id} message={msg} currentUser={currentUser} />
      ))}
    </MessageListWrapper>
  );
};
