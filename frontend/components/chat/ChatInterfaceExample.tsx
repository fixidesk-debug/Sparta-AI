import React, { useState, useEffect } from 'react';
import ChatInterface, { Message, Conversation } from './ChatInterface';

// Sample data
const sampleConversations: Conversation[] = [
  {
    id: '1',
    title: 'Data Analysis Q&A',
    lastMessage: 'Here are the insights from your sales data...',
    timestamp: new Date(2024, 9, 14, 10, 30),
    unreadCount: 2
  },
  {
    id: '2',
    title: 'Report Generation',
    lastMessage: 'Your quarterly report is ready',
    timestamp: new Date(2024, 9, 13, 15, 45),
  },
  {
    id: '3',
    title: 'Chart Visualization',
    lastMessage: 'I\'ve created the chart you requested',
    timestamp: new Date(2024, 9, 12, 9, 20),
  }
];

const sampleMessages: Message[] = [
  {
    id: '1',
    content: 'Hello! Can you help me analyze my sales data?',
    sender: 'user',
    timestamp: new Date(2024, 9, 14, 10, 15),
    status: 'read',
    type: 'text'
  },
  {
    id: '2',
    content: 'Of course! I\'d be happy to help you analyze your sales data. Could you please upload the file or tell me what specific insights you\'re looking for?',
    sender: 'ai',
    timestamp: new Date(2024, 9, 14, 10, 15, 30),
    type: 'text'
  },
  {
    id: '3',
    content: 'I want to see trends over the past quarter',
    sender: 'user',
    timestamp: new Date(2024, 9, 14, 10, 16),
    status: 'read',
    type: 'text'
  },
  {
    id: '4',
    content: `import pandas as pd
import matplotlib.pyplot as plt

# Load sales data
df = pd.read_csv('sales_data.csv')

# Calculate quarterly trends
quarterly_sales = df.groupby('quarter')['revenue'].sum()

# Create visualization
plt.figure(figsize=(10, 6))
plt.plot(quarterly_sales.index, quarterly_sales.values)
plt.title('Quarterly Sales Trends')
plt.show()`,
    sender: 'ai',
    timestamp: new Date(2024, 9, 14, 10, 16, 45),
    type: 'code',
    metadata: {
      language: 'python'
    }
  },
  {
    id: '5',
    content: 'I\'ve analyzed your quarterly trends. Here\'s what I found:\n\n1. Q1 showed 15% growth\n2. Q2 had a slight dip of 3%\n3. Q3 recovered with 18% growth\n4. Q4 is projected to continue upward',
    sender: 'ai',
    timestamp: new Date(2024, 9, 14, 10, 17),
    type: 'text',
    reactions: [
      { emoji: '👍', count: 1 },
      { emoji: '🎉', count: 1 }
    ]
  }
];

const ChatInterfaceExample: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>(sampleMessages);
  const [conversations] = useState<Conversation[]>(sampleConversations);
  const [currentConversationId, setCurrentConversationId] = useState('1');
  const [isTyping, setIsTyping] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isOnline, setIsOnline] = useState(true);

  // Simulate AI typing
  const simulateAIResponse = (userMessage: string) => {
    setIsTyping(true);

    setTimeout(() => {
      setIsTyping(false);
      
      const aiResponse: Message = {
        id: Date.now().toString(),
        content: getAIResponse(userMessage),
        sender: 'ai',
        timestamp: new Date(),
        type: 'text'
      };

      setMessages(prev => [...prev, aiResponse]);
    }, 2000);
  };

  const getAIResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('help') || lowerMessage.includes('how')) {
      return 'I\'m Sparta AI, your intelligent data assistant. I can help you with:\n\n• Data analysis and insights\n• Creating visualizations\n• Generating reports\n• Answering questions about your data\n\nWhat would you like to explore today?';
    }
    
    if (lowerMessage.includes('chart') || lowerMessage.includes('visuali')) {
      return 'I can create various types of visualizations for you:\n\n📊 Bar charts\n📈 Line graphs\n🥧 Pie charts\n📉 Scatter plots\n\nWhich type would you prefer?';
    }
    
    if (lowerMessage.includes('data') || lowerMessage.includes('analyz')) {
      return 'I\'d be happy to analyze your data! Please upload your dataset, and I\'ll provide comprehensive insights including:\n\n• Statistical summaries\n• Trend analysis\n• Anomaly detection\n• Predictive insights';
    }
    
    return 'I understand you\'re asking about "' + userMessage.substring(0, 50) + '...". Let me help you with that. Could you provide more details about what you\'d like to know?';
  };

  const handleSendMessage = (content: string, files?: File[]) => {
    if (!content.trim() && (!files || files.length === 0)) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date(),
      status: 'sending',
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);

    // Simulate message being sent
    setTimeout(() => {
      setMessages(prev => 
        prev.map(msg => 
          msg.id === userMessage.id 
            ? { ...msg, status: 'sent' as const }
            : msg
        )
      );
    }, 500);

    // Simulate delivery
    setTimeout(() => {
      setMessages(prev => 
        prev.map(msg => 
          msg.id === userMessage.id 
            ? { ...msg, status: 'delivered' as const }
            : msg
        )
      );
    }, 1000);

    // Simulate read
    setTimeout(() => {
      setMessages(prev => 
        prev.map(msg => 
          msg.id === userMessage.id 
            ? { ...msg, status: 'read' as const }
            : msg
        )
      );
      
      // Trigger AI response
      simulateAIResponse(content);
    }, 1500);
  };

  const handleSelectConversation = (id: string) => {
    setCurrentConversationId(id);
    // In a real app, load messages for this conversation
    console.log('Selected conversation:', id);
  };

  const handleVoiceInput = () => {
    console.log('Voice input activated');
    setIsProcessing(true);
    
    setTimeout(() => {
      setIsProcessing(false);
      handleSendMessage('This is a sample voice input message');
    }, 2000);
  };

  // Simulate online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <div className="chat-example-container">
      <ChatInterface
        messages={messages}
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSendMessage={handleSendMessage}
        onSelectConversation={handleSelectConversation}
        onVoiceInput={handleVoiceInput}
        isTyping={isTyping}
        isProcessing={isProcessing}
        isOnline={isOnline}
        userName="User"
        aiName="Sparta AI"
      />
    </div>
  );
};

export default ChatInterfaceExample;
