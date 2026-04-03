/**
 * Sidebar — Conversation history and new chat button.
 */

export default function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  isOpen,
  onClose,
}) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && <div className="sidebar-overlay" onClick={onClose} style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
        zIndex: 99, display: 'none',
      }} />}

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon">⚡</div>
            <span className="logo-text">NexusAI</span>
          </div>
        </div>

        <button className="new-chat-btn" onClick={onNewChat} id="new-chat-button">
          ✦ New Chat
        </button>

        <div className="conversation-list">
          {conversations.length === 0 ? (
            <div style={{
              padding: '20px 16px',
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: 'var(--fs-sm)',
            }}>
              No conversations yet
            </div>
          ) : (
            conversations.map(conv => (
              <div
                key={conv.id}
                className={`conversation-item ${conv.id === activeConversationId ? 'active' : ''}`}
                onClick={() => onSelectConversation(conv.id)}
                id={`conv-${conv.id}`}
              >
                <span className="conv-icon">💬</span>
                <span className="conv-title">{conv.title}</span>
                <button
                  className="conv-delete"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conv.id);
                  }}
                  aria-label="Delete conversation"
                >
                  ✕
                </button>
              </div>
            ))
          )}
        </div>

        <div style={{
          padding: 'var(--space-4) var(--space-5)',
          borderTop: '1px solid var(--border-subtle)',
          fontSize: 'var(--fs-xs)',
          color: 'var(--text-muted)',
          textAlign: 'center',
        }}>
          Multi-Agent AI System v1.0
        </div>
      </aside>
    </>
  );
}
