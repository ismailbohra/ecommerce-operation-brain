import { MessageSquarePlus, Trash2 } from 'lucide-react'
import type { Session } from '@/types'

interface SessionListProps {
  sessions: Session[]
  activeSessionId: string
  onNew: () => void
  onSwitch: (id: string) => void
  onDelete: (id: string) => void
}

function relativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const minutes = Math.floor(diff / 60_000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return new Date(iso).toLocaleDateString()
}

export function SessionList({
  sessions,
  activeSessionId,
  onNew,
  onSwitch,
  onDelete,
}: SessionListProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <button
        onClick={onNew}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          width: '100%',
          padding: '8px 10px',
          borderRadius: 7,
          border: '1px solid var(--color-border)',
          background: 'var(--color-bg-muted)',
          fontSize: 13,
          fontWeight: 500,
          cursor: 'pointer',
          color: 'var(--color-fg)',
          marginBottom: 6,
        }}
      >
        <MessageSquarePlus size={14} />
        New Chat
      </button>

      {sessions.length === 0 && (
        <p style={{ fontSize: 12, color: 'var(--color-fg-muted)', padding: '4px 2px' }}>
          No conversations yet. Start chatting!
        </p>
      )}

      {sessions.map((s) => {
        const isActive = s.id === activeSessionId
        return (
          <div
            key={s.id}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              borderRadius: 7,
              background: isActive ? 'oklch(0.55 0.22 270 / 0.1)' : 'transparent',
              border: isActive ? '1px solid oklch(0.55 0.22 270 / 0.25)' : '1px solid transparent',
              padding: '2px 4px 2px 8px',
            }}
          >
            <button
              onClick={() => onSwitch(s.id)}
              style={{
                flex: 1,
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left',
                padding: '5px 0',
                minWidth: 0,
              }}
            >
              <div
                style={{
                  fontSize: 13,
                  fontWeight: isActive ? 600 : 400,
                  color: isActive ? 'var(--color-accent)' : 'var(--color-fg)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
                title={s.title}
              >
                {s.title}
              </div>
              <div style={{ fontSize: 11, color: 'var(--color-fg-muted)' }}>
                {relativeTime(s.updated_at)}
              </div>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                if (confirm('Delete this conversation?')) onDelete(s.id)
              }}
              title="Delete conversation"
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: 'var(--color-fg-muted)',
                padding: 4,
                borderRadius: 4,
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
              }}
            >
              <Trash2 size={13} />
            </button>
          </div>
        )
      })}
    </div>
  )
}
