export type MessageType = 'query' | 'analysis' | 'result' | 'error';
export type MessageStatus = 'sending' | 'sent' | 'failed';

export interface User {
  id: string;
  name: string;
  avatar: string;
  isOnline: boolean;
}

export interface Attachment {
  id: string;
  name: string;
  type: string;
  size: number;
  url: string;
  thumbnail?: string;
}

export interface CodeBlock {
  language: string;
  code: string;
  runnable: boolean;
}

export interface ChartData {
  type: 'line' | 'bar' | 'pie' | 'scatter';
  data: any;
  title: string;
}

export interface Reaction {
  emoji: string;
  users: string[];
}

export interface Message {
  id: string;
  content: string;
  type: MessageType;
  sender: User;
  timestamp: Date;
  status?: MessageStatus;
  attachments?: Attachment[];
  codeBlocks?: CodeBlock[];
  charts?: ChartData[];
  reactions?: Reaction[];
  threadId?: string;
  mentions?: string[];
  isEdited?: boolean;
}

export interface TypingUser {
  userId: string;
  userName: string;
}
