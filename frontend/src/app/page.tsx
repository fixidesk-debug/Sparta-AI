"use client";

import { MainLayout } from "@/components/layout/main-layout";
import { ChatInterface } from "@/components/chat/chat-interface";

export default function Home() {
  return (
    <MainLayout>
      <ChatInterface />
    </MainLayout>
  );
}
