/**
 * useChat hook — manages chat state, SSE streaming, and message history.
 */

import { useState, useRef, useCallback } from 'react';
import { streamChat } from '../services/api';

export default function useChat() {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [agentStatus, setAgentStatus] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  const sendMessage = useCallback((text) => {
    if (!text.trim() || isStreaming) return;

    setError(null);

    // Add user message
    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
    };

    // Add placeholder for assistant response
    const assistantMsg = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      isStreaming: true,
    };

    setMessages(prev => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);
    setAgentStatus(null);

    // Start SSE stream
    const abort = streamChat(text, conversationId, {
      onToken: (content) => {
        setMessages(prev => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.role === 'assistant') {
            updated[updated.length - 1] = {
              ...last,
              content: last.content + content,
            };
          }
          return updated;
        });
      },

      onAgentStatus: (status) => {
        setAgentStatus(status);
      },

      onDone: (data) => {
        setIsStreaming(false);
        setAgentStatus(null);

        // Update conversation ID
        if (data.conversationId) {
          setConversationId(data.conversationId);
        }

        // Mark message as done streaming
        setMessages(prev => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.role === 'assistant') {
            updated[updated.length - 1] = {
              ...last,
              isStreaming: false,
              agentsUsed: data.agents_used,
              cached: data.cached,
            };
          }
          return updated;
        });
      },

      onError: (err) => {
        setIsStreaming(false);
        setAgentStatus(null);
        setError(err.message || 'Something went wrong');

        // Update the assistant message with error
        setMessages(prev => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.role === 'assistant' && !last.content) {
            updated[updated.length - 1] = {
              ...last,
              content: '⚠️ Failed to get a response. Please check that the backend is running and your API key is configured.',
              isStreaming: false,
              isError: true,
            };
          }
          return updated;
        });
      },
    });

    abortRef.current = abort;
  }, [conversationId, isStreaming]);

  const stopStreaming = useCallback(() => {
    if (abortRef.current) {
      abortRef.current();
      setIsStreaming(false);
      setAgentStatus(null);

      setMessages(prev => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === 'assistant') {
          updated[updated.length - 1] = { ...last, isStreaming: false };
        }
        return updated;
      });
    }
  }, []);

  const loadConversation = useCallback((convId, convMessages) => {
    setConversationId(convId);
    setMessages(convMessages.map(m => ({
      id: m.id,
      role: m.role,
      content: m.content,
      agentType: m.agent_type,
    })));
    setError(null);
    setAgentStatus(null);
  }, []);

  const startNewChat = useCallback(() => {
    if (abortRef.current) abortRef.current();
    setMessages([]);
    setConversationId(null);
    setIsStreaming(false);
    setAgentStatus(null);
    setError(null);
  }, []);

  return {
    messages,
    isStreaming,
    agentStatus,
    conversationId,
    error,
    sendMessage,
    stopStreaming,
    loadConversation,
    startNewChat,
  };
}
