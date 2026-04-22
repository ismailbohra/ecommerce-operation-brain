export type AgentName = 'sales' | 'inventory' | 'support' | 'marketing' | 'memory'

export type Role = 'user' | 'assistant' | 'system'

export interface ProposedAction {
  id: string
  type: string
  description: string
  reason: string
  params: Record<string, unknown>
}

export interface ChatMessage {
  id: string
  role: Role
  content: string
  agents?: string[]
  actions?: ProposedAction[]
  actionResults?: string[]
  isStreaming?: boolean
  error?: boolean
}

export interface SalesMetrics {
  revenue: number
  orders: number
}
export interface InventoryMetrics {
  out_of_stock: number
  low_stock: number
}
export interface SupportMetrics {
  open_tickets: number
  high_priority: number
}
export interface MarketingMetrics {
  campaigns: number
  ad_spend: number
}
export interface DashboardMetrics {
  sales: SalesMetrics
  inventory: InventoryMetrics
  support: SupportMetrics
  marketing: MarketingMetrics
}

export type StreamEvent =
  | { type: 'status'; stage: string }
  | { type: 'agents'; agents: string[] }
  | { type: 'token'; text: string }
  | { type: 'actions'; actions: ProposedAction[] }
  | { type: 'done'; thread_id: string; agents_consulted: string[]; response: string }
  | { type: 'error'; message: string }

export interface ChatHistoryItem {
  role: Role
  content: string
  agents?: string[]
}
