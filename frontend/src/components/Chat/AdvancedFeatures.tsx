import React, { useState, useCallback, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Message, User } from '../../types/chat.types';

// ==================== Types ====================

export interface MentionInputProps {
  value: string;
  onChange: (value: string) => void;
  onMention: (user: User) => void;
  users: User[];
  placeholder?: string;
  disabled?: boolean;
}

export interface SearchPanelProps {
  messages: Message[];
  users: User[];
  onMessageSelect: (messageId: string) => void;
  onClose: () => void;
}

export interface ExportDialogProps {
  messages: Message[];
  onClose: () => void;
  onExport: (format: 'pdf' | 'markdown' | 'json' | 'html', options: ExportOptions) => void;
}

export interface ExportOptions {
  dateRange?: { start: Date; end: Date };
  includeAttachments?: boolean;
  includeReactions?: boolean;
  includeThreads?: boolean;
  includeSystemMessages?: boolean;
}

export interface SearchFilters {
  type?: 'all' | 'user' | 'ai' | 'system';
  sender?: string;
  dateRange?: { start: Date; end: Date };
  hasAttachments?: boolean;
  hasCode?: boolean;
  hasChart?: boolean;
}

// ==================== Styled Components ====================

// Mention Input Styles
const MentionInputContainer = styled.div`
  position: relative;
  width: 100%;
`;

const StyledTextarea = styled.textarea`
  width: 100%;
  min-height: 44px;
  max-height: 200px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 14px;
  font-family: Inter, sans-serif;
  color: rgba(255, 255, 255, 0.95);
  resize: none;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: rgba(59, 130, 246, 0.5);
    background: rgba(255, 255, 255, 0.08);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const MentionDropdown = styled(motion.div)`
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  margin-bottom: 8px;
  max-height: 240px;
  overflow-y: auto;
  background: rgba(17, 24, 39, 0.95);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
  z-index: 100;

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

const MentionItem = styled(motion.div)<{ $active: boolean }>`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  cursor: pointer;
  background: ${props => props.$active ? 'rgba(59, 130, 246, 0.15)' : 'transparent'};
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: background 0.15s ease;

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background: rgba(59, 130, 246, 0.1);
  }
`;

const MentionAvatar = styled.div<{ $color: string }>`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: ${props => props.$color};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
`;

const MentionInfo = styled.div`
  flex: 1;
  min-width: 0;
`;

const MentionName = styled.div`
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.95);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const MentionUsername = styled.div`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
`;

// Search Panel Styles
const SearchOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  z-index: 900;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 60px 20px 20px;

  @media (max-width: 768px) {
    padding: 0;
    align-items: flex-end;
  }
`;

const SearchContainer = styled(motion.div)`
  width: 100%;
  max-width: 700px;
  max-height: calc(100vh - 120px);
  background: rgba(17, 24, 39, 0.98);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.4);

  @media (max-width: 768px) {
    max-width: 100%;
    max-height: 85vh;
    border-radius: 16px 16px 0 0;
  }
`;

const SearchHeader = styled.div`
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
`;

const SearchInputWrapper = styled.div`
  position: relative;
  margin-bottom: 16px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px 12px 44px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.95);
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: rgba(59, 130, 246, 0.5);
    background: rgba(255, 255, 255, 0.08);
  }

  &::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }
`;

const SearchIcon = styled.div`
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.5);

  svg {
    width: 18px;
    height: 18px;
  }
`;

const FilterRow = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
`;

const FilterChip = styled(motion.button)<{ $active: boolean }>`
  padding: 6px 12px;
  background: ${props => props.$active ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.05)'};
  border: 1px solid ${props => props.$active ? 'rgba(59, 130, 246, 0.5)' : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: ${props => props.$active ? 'rgba(59, 130, 246, 1)' : 'rgba(255, 255, 255, 0.7)'};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.$active ? 'rgba(59, 130, 246, 0.3)' : 'rgba(255, 255, 255, 0.08)'};
    border-color: ${props => props.$active ? 'rgba(59, 130, 246, 0.6)' : 'rgba(255, 255, 255, 0.2)'};
  }
`;

const SearchResults = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;

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
`;

const SearchResultItem = styled(motion.div)`
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(59, 130, 246, 0.3);
    transform: translateX(4px);
  }
`;

const ResultHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
`;

const ResultSender = styled.span`
  font-size: 13px;
  font-weight: 600;
  color: rgba(59, 130, 246, 0.9);
