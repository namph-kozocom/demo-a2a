'use client';

import { useState, useEffect, useRef } from 'react';
import ChatPanel from '@/components/ChatPanel';
import CodePanel from '@/components/CodePanel';
import Header from '@/components/Header';
import styles from './page.module.css';

export default function Home() {
  const [files, setFiles] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('code');
  const [messages, setMessages] = useState<Array<{
    role: 'user' | 'assistant' | 'system';
    content: string;
    agent?: string;
  }>>([
    {
      role: 'system',
      content: 'Welcome to A2A Web Builder! I coordinate three specialized agents to help you build web applications.',
      agent: 'Analyst'
    }
  ]);

  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/ws');
      
      ws.onopen = () => {
        console.log('Connected to backend');
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        // Add message to chat
        setMessages(prev => [...prev, {
          role: data.role,
          content: data.content,
          agent: data.agent
        }]);
        
        // Update files if provided
        if (data.files) {
          console.log('Updating files:', data.files);
          setFiles(data.files);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('Disconnected from backend');
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
      
      wsRef.current = ws;
    };
    
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleSendMessage = async (message: string) => {
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    
    // Send to backend via WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        content: message
      }));
    } else {
      // Fallback if WebSocket is not connected
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Backend is not connected. Please make sure the Python server is running on port 8000.',
      }]);
    }
  };

  return (
    <div className={styles.container}>
      <Header activeTab={activeTab} onTabChange={setActiveTab} />
      <div className={styles.mainContent}>
        <div className={styles.codeArea}>
          <CodePanel files={files} activeTab={activeTab} />
        </div>
        <div className={styles.chatArea}>
          <ChatPanel messages={messages} onSendMessage={handleSendMessage} />
        </div>
      </div>
    </div>
  );
}
