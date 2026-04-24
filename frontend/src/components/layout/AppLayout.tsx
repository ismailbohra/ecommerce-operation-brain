import { RefreshCw } from 'lucide-react'
import type { ReactNode } from 'react'

interface AppLayoutProps {
  sidebar: ReactNode
  children: ReactNode
  onRefresh: () => void
  isStreaming: boolean
}

export function AppLayout({
  sidebar,
  children,
  onRefresh,
  isStreaming,
}: AppLayoutProps) {
  return (
    <div style={{ display:'flex', height:'100%', width:'100%', overflow:'hidden', background:'var(--color-bg)', color:'var(--color-fg)' }}>
      {/* Sidebar */}
      <aside style={{ width:300, flexShrink:0, display:'flex', flexDirection:'column', borderRight:'1px solid var(--color-border)', background:'var(--color-bg-elevated)', overflow:'hidden' }}>
        <div style={{ display:'flex', alignItems:'center', gap:10, padding:'14px 16px', borderBottom:'1px solid var(--color-border)' }}>
          <div style={{ width:36, height:36, borderRadius:8, background:'oklch(0.55 0.22 270 / 0.12)', color:'var(--color-accent)', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="m9 12 2 2 4-4"/></svg>
          </div>
          <div>
            <div style={{ fontWeight:600, fontSize:14, lineHeight:1.2 }}>Ecom</div>
            <div style={{ fontSize:11, color:'var(--color-fg-muted)', lineHeight:1.2 }}>AI operations agent</div>
          </div>
          <button
            onClick={onRefresh}
            title="Refresh"
            style={{ marginLeft:'auto', background:'none', border:'none', cursor:'pointer', color:'var(--color-fg-muted)', padding:4, borderRadius:4, display:'flex', alignItems:'center' }}
          >
            <RefreshCw size={14} />
          </button>
        </div>
        <div style={{ flex:1, overflowY:'auto', padding:'12px 14px' }}>{sidebar}</div>
      </aside>

      {/* Main */}
      <main style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden', minWidth:0 }}>
        <header style={{ height:52, display:'flex', alignItems:'center', justifyContent:'space-between', borderBottom:'1px solid var(--color-border)', padding:'0 20px', background:'var(--color-bg-elevated)', flexShrink:0 }}>
          <div style={{ display:'flex', alignItems:'center', gap:8 }}>
            <span style={{ fontWeight:600, fontSize:14 }}>Conversation</span>
            {isStreaming && (
              <span style={{ display:'inline-flex', alignItems:'center', gap:5, borderRadius:20, background:'oklch(0.55 0.22 270 / 0.1)', padding:'2px 9px', fontSize:11, fontWeight:500, color:'var(--color-accent)' }}>
                <span style={{ width:6, height:6, borderRadius:'50%', background:'var(--color-accent)', animation:'pulse 1.5s ease-in-out infinite' }} />
                Thinking
              </span>
            )}
          </div>
          <div style={{ fontSize:11, color:'var(--color-fg-muted)' }}>Multi-agent · LangGraph</div>
        </header>
        <div style={{ flex:1, overflow:'hidden', minHeight:0 }}>{children}</div>
      </main>
    </div>
  )
}
