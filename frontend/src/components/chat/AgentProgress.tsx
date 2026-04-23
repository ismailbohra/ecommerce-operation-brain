import type { AgentProgress } from '@/types'

const STAGE_LABELS: Record<AgentProgress['stage'], string> = {
  routing: 'Routing…',
  agents: 'Running agents',
  synthesizing: 'Synthesizing…',
  checking_actions: 'Checking actions…',
}

const AGENT_COLORS: Record<string, string> = {
  sales: '#3b82f6',
  inventory: '#f59e0b',
  support: '#ec4899',
  marketing: '#8b5cf6',
  memory: '#10b981',
}

interface Props {
  progress: AgentProgress
}

export function AgentProgress({ progress }: Props) {
  const { stage, agents } = progress
  const label = STAGE_LABELS[stage]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {/* Stage label with pulse dot */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span className="progress-dot" />
        <span style={{ fontSize: 12, color: 'var(--color-fg-muted)', fontWeight: 500 }}>
          {label}
        </span>
      </div>

      {/* Per-agent pills */}
      {agents.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {agents.map((a) => {
            const color = AGENT_COLORS[a.name] ?? '#6b7280'
            const isDone = a.status === 'done'
            return (
              <span
                key={a.name}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 4,
                  padding: '2px 8px',
                  borderRadius: 99,
                  fontSize: 11,
                  fontWeight: 500,
                  border: `1px solid ${color}40`,
                  background: `${color}18`,
                  color: isDone ? 'var(--color-fg-muted)' : color,
                  opacity: isDone ? 0.6 : 1,
                  transition: 'opacity 0.3s',
                }}
              >
                {!isDone && (
                  <span
                    style={{
                      width: 5,
                      height: 5,
                      borderRadius: '50%',
                      background: color,
                      animation: 'pulse 1.2s ease-in-out infinite',
                      display: 'inline-block',
                    }}
                  />
                )}
                {isDone && (
                  <svg width="8" height="8" viewBox="0 0 8 8" fill="none">
                    <path d="M1.5 4L3 5.5L6.5 2" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
                {a.name}
              </span>
            )
          })}
        </div>
      )}
    </div>
  )
}
