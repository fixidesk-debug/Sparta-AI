import React, { useState, useCallback, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Message, User, MessageType } from '../../types/chat.types';
import { AdvancedMessageBubble } from './AdvancedMessageBubble';
import { MessageThread, ThreadView, ThreadedMessage } from './MessageThread';
import { UserPresencePanel } from './UserPresencePanel';
import { AdvancedTypingIndicator } from './AdvancedTypingIndicator';
import { MentionInput, SearchPanel, ExportDialog, ExportOptions } from './AdvancedFeatures';

// ==================== Types ====================

export interface ChatInterfaceProps {
  currentUser: User;
  messages: ThreadedMessage[];
  users: User[];
  typingUsers?: User[];
  onSendMessage: (content: string, type?: MessageType, metadata?: any) => void;
  onEditMessage?: (messageId: string, content: string) => void;
  onDeleteMessage?: (messageId: string) => void;
  onReaction?: (messageId: string, emoji: string) => void;
  onFileUpload?: (files: File[]) => void;
  onExport?: (format: 'pdf' | 'markdown' | 'json' | 'html', options: ExportOptions) => void;
  websocketUrl?: string;
  className?: string;
}

// ==================== Styled Components ====================

const ChatContainer = styled.div`
  display: flex;
  height: 100vh;
  background: linear-gradient(
    135deg,
    rgba(17, 24, 39, 1) 0%,
    rgba(31, 41, 55, 1) 100%
  );
  position: relative;
  overflow: hidden;

  @media (max-width: 1024px) {
    flex-direction: column;
  }
`;

const MainContent = styled.div<{ $sidebarOpen: boolean }>`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: margin-right 0.3s ease;

  @media (min-width: 1025px) {
    margin-right: ${props => props.$sidebarOpen ? '320px' : '0'};
  }
`;

const ChatHeader = styled.header`
  height: 64px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 10;

  @media (max-width: 768px) {
    padding: 0 16px;
    height: 56px;
  }
`;

const HeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const HeaderTitle = styled.h1`
  font-size: 20px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;

  @media (max-width: 768px) {
    font-size: 18px;
  }
`;

const HeaderRight = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const HeaderButton = styled(motion.button)`
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.9);
  }

  svg {
    width: 18px;
    height: 18px;
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.02);
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;

    &:hover {
      background: rgba(255, 255, 255, 0.15);
    }
  }

  @media (max-width: 768px) {
    padding: 16px;
  }
`;

const DateDivider = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  font-weight: 500;

  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(
      to right,
      transparent,
      rgba(255, 255, 255, 0.1),
      transparent
    );
  }
`;

const InputArea = styled.div`
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);

  @media (max-width: 768px) {
    padding: 16px;
  }
`;

const InputWrapper = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-end;
`;

const InputActions = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
`;

const ActionButton = styled(motion.button)`
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.9);
  }

  svg {
    width: 14px;
    height: 14px;
  }
`;

const SendButton = styled(motion.button)`
  min-width: 44px;
  height: 44px;
  border-radius: 10px;
  background: linear-gradient(
    135deg,
    rgba(59, 130, 246, 0.9),
    rgba(139, 92, 246, 0.9)
  );
  border: 1px solid rgba(59, 130, 246, 0.5);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;

  &:hover:not(:disabled) {
    background: linear-gradient(
      135deg,
      rgba(59, 130, 246, 1),
      rgba(139, 92, 246, 1)
    );
    transform: scale(1.05);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  svg {
    width: 20px;
    height: 20px;
  }
`;

const Sidebar = styled(motion.aside)<{ $open: boolean }>`
  width: 320px;
  background: rgba(17, 24, 39, 0.98);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;

  @media (min-width: 1025px) {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    transform: translateX(${props => props.$open ? '0' : '100%'});
    transition: transform 0.3s ease;
  }

  @media (max-width: 1024px) {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    z-index: 100;
    transform: translateY(${props => props.$open ? '0' : '100%'});
    transition: transform 0.3s ease;
  }
`;

const SidebarHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.95);
    margin: 0;
  }
`;

const SidebarContent = styled.div`
  flex: 1;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;

    &:hover {
      background: rgba(255, 255, 255, 0.15);
    }
  }
`;

const EmptyState = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;

  svg {
    width: 64px;
    height: 64px;
    margin-bottom: 24px;
    opacity: 0.3;
  }

  h3 {
    font-size: 20px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.8);
    margin: 0 0 8px 0;
  }

  p {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.5);
    margin: 0;
  }
`;

const FileInput = styled.input`
  display: none;
`;

const ScrollToBottom = styled(motion.button)`
  position: absolute;
  bottom: 100px;
  right: 32px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.9);
  border: 1px solid rgba(59, 130, 246, 0.5);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 10;

  &:hover {
    background: rgba(59, 130, 246, 1);
    transform: scale(1.1);
  }

  svg {
    width: 20px;
    height: 20px;
  }

  @media (max-width: 768px) {
    bottom: 90px;
    right: 24px;
  }
