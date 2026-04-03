/**
 * MessageBubble — Renders a single chat message with markdown + code highlighting.
 */

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import CodeBlock from './CodeBlock';

export default function MessageBubble({ message }) {
  const { role, content, isStreaming, isError, cached, agentsUsed } = message;

  return (
    <div className={`message ${role}`} id={`msg-${message.id}`}>
      <div className="message-avatar">
        {role === 'user' ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <div className="message-role">
          {role === 'user' ? 'You' : 'NexusAI'}
          {cached && <span style={{ marginLeft: 8, color: 'var(--agent-cache)', fontSize: 'var(--fs-xs)' }}>⚡ Cached</span>}
          {agentsUsed && agentsUsed.length > 0 && (
            <span style={{ marginLeft: 8, color: 'var(--text-muted)', fontSize: 'var(--fs-xs)', fontWeight: 400, textTransform: 'none' }}>
              via {agentsUsed.join(', ')}
            </span>
          )}
        </div>
        <div className={`message-text ${isError ? 'error' : ''}`}>
          {content ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  if (!inline && match) {
                    return (
                      <CodeBlock language={match[1]}>
                        {children}
                      </CodeBlock>
                    );
                  }
                  return (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {content}
            </ReactMarkdown>
          ) : (
            isStreaming && <span className="streaming-cursor" />
          )}
          {isStreaming && content && <span className="streaming-cursor" />}
        </div>
      </div>
    </div>
  );
}
