import { cn } from '@/lib/utils'

const AGENT_STYLES: Record<string, string> = {
  sales: 'bg-success/15 text-success border-success/30',
  inventory: 'bg-warning/15 text-warning border-warning/30',
  support: 'bg-info/15 text-info border-info/30',
  marketing: 'bg-accent/15 text-accent border-accent/30',
  memory: 'bg-fg-muted/15 text-fg-muted border-fg-muted/30',
}

export function AgentBadges({ agents }: { agents: string[] }) {
  if (!agents.length) return null
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="text-[11px] font-medium uppercase tracking-wider text-fg-muted">
        Consulted
      </span>
      {agents.map((agent) => (
        <span
          key={agent}
          className={cn(
            'rounded-full border px-2 py-0.5 text-[11px] font-medium capitalize',
            AGENT_STYLES[agent] ?? 'bg-bg-muted text-fg-muted border-border',
          )}
        >
          {agent}
        </span>
      ))}
    </div>
  )
}
