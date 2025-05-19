import React, { useState } from 'react';
import './MessageInput.css';

function MessageInput({ onSendMessage, disabled }) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="message-input-container">
      <form className="message-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={disabled}
          className="message-input"
        />
        <button type="submit" disabled={disabled || !message.trim()} className="send-button">
          Send
        </button>
      </form>
    </div>
  );
}

export default MessageInput; 