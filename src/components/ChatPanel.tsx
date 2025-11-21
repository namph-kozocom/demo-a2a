'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, Code, TestTube } from 'lucide-react';
import styles from './ChatPanel.module.css';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  agent?: string;
}

interface ChatPanelProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
}

export default function ChatPanel({ messages, onSendMessage }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
    }
  };

  const getAgentIcon = (agent?: string) => {
    switch (agent) {
      case 'Analyst':
        return <Bot size={16} />;
      case 'Developer':
        return <Code size={16} />;
      case 'Tester':
        return <TestTube size={16} />;
      default:
        return null;
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>Agent Chat</h2>
        <p>Collaborate with AI agents to build your app</p>
      </div>

      <div className={styles.messages}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`${styles.message} ${styles[msg.role]} animate-fade-in`}
          >
            {msg.agent && (
              <div className={styles.agentBadge}>
                {getAgentIcon(msg.agent)}
                <span>{msg.agent}</span>
              </div>
            )}
            <div className={styles.content}>{msg.content}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form className={styles.inputForm} onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe what you want to build..."
          className={styles.input}
        />
        <button type="submit" className={styles.sendButton} disabled={!input.trim()}>
          <Send size={20} />
        </button>
      </form>
    </div>
  );
}
