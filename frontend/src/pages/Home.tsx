import React, { useMemo } from 'react';
import { ChatContainer } from '../components/Chat/ChatContainer';
import { Message, User } from '../types/chat';
import './Home.css';

// Small, well-formed python snippet used in demo message
const PYTHON_LOAD_SNIPPET = `import pandas as pd

def load_sales_data(file_path):
    """Loads sales data from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        print("File loaded successfully!")
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
`;

const Home: React.FC = () => {
  const currentUser: User = useMemo(() => ({
    id: 'user1',
    email: 'viren@example.com',
    name: 'Viren',
    avatar: 'https://i.pravatar.cc/150?u=user1',
  }), []);

  const spartaUser: User = useMemo(() => ({
    id: 'sparta-ai',
    email: 'ai@sparta.com',
    name: 'Sparta AI',
    avatar: 'https://i.pravatar.cc/150?u=sparta-ai',
  }), []);

  const mockMessages: Message[] = useMemo(() => [
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
      content:
        'Of course. I can help with that. First, please upload your data file. In the meantime, here is a Python script to get you started with loading a CSV file.',
      timestamp: new Date(),
      status: 'sent',
      codeBlocks: [
        {
          language: 'python',
          code: PYTHON_LOAD_SNIPPET,
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
  ], [currentUser, spartaUser]);

  return (
    <div className="home-root">
      <ChatContainer messages={mockMessages} currentUser={currentUser} />
    </div>
  );
};

export default Home;