import { Sparkles } from 'lucide-react'

interface EmptyStateProps {
  onPick: (text: string) => void
}

const PROMPTS = [
  'How did sales perform last week?',
  'Which products are out of stock?',
  'Show me high-priority support tickets.',
  'Are any marketing campaigns underperforming?',
]

export function EmptyState({ onPick }: EmptyStateProps) {
  return (
    <div className="mx-auto flex h-full max-w-2xl flex-col items-center justify-center px-6 text-center">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-accent/15 text-accent">
        <Sparkles className="h-6 w-6" />
      </div>
      <h2 className="mb-2 text-2xl font-semibold">How can I help today?</h2>
      <p className="mb-6 max-w-md text-sm text-fg-muted">
        Ask anything about sales, inventory, support tickets, or marketing
        campaigns. I&apos;ll consult the right specialist agents and propose
        actions you can approve.
      </p>
      <div className="grid w-full grid-cols-1 gap-2 sm:grid-cols-2">
        {PROMPTS.map((p) => (
          <button
            key={p}
            onClick={() => onPick(p)}
            className="rounded-lg border border-border bg-bg-elevated px-4 py-3 text-left text-sm transition hover:border-accent/60 hover:bg-bg-muted"
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  )
}