`;

// ==================== Helper Functions ====================

const groupMessagesByDate = (messages: ThreadedMessage[]): { date: string; messages: ThreadedMessage[] }[] => {
  const groups: { [key: string]: ThreadedMessage[] } = {};

  messages.forEach(msg => {
    const date = new Date(msg.timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });

    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(msg);
  });

  return Object.entries(groups).map(([date, messages]) => ({ date, messages }));
};

// ==================== ChatInterface Component ====================

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  currentUser,
  messages,
  users,
  typingUsers = [],
  onSendMessage,
  onEditMessage,
  onDeleteMessage,
  onReaction,
  onFileUpload,
  onExport,
  websocketUrl,
  className,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const [threadViewMessage, setThreadViewMessage] = useState<ThreadedMessage | null>(null);
  const [showScrollButton, setShowScrollButton] = useState(false);

  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback((smooth = true) => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTo({
        top: messagesContainerRef.current.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto',
      });
    }
  }, []);

  useEffect(() => {
    scrollToBottom(false);
  }, [messages.length, scrollToBottom]);

  const handleScroll = useCallback(() => {
    if (!messagesContainerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 200;
    setShowScrollButton(!isNearBottom);
  }, []);

  const handleSend = useCallback(() => {
    if (!inputValue.trim()) return;

    onSendMessage(inputValue, 'query');
    setInputValue('');
    setTimeout(() => scrollToBottom(), 100);
  }, [inputValue, onSendMessage, scrollToBottom]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0 && onFileUpload) {
      onFileUpload(files);
    }
  }, [onFileUpload]);

  const handleMention = useCallback((user: User) => {
    console.log('Mentioned user:', user);
  }, []);

  const handleMessageSelect = useCallback((messageId: string) => {
    setSearchOpen(false);
    // Scroll to message
    const element = document.getElementById(`message-${messageId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      element.classList.add('highlight');
      setTimeout(() => element.classList.remove('highlight'), 2000);
    }
  }, []);

  const handleExport = useCallback((format: 'pdf' | 'markdown' | 'json' | 'html', options: ExportOptions) => {
    if (onExport) {
      onExport(format, options);
    }
    setExportOpen(false);
  }, [onExport]);

  const groupedMessages = groupMessagesByDate(messages);

  return (
    <ChatContainer className={className}>
      <MainContent $sidebarOpen={sidebarOpen}>
        <ChatHeader>
          <HeaderLeft>
            <HeaderTitle>Sparta AI Chat</HeaderTitle>
          </HeaderLeft>
          <HeaderRight>
            <HeaderButton
              onClick={() => setSearchOpen(true)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Search messages"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" />
              </svg>
            </HeaderButton>
            <HeaderButton
              onClick={() => setExportOpen(true)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Export conversation"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 4v12m0 0l-4-4m4 4l4-4M4 20h16" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </HeaderButton>
            <HeaderButton
              onClick={() => setSidebarOpen(!sidebarOpen)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Toggle sidebar"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M17 8l4 4m0 0l-4 4m4-4H3" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </HeaderButton>
          </HeaderRight>
        </ChatHeader>

        <MessagesContainer ref={messagesContainerRef} onScroll={handleScroll}>
          {messages.length === 0 ? (
            <EmptyState>
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke="currentColor" strokeWidth="2" fill="none" />
              </svg>
              <h3>No messages yet</h3>
              <p>Start a conversation by sending a message below</p>
            </EmptyState>
          ) : (
            <>
              {groupedMessages.map(({ date, messages: dayMessages }) => (
                <React.Fragment key={date}>
                  <DateDivider>{date}</DateDivider>
                  {dayMessages.map(message => (
                    <MessageThread
                      key={message.id}
                      message={message}
                      currentUser={currentUser}
                      allUsers={users}
                      onEdit={onEditMessage}
                      onDelete={onDeleteMessage}
                      onReaction={onReaction}
                      onReply={(parentId, content) => onSendMessage(content, 'query', { parentId })}
                    />
                  ))}
                </React.Fragment>
              ))}
              {typingUsers.length > 0 && (
                <AdvancedTypingIndicator typingUsers={typingUsers} />
              )}
            </>
          )}
        </MessagesContainer>

        <AnimatePresence>
          {showScrollButton && (
            <ScrollToBottom
              onClick={() => scrollToBottom()}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 14l-7 7m0 0l-7-7m7 7V3" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </ScrollToBottom>
          )}
        </AnimatePresence>

        <InputArea>
          <InputActions>
            <ActionButton
              onClick={() => fileInputRef.current?.click()}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              Attach
            </ActionButton>
          </InputActions>
          <InputWrapper>
            <MentionInput
              value={inputValue}
              onChange={setInputValue}
              onMention={handleMention}
              users={users}
              placeholder="Type a message... (@ to mention)"
            />
            <SendButton
              onClick={handleSend}
              disabled={!inputValue.trim()}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </SendButton>
          </InputWrapper>
        </InputArea>

        <FileInput
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
        />
      </MainContent>

      <Sidebar $open={sidebarOpen}>
        <SidebarHeader>
          <h3>Participants ({users.length})</h3>
          <HeaderButton
            onClick={() => setSidebarOpen(false)}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 18L18 6M6 6l12 12" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" />
            </svg>
          </HeaderButton>
        </SidebarHeader>
        <SidebarContent>
          <UserPresencePanel users={users} currentUserId={currentUser.id} />
        </SidebarContent>
      </Sidebar>

      <AnimatePresence>
        {searchOpen && (
          <SearchPanel
            messages={messages}
            users={users}
            onMessageSelect={handleMessageSelect}
            onClose={() => setSearchOpen(false)}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {exportOpen && (
          <ExportDialog
            messages={messages}
            onClose={() => setExportOpen(false)}
            onExport={handleExport}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {threadViewMessage && (
          <ThreadView
            rootMessage={threadViewMessage}
            currentUser={currentUser}
            allUsers={users}
            onClose={() => setThreadViewMessage(null)}
            onEdit={onEditMessage}
            onDelete={onDeleteMessage}
            onReaction={onReaction}
            onReply={(parentId, content) => onSendMessage(content, 'query', { parentId })}
          />
        )}
      </AnimatePresence>
    </ChatContainer>
  );
};

export default ChatInterface;
