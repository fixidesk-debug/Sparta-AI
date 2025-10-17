import { create } from "zustand";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  images?: string[]; // Base64 encoded images
  fileId?: string;
}

export interface ChatFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: Date;
}

interface ChatState {
  messages: Message[];
  currentFile: ChatFile | null;
  isLoading: boolean;
  addMessage: (message: Omit<Message, "id" | "timestamp">) => void;
  setMessages: (messages: Message[]) => void;
  setCurrentFile: (file: ChatFile | null) => void;
  setIsLoading: (loading: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  currentFile: null,
  isLoading: false,
  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: Date.now().toString(),
          timestamp: new Date(),
        },
      ],
    })),
  setMessages: (messages) => set({ messages }),
  setCurrentFile: (file) => set({ currentFile: file }),
  setIsLoading: (loading) => set({ isLoading: loading }),
  clearMessages: () => set({ messages: [] }),
}));
