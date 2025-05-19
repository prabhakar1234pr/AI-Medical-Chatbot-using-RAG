import React from 'react';
import './Message.css';

function Message({ text, sender }) {
  return (
    <div className={`message ${sender}`}>
      <div className="message-content">{text}</div>
    </div>
  );
}

export default Message; 