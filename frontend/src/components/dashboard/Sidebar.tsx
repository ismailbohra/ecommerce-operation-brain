import {
  AlertTriangle,
  DollarSign,
  Megaphone,
  Package,
  ShoppingCart,
  Ticket,
  TrendingUp,
  Wallet,
} from 'lucide-react'
import { MetricCard } from './MetricCard'
import { formatCurrency, formatNumber } from '@/lib/utils'
import type { DashboardMetrics } from '@/types'

interface SidebarProps {
  metrics: DashboardMetrics | null
  isLoading: boolean
  error: string | null
}

export function Sidebar({ metrics, isLoading, error }: SidebarProps) {
  return (
    <div className="space-y-5">
      <Section title="Sales (7d)">
        <MetricCard
          icon={DollarSign}
          label="Revenue"
          value={metrics ? formatCurrency(metrics.sales.revenue) : ''}
          tone="success"
          loading={isLoading}
        />
        <MetricCard
          icon={ShoppingCart}
          label="Orders"
          value={metrics ? formatNumber(metrics.sales.orders) : ''}
          loading={isLoading}
        />
      </Section>

      <Section title="Inventory">
        <MetricCard
          icon={AlertTriangle}
          label="Out of stock"
          value={metrics ? formatNumber(metrics.inventory.out_of_stock) : ''}
          tone={metrics && metrics.inventory.out_of_stock > 0 ? 'danger' : 'default'}
          loading={isLoading}
        />
        <MetricCard
          icon={Package}
          label="Low stock"
          value={metrics ? formatNumber(metrics.inventory.low_stock) : ''}
          tone={metrics && metrics.inventory.low_stock > 0 ? 'warning' : 'default'}
          loading={isLoading}
        />
      </Section>

      <Section title="Support">
        <MetricCard
          icon={Ticket}
          label="Open tickets"
          value={metrics ? formatNumber(metrics.support.open_tickets) : ''}
          loading={isLoading}
        />
        <MetricCard
          icon={AlertTriangle}
          label="High priority"
          value={metrics ? formatNumber(metrics.support.high_priority) : ''}
          tone={metrics && metrics.support.high_priority > 0 ? 'danger' : 'default'}
          loading={isLoading}
        />
      </Section>

      <Section title="Marketing">
        <MetricCard
          icon={Megaphone}
          label="Campaigns"
          value={metrics ? formatNumber(metrics.marketing.campaigns) : ''}
          tone="info"
          loading={isLoading}
        />
        <MetricCard
          icon={Wallet}
          label="Ad spend"
          value={metrics ? formatCurrency(metrics.marketing.ad_spend) : ''}
          loading={isLoading}
        />
      </Section>

      {error && (
        <div className="rounded-md border border-danger/40 bg-danger/10 px-3 py-2 text-xs text-danger">
          {error}
        </div>
      )}

      <div className="flex items-center gap-1.5 px-1 text-[11px] text-fg-muted">
        <TrendingUp className="h-3 w-3" />
        Auto-refreshes every 60s
      </div>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="mb-2 px-1 text-[11px] font-semibold uppercase tracking-wider text-fg-muted">
        {title}
      </h2>
      <div className="grid grid-cols-2 gap-2">{children}</div>
    </div>
  )
}
