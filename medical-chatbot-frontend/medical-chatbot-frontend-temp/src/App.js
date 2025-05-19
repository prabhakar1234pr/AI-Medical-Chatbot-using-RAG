import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('Checking...');
  const [sessionId, setSessionId] = useState(null);
  const [tools, setTools] = useState([]);

  // Check if the API is reachable and get available tools on component mount
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check API health
        const healthResponse = await fetch('http://localhost:8000/');
        const healthData = await healthResponse.json();
        setApiStatus(healthData.message || 'API is connected');
        
        // Get available tools
        const toolsResponse = await fetch('http://localhost:8000/tools');
        const toolsData = await toolsResponse.json();
        setTools(toolsData.tools || []);
      } catch (error) {
        console.error('API initialization error:', error);
        setApiStatus('API connection failed');
      }
    };
    
    initializeApp();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage]
        }),
      });
      
      const data = await response.json();
      console.log("API Response:", data); // Debug: Log the full response
      
      if (data.status === 'success') {
        const botMessage = { 
          role: 'assistant', 
          content: data.response,
          tool: data.tool_used  // Store the tool used
        };
        console.log("Bot message with tool:", botMessage); // Debug: Log the message we're adding
        setMessages(prev => [...prev, botMessage]);
        
        // Save session ID if provided
        if (data.session_id) {
          setSessionId(data.session_id);
        }
      } else {
        const errorMessage = { 
          role: 'assistant', 
          content: `Error: ${data.response || 'Something went wrong'}` 
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error connecting to the server. Please try again.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Medical Chatbot Demo</h1>
        <div className="api-status">API status: {apiStatus}</div>
        {tools.length > 0 && (
          <div className="tools-list">
            Available Tools: {tools.join(', ')}
          </div>
        )}
      </header>
      <main className="chat-container">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Welcome to the Medical Chatbot!</h2>
              <p>This chatbot can help you with:</p>
              <ul>
                <li>Answering medical questions</li>
                <li>Finding clinics by location or specialty</li>
                <li>Providing information about medical services</li>
                <li>Looking up appointments</li>
                <li>Scheduling new appointments</li>
                <li>Comparing prices for medical services</li>
              </ul>
              <p>Try asking something like:</p>
              <ul>
                <li>"What are symptoms of the flu?"</li>
                <li>"Find dermatologists in Boston"</li>
                <li>"What services do you offer for prenatal care?"</li>
              </ul>
            </div>
          )}
          {messages.map((msg, idx) => {
            console.log("Rendering message:", msg); // Debug: Log each message as it's rendered
            return (
              <div key={idx} className={`message ${msg.role}`}>
                {msg.role === 'assistant' && msg.tool && (
                  <div className="tool-badge">Tool: {msg.tool}</div>
                )}
                {msg.content}
              </div>
            );
          })}
          {loading && <div className="message assistant">Thinking...</div>}
        </div>
        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={loading}
          />
          <button type="submit" disabled={loading}>Send</button>
        </form>
      </main>
    </div>
  );
}

export default App; 