/**
 * Chat Interface Types
 * Comprehensive type definitions for Sparta AI chat system
 */

export type MessageType = 'query' | 'analysis' | 'result' | 'error' | 'system';
export type MessageStatus = 'sending' | 'sent' | 'delivered' | 'read' | 'failed';
export type UserRole = 'user' | 'ai' | 'admin' | 'analyst';
export type UserStatus = 'online' | 'away' | 'busy' | 'offline';
export type AttachmentType = 'image' | 'file' | 'csv' | 'code' | 'audio' | 'video';
export type ReactionType = '👍' | '❤️' | '🎉' | '🤔' | '👀' | '🚀';

export interface User {
  id: string;
  name: string;
  username?: string;
  email: string;
  avatar?: string;
  role: UserRole;
  status: UserStatus;
  isTyping: boolean;
  lastSeen?: Date;
  color?: string;
}

export interface Attachment {
  id: string;
  type: AttachmentType;
  name: string;
  url: string;
  size: number;
  mimeType: string;
  thumbnail?: string;
  metadata?: {
    width?: number;
    height?: number;
    duration?: number;
    rows?: number;
    columns?: number;
  };
}

export interface CodeBlock {
  language: string;
  code: string;
  fileName?: string;
  isCollapsed: boolean;
  canExecute: boolean;
  output?: string;
  executionTime?: number;
}

export interface ChartData {
  id: string;
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'heatmap' | 'area';
  title: string;
  data: any;
  config?: any;
  isExpanded: boolean;
}

export interface Reaction {
  id: string;
  type: ReactionType;
  userId: string;
  userName: string;
  timestamp: Date;
}

export interface Mention {
  id: string;
  userId: string;
  userName: string;
  startIndex: number;
  endIndex: number;
}

export interface MessageThread {
  id: string;
  parentMessageId: string;
  messages: Message[];
  participantIds: string[];
  isCollapsed: boolean;
}

export interface Message {
  id: string;
  content: string;
  type: MessageType;
  status: MessageStatus;
  sender: User;
  timestamp: Date;
  editedAt?: Date;
  attachments?: Attachment[];
  codeBlocks?: CodeBlock[];
  charts?: ChartData[];
  reactions?: Reaction[];
  mentions?: Mention[];
  threadId?: string;
  parentMessageId?: string;
  replyCount?: number;
  isEdited: boolean;
  isPinned: boolean;
  metadata?: {
    modelUsed?: string;
    tokensUsed?: number;
    executionTime?: number;
    confidence?: number;
  };
}

export interface VoiceMessage {
  id: string;
  url: string;
  duration: number;
  waveformData: number[];
  isPlaying: boolean;
  currentTime: number;
  transcript?: string;
}

export interface SmartSuggestion {
  id: string;
  text: string;
  type: 'query' | 'action' | 'analysis';
  icon?: string;
  context?: string;
}

export interface ChatState {
  messages: Message[];
  threads: MessageThread[];
  users: User[];
  currentUser: User;
  activeThread?: string;
  searchQuery: string;
  searchResults: Message[];
  isSearching: boolean;
  suggestions: SmartSuggestion[];
  typingUsers: string[];
  scrollPosition: number;
  isLoading: boolean;
}

export interface MessageAction {
  id: string;
  label: string;
  icon: string;
  handler: (message: Message) => void;
  requiresConfirmation?: boolean;
  confirmationMessage?: string;
}

export interface ExportOptions {
  format: 'pdf' | 'markdown' | 'json' | 'html';
  includeAttachments: boolean;
  includeCharts: boolean;
  includeMetadata: boolean;
  dateRange?: {
    start: Date;
    end: Date;
  };
  messageTypes?: MessageType[];
}

export interface ChatFilter {
  type?: MessageType;
  sender?: string;
  dateRange?: {
    start: Date;
    end: Date;
  };
  hasAttachments?: boolean;
  hasCharts?: boolean;
  isPinned?: boolean;
}

export interface NotificationPreferences {
  mentions: boolean;
  replies: boolean;
  reactions: boolean;
  newMessages: boolean;
  sound: boolean;
  desktop: boolean;
}
