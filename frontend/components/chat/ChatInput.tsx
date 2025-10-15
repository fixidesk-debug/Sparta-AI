import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const InputContainer = styled.div`
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 16px;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  transition: all 250ms;
  
  &:focus-within {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
  }
`;

const TextArea = styled.textarea`
  flex: 1;
  background: transparent;
  border: none;
  color: #f8fafc;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  resize: none;
  outline: none;
  max-height: 120px;
  line-height: 1.5;
  
  &::placeholder {
    color: #64748b;
  }
`;

const ActionBar = styled.div`
  display: flex;
  gap: 8px;
  align-items: center;
`;

const IconButton = styled(motion.button)`
  background: transparent;
  border: none;
  color: #cbd5e1;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 150ms;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #f8fafc;
  }
`;

const SendButton = styled(motion.button)`
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 0 20px rgba(37, 99, 235, 0.3);
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const MentionDropdown = styled.div`
  position: absolute;
  bottom: 100%;
  left: 0;
  background: rgba(10, 14, 39, 0.95);
  backdrop-filter: blur(16px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px;
  margin-bottom: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
`;

const MentionItem = styled.div`
  padding: 8px 12px;
  border-radius: 8px;
  color: #f8fafc;
  font-size: 14px;
  cursor: pointer;
  transition: all 150ms;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

interface ChatInputProps {
  onSend: (message: string, attachments?: File[]) => void;
  onTyping: () => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, onTyping }) => {
  const [message, setMessage] = useState('');
  const [showMentions, setShowMentions] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (message.trim()) {
      onSend(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
    if (e.key === '@') {
      setShowMentions(true);
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      {showMentions && (
        <MentionDropdown>
          <MentionItem onClick={() => setShowMentions(false)}>@team</MentionItem>
          <MentionItem onClick={() => setShowMentions(false)}>@analyst</MentionItem>
        </MentionDropdown>
      )}
      
      <InputContainer>
        <TextArea
          value={message}
          onChange={(e) => { setMessage(e.target.value); onTyping(); }}
          onKeyDown={handleKeyDown}
          placeholder="Ask Sparta AI anything..."
          rows={1}
        />
        
        <ActionBar>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            style={{ display: 'none' }}
          />
          <IconButton onClick={() => fileInputRef.current?.click()}>
            📎
          </IconButton>
          <IconButton>🎤</IconButton>
          <SendButton
            onClick={handleSend}
            disabled={!message.trim()}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Send
          </SendButton>
        </ActionBar>
      </InputContainer>
    </div>
  );
};
