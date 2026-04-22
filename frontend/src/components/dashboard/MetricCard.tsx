import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface MetricCardProps {
  icon: LucideIcon
  label: string
  value: string
  tone?: 'default' | 'danger' | 'warning' | 'success' | 'info'
  loading?: boolean
}

const toneClasses: Record<NonNullable<MetricCardProps['tone']>, string> = {
  default: 'text-fg',
  danger: 'text-danger',
  warning: 'text-warning',
  success: 'text-success',
  info: 'text-info',
}

export function MetricCard({
  icon: Icon,
  label,
  value,
  tone = 'default',
  loading = false,
}: MetricCardProps) {
  return (
    <div className="rounded-lg border border-border bg-bg-muted/50 p-3 transition hover:border-fg-muted/40">
      <div className="mb-1 flex items-center gap-1.5 text-xs text-fg-muted">
        <Icon className="h-3.5 w-3.5" />
        <span>{label}</span>
      </div>
      {loading ? (
        <div className="h-6 w-16 animate-pulse rounded bg-border/60" />
      ) : (
        <div className={cn('text-xl font-semibold tabular-nums', toneClasses[tone])}>
          {value}
        </div>
      )}
    </div>
  )
}
