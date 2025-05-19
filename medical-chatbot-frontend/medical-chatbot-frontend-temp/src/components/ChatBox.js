import React, { useRef, useEffect } from 'react';
import './ChatBox.css';
import Message from './Message';

function ChatBox({ messages, isLoading }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  return (
    <div className="chat-box">
      {messages.map((message, index) => (
        <Message key={index} text={message.text} sender={message.sender} />
      ))}
      {isLoading && <div className="typing-indicator">Bot is typing...</div>}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default ChatBox; 