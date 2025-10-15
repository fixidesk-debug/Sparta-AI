// New Chat Interface (Modern, Comprehensive)
export { default as ChatInterface } from './ChatInterface';
export { default as ChatInterfaceExample } from './ChatInterfaceExample';
export type { Message, Conversation } from './ChatInterface';

// Main Chat Interface (Advanced Features)
export { ChatInterface as AdvancedChatInterface } from '../../src/components/chat/ChatInterface';

// Message Components
export { AdvancedMessageBubble } from '../../src/components/chat/AdvancedMessageBubble';
export { AdvancedCodeBlock } from '../../src/components/chat/AdvancedCodeBlock';
export { AdvancedChartPreview } from '../../src/components/chat/AdvancedChartPreview';

// Threading Components
export { MessageThread, ThreadView } from '../../src/components/chat/MessageThread';
export type { ThreadedMessage, MessageThreadProps, ThreadViewProps } from '../../src/components/chat/MessageThread';

// Presence Components
export { UserAvatar } from '../../src/components/chat/UserAvatar';
export { AdvancedTypingIndicator } from '../../src/components/chat/AdvancedTypingIndicator';
export { UserPresencePanel } from '../../src/components/chat/UserPresencePanel';

// Advanced Features
export { MentionInput, SearchPanel, ExportDialog } from '../../src/components/chat/AdvancedFeatures';
export type {
  MentionInputProps,
  SearchPanelProps,
  ExportDialogProps,
  ExportOptions,
  SearchFilters,
} from '../../src/components/chat/AdvancedFeatures';

// Legacy Components (keep for backward compatibility)
export { ChatContainer } from './ChatContainer';
export { ChatMessage } from './ChatMessage';
export { ChatInput } from './ChatInput';
export { CodeBlock } from './CodeBlock';
export { ChartPreview } from './ChartPreview';
export { TypingIndicator } from './TypingIndicator';

// Types
export * from './types';
