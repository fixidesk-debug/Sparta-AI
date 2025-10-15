import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { Message, TypingUser } from './types';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
`;

const Header = styled.div`
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h2`
  margin: 0;
  font-size: 20px;
  color: #f8fafc;
  font-weight: 600;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 12px;
`;

const HeaderButton = styled.button`
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #cbd5e1;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 150ms;
  
  &:hover {
    background: rgba(255, 255, 255, 0.15);
    color: #f8fafc;
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    
    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
`;

const InputWrapper = styled.div`
  padding: 16px 24px;
  background: rgba(10, 14, 39, 0.6);
  backdrop-filter: blur(12px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
`;

const DateDivider = styled.div`
  text-align: center;
  color: #64748b;
  font-size: 12px;
  margin: 16px 0;
  position: relative;
  
  &::before, &::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 40%;
    height: 1px;
    background: rgba(255, 255, 255, 0.1);
  }
  
  &::before { left: 0; }
  &::after { right: 0; }
`;

export const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      content,
      type: 'query',
      sender: {
        id: 'user1',
        name: 'You',
        avatar: '',
        isOnline: true
      },
      timestamp: new Date(),
      status: 'sent'
    };
    setMessages([...messages, newMessage]);
  };

  const handleTyping = () => {
    // Emit typing event
  };

  const handleExport = () => {
    console.log('Export conversation');
  };

  const handleSearch = () => {
    console.log('Search messages');
  };

  return (
    <Container>
      <Header>
        <Title>Sparta AI Chat</Title>
        <HeaderActions>
          <HeaderButton onClick={handleSearch}>🔍 Search</HeaderButton>
          <HeaderButton onClick={handleExport}>📥 Export</HeaderButton>
        </HeaderActions>
      </Header>

      <MessagesContainer>
        <DateDivider>Today</DateDivider>
        {messages.map(msg => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        <TypingIndicator users={typingUsers} />
        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputWrapper>
        <ChatInput onSend={handleSend} onTyping={handleTyping} />
      </InputWrapper>
    </Container>
  );
};
