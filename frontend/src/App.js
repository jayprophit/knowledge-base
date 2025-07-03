import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// Mock data for demonstration purposes
const knowledgeBaseCategories = [
  { id: 'ai', name: 'Artificial Intelligence', icon: '🧠' },
  { id: 'robotics', name: 'Robotics', icon: '🤖' },
  { id: 'blockchain', name: 'Blockchain', icon: '🔗' },
  { id: 'multimodal', name: 'Multimodal', icon: '📊' },
  { id: 'vision', name: 'Computer Vision', icon: '👁️' },
  { id: 'quantum', name: 'Quantum Computing', icon: '⚛️' },
];

// Mock conversation history
const initialMessages = [
  { 
    id: 1, 
    role: 'assistant', 
    content: 'Hello! I\'m your AI assistant. I can help you explore the knowledge base, answer questions, generate code, and more. How can I help you today?',
    timestamp: new Date().toISOString()
  },
];

function App() {
  const [messages, setMessages] = useState(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isThinking, setIsThinking] = useState(false);
  const [userProfile, setUserProfile] = useState({
    name: 'User',
    avatar: 'https://via.placeholder.com/40',
    preferences: {
      theme: 'light',
      codeStyle: 'default',
      model: 'gpt-4',
    }
  });

  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };
    setMessages([...messages, userMessage]);
    setInputValue('');
    setIsThinking(true);

    // Simulate assistant response after a delay
    setTimeout(() => {
      const assistantMessage = {
        id: messages.length + 2,
        role: 'assistant',
        content: generateMockResponse(inputValue),
        timestamp: new Date().toISOString()
      };
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
      setIsThinking(false);
    }, 1500);
  };

  // Generate a mock response based on user input
  const generateMockResponse = (input) => {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('robotics') || lowerInput.includes('robot')) {
      return `
## Robotics in the Knowledge Base

The robotics section contains documentation on:

1. **Robot Perception** - Computer vision and sensor integration
2. **Motion Planning** - Algorithms for robot movement
3. **Robot Learning** - Machine learning for robotics

Would you like me to explain any of these topics in more detail, or would you like to see some code examples?
      `;
    } 
    else if (lowerInput.includes('multimodal') || lowerInput.includes('vision') || lowerInput.includes('audio')) {
      return `
## Multimodal AI Systems

Our knowledge base includes comprehensive documentation on multimodal AI systems that combine:

- 👁️ **Visual processing** (object detection, scene understanding)
- 🔊 **Audio processing** (speech recognition, sound classification)
- 🔄 **Cross-modal integration** techniques

The \`MultiModalRecognitionSystem\` class in \`src/multimodal/recognition_api.py\` provides a unified API for working with audio-visual data.

Would you like to see some example code for implementing multimodal recognition?
      `;
    }
    else if (lowerInput.includes('help') || lowerInput.includes('capabilities')) {
      return `
I can help you with the following:

1. **Knowledge Base Navigation** - Find and explain topics in the knowledge base
2. **Code Generation** - Create code examples and implementations
3. **Multimodal Interaction** - Process text, voice, and visual inputs
4. **Cross-Platform Development** - Guidance for web, mobile, and desktop
5. **AI Agent Integration** - Connect specialized AI agents for different domains

What would you like to explore today?
      `;
    }
    else {
      return `I'll help you explore that topic. The knowledge base contains extensive documentation on advanced AI, robotics, blockchain, and more. Could you tell me which specific aspect you're interested in?`;
    }
  };

  // Toggle voice recording
  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      // Simulate voice recording
      setTimeout(() => {
        setIsRecording(false);
        setInputValue("Show me information about multimodal recognition");
      }, 2000);
    }
  };

  // Render individual message
  const renderMessage = (message) => {
    const isAssistant = message.role === 'assistant';
    
    return (
      <div 
        key={message.id} 
        className={`message ${isAssistant ? 'assistant' : 'user'}`}
      >
        <div className="avatar">
          {isAssistant ? '🤖' : '👤'}
        </div>
        <div className="message-content">
          <div className="message-header">
            <span className="message-sender">{isAssistant ? 'AI Assistant' : userProfile.name}</span>
            <span className="message-time">
              {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
          <div className="message-text">
            {isAssistant ? (
              <div dangerouslySetInnerHTML={{ __html: convertMarkdownToHtml(message.content) }} />
            ) : (
              message.content
            )}
          </div>
        </div>
      </div>
    );
  };

  // Simple Markdown to HTML conversion for demo
  const convertMarkdownToHtml = (markdown) => {
    return markdown
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^# (.*$)/gm, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
  };

  return (
    <div className="app">
      <header className="app-header">
        <button className="menu-button" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
          ☰
        </button>
        <h1>Knowledge Base Assistant</h1>
        <div className="user-profile">
          <img src={userProfile.avatar} alt="User avatar" className="user-avatar" />
        </div>
      </header>

      <div className="app-container">
        {isSidebarOpen && (
          <aside className="sidebar">
            <div className="sidebar-section">
              <h2>Knowledge Categories</h2>
              <ul className="category-list">
                {knowledgeBaseCategories.map((category) => (
                  <li 
                    key={category.id} 
                    className={`category-item ${selectedCategory === category.id ? 'selected' : ''}`}
                    onClick={() => setSelectedCategory(category.id)}
                  >
                    <span className="category-icon">{category.icon}</span>
                    <span className="category-name">{category.name}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="sidebar-section">
              <h2>Recent Searches</h2>
              <ul className="recent-searches">
                <li>Multimodal AI integration</li>
                <li>Robot navigation systems</li>
                <li>Quantum computing basics</li>
              </ul>
            </div>

            <div className="sidebar-section">
              <h2>Settings</h2>
              <div className="settings-option">
                <label>Theme:</label>
                <select 
                  value={userProfile.preferences.theme}
                  onChange={(e) => setUserProfile({
                    ...userProfile, 
                    preferences: {...userProfile.preferences, theme: e.target.value}
                  })}
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System</option>
                </select>
              </div>
              
              <div className="settings-option">
                <label>AI Model:</label>
                <select 
                  value={userProfile.preferences.model}
                  onChange={(e) => setUserProfile({
                    ...userProfile, 
                    preferences: {...userProfile.preferences, model: e.target.value}
                  })}
                >
                  <option value="gpt-4">GPT-4</option>
                  <option value="claude-3">Claude 3</option>
                  <option value="local">Local Model</option>
                </select>
              </div>
            </div>
          </aside>
        )}

        <main className="chat-container">
          <div className="messages">
            {messages.map(renderMessage)}
            {isThinking && (
              <div className="thinking-indicator">
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="input-form" onSubmit={handleSubmit}>
            <button 
              type="button" 
              className={`voice-button ${isRecording ? 'recording' : ''}`}
              onClick={toggleRecording}
              title="Voice input"
            >
              🎤
            </button>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask me anything about the knowledge base..."
              className="message-input"
            />
            <button type="submit" className="send-button" disabled={!inputValue.trim()}>
              Send
            </button>
          </form>
        </main>
      </div>
    </div>
  );
}

export default App;
