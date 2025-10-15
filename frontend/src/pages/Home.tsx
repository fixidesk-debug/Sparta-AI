import React from 'react';
import { ChatContainer } from '../components/Chat/ChatContainer';
import { Message, User } from '../types/chat';

// Mock Data for demonstration
const currentUser: User = {
  id: 'user1',
  email: 'viren@example.com',
  name: 'Viren',
  avatar: 'https://i.pravatar.cc/150?u=user1',
};

const spartaUser: User = {
  id: 'sparta-ai',
  email: 'ai@sparta.com',
  name: 'Sparta AI',
  avatar: 'https://i.pravatar.cc/150?u=sparta-ai',
};

const mockMessages: Message[] = [
  {
    id: '1',
    conversationId: 'conv1',
    user: currentUser,
    role: 'user',
    content: 'How can I analyze my sales data from Q4 2024?',
    timestamp: new Date(),
    status: 'sent',
  },
  {
    id: '2',
    conversationId: 'conv1',
    user: spartaUser,
    role: 'assistant',
    content: 'Of course. I can help with that. First, please upload your data file. In the meantime, here is a Python script to get you started with loading a CSV file.',
    timestamp: new Date(),
    status: 'sent',
    codeBlocks: [
      {
        language: 'python',
        code: 'import pandas as pd\n\ndef load_sales_data(file_path):\n    """Loads sales data from a CSV file."""\n    try:\n        df = pd.read_csv(file_path)\n        console.log("File loaded successfully!")\n        return df\n    except FileNotFoundError:\n        console.log(f"Error: File not found at {file_path}")\n        return None',
      },
    ],
  },
  {
    id: '3',
    conversationId: 'conv1',
    user: currentUser,
    role: 'user',
    content: 'Thanks! File is attached.',
    timestamp: new Date(),
    status: 'sent',
  },
];

const Home: React.FC = () => {
  return (
    <div style={{ paddingTop: 'var(--spacing-4)', paddingBottom: 'var(--spacing-4)' }}>
      <ChatContainer messages={mockMessages} currentUser={currentUser} />
    </div>
  );
};

export default Home;