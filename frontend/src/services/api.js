/**
 * API service — handles SSE streaming and REST calls to the backend.
 */

const API_BASE = 'http://localhost:8000/api';

/**
 * Send a chat message and receive an SSE stream of events.
 * @param {string} message - The user's message
 * @param {string|null} conversationId - Existing conversation ID
 * @param {function} onToken - Callback for each token chunk
 * @param {function} onAgentStatus - Callback for agent status updates
 * @param {function} onDone - Callback when streaming is complete
 * @param {function} onError - Callback for errors
 * @returns {function} abort function to cancel the stream
 */
export function streamChat(message, conversationId, { onToken, onAgentStatus, onDone, onError }) {
  const controller = new AbortController();

  (async () => {
    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Get conversation ID from response header
      const newConvId = response.headers.get('X-Conversation-Id');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Parse SSE events from buffer
        const events = buffer.split('\n\n');
        buffer = events.pop() || ''; // Keep incomplete event in buffer

        for (const eventStr of events) {
          if (!eventStr.trim()) continue;

          const lines = eventStr.split('\n');
          let eventType = '';
          let eventData = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.slice(7);
            } else if (line.startsWith('data: ')) {
              eventData = line.slice(6);
            }
          }

          if (!eventType || !eventData) continue;

          try {
            const data = JSON.parse(eventData);

            switch (eventType) {
              case 'token':
                onToken?.(data.content, data.agent);
                break;
              case 'agent_status':
                onAgentStatus?.(data);
                break;
              case 'done':
                onDone?.({ ...data, conversationId: newConvId });
                break;
            }
          } catch (parseErr) {
            console.warn('Failed to parse SSE event:', parseErr);
          }
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        onError?.(err);
      }
    }
  })();

  return () => controller.abort();
}

/**
 * Fetch all conversations.
 */
export async function getConversations() {
  const res = await fetch(`${API_BASE}/conversations`);
  if (!res.ok) throw new Error('Failed to fetch conversations');
  const data = await res.json();
  return data.conversations;
}

/**
 * Fetch a single conversation with messages.
 */
export async function getConversation(id) {
  const res = await fetch(`${API_BASE}/conversations/${id}`);
  if (!res.ok) throw new Error('Failed to fetch conversation');
  return res.json();
}

/**
 * Delete a conversation.
 */
export async function deleteConversation(id) {
  const res = await fetch(`${API_BASE}/conversations/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete conversation');
  return res.json();
}

/**
 * Health check.
 */
export async function healthCheck() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}