`;

const ResultTimestamp = styled.span`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
`;

const ResultContent = styled.div`
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;

  mark {
    background: rgba(245, 158, 11, 0.3);
    color: rgba(245, 158, 11, 1);
    padding: 2px 4px;
    border-radius: 4px;
  }
`;

const NoResults = styled.div`
  text-align: center;
  padding: 48px 24px;
  color: rgba(255, 255, 255, 0.5);

  svg {
    width: 48px;
    height: 48px;
    margin-bottom: 16px;
    opacity: 0.3;
  }

  p {
    font-size: 14px;
    margin: 8px 0;
  }
`;

const HintText = styled.p`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 8px 0 0 0;
`;

// Export Dialog Styles
const ExportContainer = styled(SearchContainer)`
  max-width: 600px;
  max-height: 600px;
`;

const ExportSection = styled.div`
  padding: 16px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);

  &:last-child {
    border-bottom: none;
  }
`;

const SectionTitle = styled.h4`
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 12px 0;
`;

const ExportInfo = styled.p`
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
`;

const FormatGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
`;

const FormatOption = styled(motion.button)<{ $selected: boolean }>`
  padding: 16px;
  background: ${props => props.$selected ? 'rgba(59, 130, 246, 0.15)' : 'rgba(255, 255, 255, 0.03)'};
  border: 2px solid ${props => props.$selected ? 'rgba(59, 130, 246, 0.5)' : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;

  &:hover {
    background: ${props => props.$selected ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255, 255, 255, 0.06)'};
    border-color: ${props => props.$selected ? 'rgba(59, 130, 246, 0.6)' : 'rgba(255, 255, 255, 0.2)'};
  }
`;

const FormatIcon = styled.div`
  font-size: 24px;
  margin-bottom: 8px;
`;

const FormatName = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 4px;
`;

const FormatDesc = styled.div`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
`;

const Checkbox = styled.input`
  width: 18px;
  height: 18px;
  accent-color: rgba(59, 130, 246, 1);
  cursor: pointer;
`;

const CheckboxText = styled.span`
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
`;

const ExportActions = styled.div`
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.02);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
`;

const ActionButton = styled(motion.button)<{ $variant?: 'primary' | 'secondary' }>`
  flex: 1;
  padding: 12px 24px;
  background: ${props => props.$variant === 'primary' 
    ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.9), rgba(139, 92, 246, 0.9))' 
    : 'rgba(255, 255, 255, 0.05)'};
  border: 1px solid ${props => props.$variant === 'primary' 
    ? 'rgba(59, 130, 246, 0.5)' 
    : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.$variant === 'primary' 
      ? 'linear-gradient(135deg, rgba(59, 130, 246, 1), rgba(139, 92, 246, 1))' 
      : 'rgba(255, 255, 255, 0.08)'};
    border-color: ${props => props.$variant === 'primary' 
      ? 'rgba(59, 130, 246, 0.7)' 
      : 'rgba(255, 255, 255, 0.2)'};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

// ==================== Helper Functions ====================

const getUserColor = (userId: string): string => {
  const colors = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  ];
  const index = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
  return colors[index];
};

// Note: we intentionally avoid using `dangerouslySetInnerHTML` anywhere in this
// component. Instead we return React nodes so React will safely escape content
// and we only wrap matched text in <mark> elements.
const highlightText = (text: string, query: string): React.ReactNode => {
  if (!query) return text;

  // Escape regex metacharacters in the query so it is treated as a literal
  const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  // Split the original text on the query (case-insensitive) and insert <mark>
  // elements for matches. Rendering strings directly is safe because React
  // escapes text nodes automatically.
  const parts = text.split(new RegExp(`(${escapedQuery})`, 'gi'));
  const matchExact = new RegExp(`^${escapedQuery}$`, 'i');

  return parts.map((part, i) => (
    matchExact.test(part) ? <mark key={i}>{part}</mark> : part
  ));
};

// ==================== MentionInput Component ====================

