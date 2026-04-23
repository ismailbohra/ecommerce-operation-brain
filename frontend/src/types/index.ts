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
  progress?: AgentProgress
}

export interface AgentProgressItem {
  name: string
  status: 'running' | 'done'
}

export interface AgentProgress {
  stage: 'routing' | 'agents' | 'synthesizing' | 'checking_actions'
  agents: AgentProgressItem[]
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
  | { type: 'router_start' }
  | { type: 'router_done'; agents: string[] }
  | { type: 'agents_start'; agents: string[] }
  | { type: 'agent_start'; name: string }
  | { type: 'agent_done'; name: string }
  | { type: 'agents_done' }
  | { type: 'synthesis_start' }
  | { type: 'synthesis_done' }
  | { type: 'action_start' }
  | { type: 'action_done'; count: number }
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

// ------------------------------------------------------------------ //
// Sessions
// ------------------------------------------------------------------ //

export interface Session {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export interface SessionDetail extends Session {
  messages: SessionMessage[]
}

export interface SessionMessage {
  id: string
  role: Role
  content: string
  agents: string[]
  actions?: ProposedAction[] | null
  action_results?: string[] | null
  created_at: string
}
