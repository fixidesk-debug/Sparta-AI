"use client";

import { ChatMessages } from "./chat-messages";
import { ChatInput } from "./chat-input";
import { FileUpload } from "./file-upload";
import { WelcomeScreen } from "./welcome-screen";
import { useChat } from "@/hooks/use-chat";
import { useChatStore } from "@/store/chat-store";

export function ChatInterface() {
  const { messages, sendMessage, isLoading } = useChat();
  const { currentFile } = useChatStore();

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-4xl px-4 py-8">
          {messages.length === 0 ? (
            <>
              <WelcomeScreen />
              <FileUpload />
            </>
          ) : (
            <>
              {currentFile && (
                <div className="mb-4 rounded-lg border border-border bg-card p-3">
                  <p className="text-sm">
                    <span className="font-medium">Current file:</span> {currentFile.name}
                  </p>
                </div>
              )}
              <ChatMessages messages={messages} isLoading={isLoading} />
            </>
          )}
        </div>
      </div>
      <div className="border-t border-border bg-card">
        <div className="mx-auto max-w-4xl px-4 py-4">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}