export const MentionInput: React.FC<MentionInputProps> = ({
  value,
  onChange,
  onMention,
  users,
  placeholder = 'Type @ to mention someone...',
  disabled = false,
}) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [mentionQuery, setMentionQuery] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const cursorPosition = textareaRef.current?.selectionStart || 0;
    const textBeforeCursor = value.substring(0, cursorPosition);
    const lastAtIndex = textBeforeCursor.lastIndexOf('@');

    if (lastAtIndex >= 0 && (lastAtIndex === 0 || /\s/.test(textBeforeCursor[lastAtIndex - 1]))) {
      const query = textBeforeCursor.substring(lastAtIndex + 1);
      if (!query.includes(' ')) {
        setMentionQuery(query);
        const filtered = users.filter(user =>
          user.name.toLowerCase().includes(query.toLowerCase()) ||
          (user.username && user.username.toLowerCase().includes(query.toLowerCase()))
        );
        setFilteredUsers(filtered);
        setShowDropdown(filtered.length > 0);
        setSelectedIndex(0);
        return;
      }
    }

    setShowDropdown(false);
  }, [value, users]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showDropdown) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, filteredUsers.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' || e.key === 'Tab') {
      e.preventDefault();
      if (filteredUsers[selectedIndex]) {
        handleSelectUser(filteredUsers[selectedIndex]);
      }
    } else if (e.key === 'Escape') {
      setShowDropdown(false);
    }
  };

  const handleSelectUser = (user: User) => {
    const cursorPosition = textareaRef.current?.selectionStart || 0;
    const textBeforeCursor = value.substring(0, cursorPosition);
    const lastAtIndex = textBeforeCursor.lastIndexOf('@');
    const textAfterCursor = value.substring(cursorPosition);

    const newValue = 
      value.substring(0, lastAtIndex) + 
      `@${user.username || user.name} ` + 
      textAfterCursor;

    onChange(newValue);
    onMention(user);
    setShowDropdown(false);

    // Set cursor after mention
    setTimeout(() => {
      const newPosition = lastAtIndex + (user.username || user.name).length + 2;
      textareaRef.current?.setSelectionRange(newPosition, newPosition);
      textareaRef.current?.focus();
    }, 0);
  };

  return (
    <MentionInputContainer>
      <AnimatePresence>
        {showDropdown && (
          <MentionDropdown
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
          >
            {filteredUsers.map((user, index) => (
              <MentionItem
                key={user.id}
                $active={index === selectedIndex}
                onClick={() => handleSelectUser(user)}
                whileHover={{ x: 4 }}
              >
                <MentionAvatar $color={getUserColor(user.id)}>
                  {user.name.charAt(0).toUpperCase()}
                </MentionAvatar>
                <MentionInfo>
                  <MentionName>{user.name}</MentionName>
                  {user.username && <MentionUsername>@{user.username}</MentionUsername>}
                </MentionInfo>
              </MentionItem>
            ))}
          </MentionDropdown>
        )}
      </AnimatePresence>

      <StyledTextarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
      />
    </MentionInputContainer>
  );
};

// ==================== SearchPanel Component ====================

