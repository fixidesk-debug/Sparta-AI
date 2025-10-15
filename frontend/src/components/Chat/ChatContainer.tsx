import React from 'react';
import styled from 'styled-components';
import { ThemeProvider } from 'styled-components';
import { Message, User } from '../../types/chat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { chatTheme } from '../../styles/chat.theme';

interface ChatContainerProps {
  messages: Message[];
  currentUser: User;
}

const ChatWrapper = styled.div`
  display: flex;
  flex-direction: column;
  height: 80vh;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(16px);
  box-shadow: var(--glass-shadow);
  overflow: hidden;
`;

export const ChatContainer: React.FC<ChatContainerProps> = ({ messages, currentUser }) => {
  return (
    <ThemeProvider theme={chatTheme}>
      <ChatWrapper>
        <MessageList messages={messages} currentUser={currentUser} />
        <MessageInput />
      </ChatWrapper>
    </ThemeProvider>
  );
};
