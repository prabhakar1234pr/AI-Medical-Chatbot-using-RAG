import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);

  const API_URL = 'https://ai-medical-chatbot-using-rag-2.onrender.com';

  // Check API connection on component mount
  useEffect(() => {
    const checkApi = async () => {
      try {
        const response = await axios.get(API_URL);
        console.log('API connection check:', response.data);
        setApiConnected(true);
      } catch (error) {
        console.error('API connection failed:', error);
        setApiConnected(false);
      }
    };
    
    checkApi();
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message to the chat
    const userMessage = { text: input, sender: 'user' };
    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Use the chat endpoint for real responses
      const response = await axios.post(`${API_URL}/chat`, {
        message: input
      });

      // Add bot response to the chat
      setMessages(prevMessages => [
        ...prevMessages,
        { text: response.data.message, sender: 'bot' }
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prevMessages => [
        ...prevMessages,
        { text: 'Sorry, there was an error processing your request.', sender: 'bot' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Medical Knowledge Chatbot</h1>
        {apiConnected ? (
          <span className="api-status connected">API Connected</span>
        ) : (
          <span className="api-status disconnected">API Disconnected</span>
        )}
      </header>
      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h2>Welcome to the Medical Knowledge Chatbot</h2>
              <p>Ask any medical question to get started.</p>
              {!apiConnected && (
                <p className="api-warning">Warning: The API is not connected. Your messages will not be processed.</p>
              )}
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`message ${message.sender}`}>
                <div className="message-content">{message.text}</div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="message bot loading">
              <div className="loading-dots">
                <span>.</span><span>.</span><span>.</span>
              </div>
            </div>
          )}
        </div>
        <form className="input-container" onSubmit={handleSendMessage}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your medical question here..."
            disabled={isLoading || !apiConnected}
          />
          <button type="submit" disabled={isLoading || !input.trim() || !apiConnected}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App; 