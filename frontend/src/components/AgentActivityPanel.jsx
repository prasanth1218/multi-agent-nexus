/**
 * AgentActivityPanel — Shows which agents are active and their status.
 */

const AGENT_INFO = {
  planner: { icon: '🧠', label: 'Planner' },
  coder: { icon: '💻', label: 'Coder' },
  writer: { icon: '✍️', label: 'Writer' },
  researcher: { icon: '🔍', label: 'Researcher' },
  reviewer: { icon: '✅', label: 'Reviewer' },
  cache: { icon: '⚡', label: 'Cache' },
};

export default function AgentActivityPanel({ status }) {
  if (!status) return null;

  const { agents = [], status: agentState, plan } = status;

  return (
    <div className="agent-activity">
      <div className="agent-activity-inner">
        {agentState !== 'complete' && <div className="agent-spinner" />}
        <div className="agent-badges">
          {agents.map(agent => {
            const info = AGENT_INFO[agent] || { icon: '🤖', label: agent };
            return (
              <span key={agent} className={`agent-badge ${agent}`}>
                {info.icon} {info.label}
              </span>
            );
          })}
        </div>
        {plan && <span className="agent-status-text">{plan}</span>}
      </div>
    </div>
  );
}
