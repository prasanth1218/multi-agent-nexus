/**
 * App.jsx — Main application component connecting everything together.
 */

import { useState, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import useChat from './hooks/useChat';
import useConversations from './hooks/useConversations';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const {
    messages,
    isStreaming,
    agentStatus,
    conversationId,
    error,
    sendMessage,
    stopStreaming,
    loadConversation,
    startNewChat,
  } = useChat();

  const {
    conversations,
    fetchConversations,
    loadConversation: fetchConv,
    removeConversation,
  } = useConversations();

  const handleSendMessage = useCallback((text) => {
    sendMessage(text);
    // Refresh conversations list after a delay (to pick up new conversation)
    setTimeout(() => fetchConversations(), 2000);
  }, [sendMessage, fetchConversations]);

  const handleSelectConversation = useCallback(async (convId) => {
    const data = await fetchConv(convId);
    if (data) {
      loadConversation(convId, data.messages || []);
    }
    setSidebarOpen(false);
  }, [fetchConv, loadConversation]);

  const handleNewChat = useCallback(() => {
    startNewChat();
    setSidebarOpen(false);
  }, [startNewChat]);

  const handleDeleteConversation = useCallback(async (convId) => {
    const success = await removeConversation(convId);
    if (success && convId === conversationId) {
      startNewChat();
    }
  }, [removeConversation, conversationId, startNewChat]);

  return (
    <div className="app-layout">
      <Sidebar
        conversations={conversations}
        activeConversationId={conversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <ChatInterface
        messages={messages}
        isStreaming={isStreaming}
        agentStatus={agentStatus}
        error={error}
        onSendMessage={handleSendMessage}
        onStopStreaming={stopStreaming}
        onToggleSidebar={() => setSidebarOpen(prev => !prev)}
      />
    </div>
  );
}
