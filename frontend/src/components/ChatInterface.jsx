/**
 * ChatInterface — Main chat view with messages, agent status, and input.
 */

import { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import AgentActivityPanel from './AgentActivityPanel';

const SUGGESTIONS = [
  { icon: '💻', text: 'Write a Python function to sort a list using merge sort' },
  { icon: '✍️', text: 'Write a professional email requesting a project deadline extension' },
  { icon: '🔍', text: 'Explain how neural networks work in simple terms' },
  { icon: '🌐', text: 'Build a responsive landing page with HTML, CSS, and JavaScript' },
];

export default function ChatInterface({
  messages,
  isStreaming,
  agentStatus,
  error,
  onSendMessage,
  onStopStreaming,
  onToggleSidebar,
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, agentStatus]);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = Math.min(ta.scrollHeight, 150) + 'px';
    }
  }, [input]);

  const handleSubmit = () => {
    if (!input.trim() || isStreaming) return;
    onSendMessage(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSuggestionClick = (text) => {
    onSendMessage(text);
  };

  const showWelcome = messages.length === 0;

  return (
    <div className="main-content">
      {/* Header */}
      <header className="chat-header">
        <button className="mobile-menu-btn" onClick={onToggleSidebar} aria-label="Toggle sidebar">
          ☰
        </button>
        <h1 className="chat-header-title">
          {showWelcome ? 'NexusAI' : 'Chat'}
        </h1>
        <div style={{ width: 40 }} /> {/* Spacer for centering */}
      </header>

      {/* Messages or Welcome */}
      {showWelcome ? (
        <div className="welcome-screen">
          <div className="welcome-icon">⚡</div>
          <h2 className="welcome-title">NexusAI</h2>
          <p className="welcome-subtitle">
            Powered by multiple specialized AI agents working in parallel.
            Ask me to code, write, research, or solve any problem.
          </p>
          <div className="welcome-suggestions">
            {SUGGESTIONS.map((s, i) => (
              <div
                key={i}
                className="suggestion-card"
                onClick={() => handleSuggestionClick(s.text)}
                id={`suggestion-${i}`}
              >
                <div className="suggestion-icon">{s.icon}</div>
                <div className="suggestion-text">{s.text}</div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="messages-container">
          <div className="messages-list">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {agentStatus && <AgentActivityPanel status={agentStatus} />}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      {/* Input */}
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <div className="chat-input-box">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask NexusAI anything..."
              rows={1}
              disabled={isStreaming}
              id="chat-input"
              aria-label="Chat input"
            />
            {isStreaming ? (
              <button
                className="send-btn"
                onClick={onStopStreaming}
                aria-label="Stop generating"
                style={{ background: 'var(--error)' }}
              >
                ■
              </button>
            ) : (
              <button
                className="send-btn"
                onClick={handleSubmit}
                disabled={!input.trim()}
                aria-label="Send message"
                id="send-button"
              >
                ↑
              </button>
            )}
          </div>
          <div className="chat-input-hint">
            Press Enter to send · Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
}
