/**
 * Chat Interface Type Definitions
 * Comprehensive TypeScript types for Sparta AI chat system
 */

export interface User {
  id: string;
  email: string;
  name?: string;
  avatar?: string;
}

export interface Message {
  id: string;
  conversationId: string;
  user: User;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  status: MessageStatus;
  metadata?: MessageMetadata;
  attachments?: Attachment[];
  codeBlocks?: CodeBlock[];
  visualizations?: Visualization[];
  error?: string;
}

export type MessageStatus = 
  | 'sending' 
  | 'sent' 
  | 'delivered' 
  | 'error' 
  | 'processing';

export interface MessageMetadata {
  fileId?: number;
  analysisType?: string;
  executionTime?: number;
  tokens?: number;
  model?: string;
  isStreaming?: boolean;
}

export interface Attachment {
  id: string;
  filename: string;
  name: string;
  size: number;
  type: string;
  url?: string;
  uploadProgress?: number;
  uploadStatus: 'pending' | 'uploading' | 'complete' | 'error';
  error?: string;
}

export interface CodeBlock {
  language: string;
  code: string;
  isValid?: boolean;
  validationErrors?: string[];
  error?: string;
  filename?: string;
}

export interface Visualization {
  id: string;
  type: 'plotly' | 'matplotlib' | 'table' | 'image';
  title?: string;
  data: any;
  layout?: any;
  config?: any;
  metadata?: string;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
  fileIds?: number[];
}

export interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: Message[];
  isConnected: boolean;
  isTyping: boolean;
  error?: string;
}

export interface WebSocketMessage {
  type: 'message' | 'typing' | 'status' | 'error' | 'connection';
  payload: any;
  timestamp: string;
}

export interface FileUploadProgress {
  fileId: string;
  progress: number;
  loaded: number;
  total: number;
  status: 'uploading' | 'processing' | 'complete' | 'error';
}

export interface ChatSettings {
  theme: 'light' | 'dark' | 'auto';
  fontSize: 'small' | 'medium' | 'large';
  enableSounds: boolean;
  enableNotifications: boolean;
  autoScroll: boolean;
  showTimestamps: boolean;
  codeTheme: string;
}
