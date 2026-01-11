import React, { useState, useEffect, useRef } from 'react';
import { sendMessage } from '../services/api';
import './ChatInterface.css';

const ChatInterface = ({ sessionId, onTriageComplete, disabled }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initial welcome message
    setMessages([{
      role: 'assistant',
      content: 'Welcome to MediQueue. I\'m here to help assess your condition. How can I help you today?'
    }]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading || disabled) return;

    const userMessage = input.trim();
    setInput('');
    setLoading(true);

    // Add user message to UI
    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);

    try {
      const response = await sendMessage(sessionId, userMessage);
      setMessages([...newMessages, { role: 'assistant', content: response.response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([...newMessages, {
        role: 'assistant',
        content: 'I apologize, I\'m having trouble processing that. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <span className="typing-indicator">...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSend} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          disabled={loading || disabled}
          className="chat-input"
        />
        <button type="submit" disabled={loading || disabled || !input.trim()} className="send-button">
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;

