import { useState } from 'react'
import { Check, X, ChevronDown, ChevronRight, ShieldAlert } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { ProposedAction } from '@/types'

const TYPE_STYLES: Record<string, string> = {
  restock: 'bg-info/15 text-info border-info/40',
  pause_campaign: 'bg-warning/15 text-warning border-warning/40',
  discount: 'bg-accent/15 text-accent border-accent/40',
  create_ticket: 'bg-success/15 text-success border-success/40',
  resolve_ticket: 'bg-fg-muted/15 text-fg-muted border-fg-muted/40',
}

interface ActionApprovalProps {
  actions: ProposedAction[]
  onSubmit: (approvedIds: string[]) => void
  isSubmitting: boolean
}

export function ActionApproval({ actions, onSubmit, isSubmitting }: ActionApprovalProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  const toggle = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const toggleExpand = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  return (
    <div className="fade-in mx-auto max-w-3xl rounded-xl border border-warning/40 bg-warning/5 p-4">
      <div className="mb-3 flex items-center gap-2">
        <ShieldAlert className="h-4 w-4 text-warning" />
        <h3 className="text-sm font-semibold">Approve actions</h3>
        <span className="ml-auto text-xs text-fg-muted">
          {selected.size} of {actions.length} selected
        </span>
      </div>

      <div className="space-y-2">
        {actions.map((action) => {
          const isSelected = selected.has(action.id)
          const isExpanded = expanded.has(action.id)
          return (
            <div
              key={action.id}
              className={cn(
                'rounded-lg border bg-bg-elevated p-3 transition',
                isSelected ? 'border-accent/60' : 'border-border',
              )}
            >
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => toggle(action.id)}
                  className="mt-1 h-4 w-4 shrink-0 cursor-pointer accent-[oklch(0.72_0.18_260)]"
                />
                <div className="flex-1">
                  <div className="mb-1 flex items-center gap-2">
                    <span
                      className={cn(
                        'rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider',
                        TYPE_STYLES[action.type] ??
                          'bg-bg-muted text-fg-muted border-border',
                      )}
                    >
                      {action.type.replace('_', ' ')}
                    </span>
                    <span className="text-sm font-medium">{action.description}</span>
                  </div>
                  {action.reason && (
                    <p className="text-xs text-fg-muted">{action.reason}</p>
                  )}
                  {Object.keys(action.params).length > 0 && (
                    <button
                      onClick={() => toggleExpand(action.id)}
                      className="mt-1.5 inline-flex items-center gap-1 text-[11px] text-fg-muted hover:text-fg"
                    >
                      {isExpanded ? (
                        <ChevronDown className="h-3 w-3" />
                      ) : (
                        <ChevronRight className="h-3 w-3" />
                      )}
                      Parameters
                    </button>
                  )}
                  {isExpanded && (
                    <pre className="mt-1.5 overflow-x-auto rounded-md bg-bg-muted p-2 text-[11px] text-fg-muted">
                      {JSON.stringify(action.params, null, 2)}
                    </pre>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-4 flex items-center justify-end gap-2">
        <button
          onClick={() => onSubmit([])}
          disabled={isSubmitting}
          className="inline-flex items-center gap-1.5 rounded-md border border-border bg-bg-muted px-3 py-2 text-sm font-medium transition hover:bg-border/60 disabled:opacity-50"
        >
          <X className="h-4 w-4" /> Reject all
        </button>
        <button
          onClick={() => onSubmit(Array.from(selected))}
          disabled={isSubmitting || selected.size === 0}
          className="inline-flex items-center gap-1.5 rounded-md bg-accent px-3 py-2 text-sm font-medium text-accent-fg transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Check className="h-4 w-4" />
          Execute selected ({selected.size})
        </button>
      </div>
    </div>
  )
}