export const SearchPanel: React.FC<SearchPanelProps> = ({
  messages,
  users,
  onMessageSelect,
  onClose,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({ type: 'all' });
  const [results, setResults] = useState<Message[]>([]);

  useEffect(() => {
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

  const filtered = messages.filter(msg => {
      // Type filter
      if (filters.type !== 'all' && msg.type !== filters.type) return false;
      
      // Sender filter
      if (filters.sender && msg.sender.id !== filters.sender) return false;
      
      // Attachment filters
      if (filters.hasAttachments && !msg.attachments?.length) return false;
  if (filters.hasCode && !(msg.codeBlocks && msg.codeBlocks.length > 0)) return false;
  if (filters.hasChart && !(msg.charts && msg.charts.length > 0)) return false;
      
      // Text search
      return msg.content.toLowerCase().includes(searchQuery.toLowerCase());
    });

    setResults(filtered);
  }, [searchQuery, filters, messages]);

  return (
    <SearchOverlay
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <SearchContainer
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <SearchHeader>
          <SearchInputWrapper>
            <SearchIcon>
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" />
              </svg>
            </SearchIcon>
            <SearchInput
              type="text"
              placeholder="Search messages..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              autoFocus
            />
          </SearchInputWrapper>

          <FilterRow>
            <FilterChip
              $active={filters.type === 'all'}
              onClick={() => setFilters({ ...filters, type: 'all' })}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              All
            </FilterChip>
            <FilterChip
              $active={filters.hasCode || false}
              onClick={() => setFilters({ ...filters, hasCode: !filters.hasCode })}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              💻 Code
            </FilterChip>
            <FilterChip
              $active={filters.hasChart || false}
              onClick={() => setFilters({ ...filters, hasChart: !filters.hasChart })}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              📊 Charts
            </FilterChip>
            <FilterChip
              $active={filters.hasAttachments || false}
              onClick={() => setFilters({ ...filters, hasAttachments: !filters.hasAttachments })}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              📎 Attachments
            </FilterChip>
          </FilterRow>
        </SearchHeader>

        <SearchResults>
          {results.length > 0 ? (
            results.map(msg => (
              <SearchResultItem
                key={msg.id}
                onClick={() => onMessageSelect(msg.id)}
                whileHover={{ x: 4 }}
              >
                <ResultHeader>
                  <ResultSender>{msg.sender.name}</ResultSender>
                  <ResultTimestamp>
                    {new Date(msg.timestamp).toLocaleString()}
                  </ResultTimestamp>
                </ResultHeader>
                <ResultContent>
                  {highlightText(msg.content, searchQuery)}
                </ResultContent>
              </SearchResultItem>
            ))
          ) : searchQuery ? (
            <NoResults>
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke="currentColor" strokeWidth="2" fill="none" />
              </svg>
              <p>No messages found</p>
              <HintText>Try a different search term or adjust filters</HintText>
            </NoResults>
          ) : (
            <NoResults>
              <p>Start typing to search messages</p>
            </NoResults>
          )}
        </SearchResults>
      </SearchContainer>
    </SearchOverlay>
  );
};

// ==================== ExportDialog Component ====================

export const ExportDialog: React.FC<ExportDialogProps> = ({
  messages,
  onClose,
  onExport,
}) => {
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'markdown' | 'json' | 'html'>('markdown');
  const [options, setOptions] = useState<ExportOptions>({
    includeAttachments: true,
    includeReactions: true,
    includeThreads: true,
    includeSystemMessages: false,
  });

  const formats = [
    { id: 'pdf', name: 'PDF', icon: '📄', desc: 'Formatted document' },
    { id: 'markdown', name: 'Markdown', icon: '📝', desc: 'Plain text with formatting' },
    { id: 'json', name: 'JSON', icon: '🔧', desc: 'Structured data' },
    { id: 'html', name: 'HTML', icon: '🌐', desc: 'Web page' },
  ];

  const handleExport = () => {
    onExport(selectedFormat, options);
  };

  return (
    <SearchOverlay
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <ExportContainer
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <SearchHeader>
          <SectionTitle>Export Conversation</SectionTitle>
          <ExportInfo>{messages.length} messages will be exported</ExportInfo>
        </SearchHeader>

        <SearchResults>
          <ExportSection>
            <SectionTitle>Format</SectionTitle>
            <FormatGrid>
              {formats.map(format => (
                <FormatOption
                  key={format.id}
                  $selected={selectedFormat === format.id}
                  onClick={() => setSelectedFormat(format.id as any)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <FormatIcon>{format.icon}</FormatIcon>
                  <FormatName>{format.name}</FormatName>
                  <FormatDesc>{format.desc}</FormatDesc>
                </FormatOption>
              ))}
            </FormatGrid>
          </ExportSection>

          <ExportSection>
            <SectionTitle>Include</SectionTitle>
            <CheckboxGroup>
              <CheckboxLabel>
                <Checkbox
                  type="checkbox"
                  checked={options.includeAttachments}
                  onChange={(e) => setOptions({ ...options, includeAttachments: e.target.checked })}
                />
                <CheckboxText>Attachments and files</CheckboxText>
              </CheckboxLabel>
              <CheckboxLabel>
                <Checkbox
                  type="checkbox"
                  checked={options.includeReactions}
                  onChange={(e) => setOptions({ ...options, includeReactions: e.target.checked })}
                />
                <CheckboxText>Reactions and emojis</CheckboxText>
              </CheckboxLabel>
              <CheckboxLabel>
                <Checkbox
                  type="checkbox"
                  checked={options.includeThreads}
                  onChange={(e) => setOptions({ ...options, includeThreads: e.target.checked })}
                />
                <CheckboxText>Thread replies</CheckboxText>
              </CheckboxLabel>
              <CheckboxLabel>
                <Checkbox
                  type="checkbox"
                  checked={options.includeSystemMessages}
                  onChange={(e) => setOptions({ ...options, includeSystemMessages: e.target.checked })}
                />
                <CheckboxText>System messages</CheckboxText>
              </CheckboxLabel>
            </CheckboxGroup>
          </ExportSection>
        </SearchResults>

        <ExportActions>
          <ActionButton onClick={onClose} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            Cancel
          </ActionButton>
          <ActionButton
            $variant="primary"
            onClick={handleExport}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Export {selectedFormat.toUpperCase()}
          </ActionButton>
        </ExportActions>
      </ExportContainer>
    </SearchOverlay>
  );
};

export default { MentionInput, SearchPanel, ExportDialog };
