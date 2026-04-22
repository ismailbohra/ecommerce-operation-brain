import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Check, Copy, User, Bot, Info } from 'lucide-react'
import { useState } from 'react'
import type { ChatMessage } from '@/types'
import { AgentBadges } from './AgentBadges'

interface ChatMessageItemProps {
  message: ChatMessage
}

export function ChatMessageItem({ message }: ChatMessageItemProps) {
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch { /* ignore */ }
  }

  if (isSystem) {
    return (
      <div className="fade-in" style={{ display:'flex', alignItems:'flex-start', gap:8, borderRadius:8, border:'1px solid var(--color-border)', background:'var(--color-bg-muted)', padding:'10px 14px', fontSize:13 }}>
        <Info size={14} style={{ color:'var(--color-info)', flexShrink:0, marginTop:2 }} />
        <div style={{ flex:1 }}>
          <div style={{ fontWeight:500 }}>{message.content}</div>
          {message.actionResults && message.actionResults.length > 0 && (
            <ul style={{ marginTop:6, paddingLeft:0, listStyle:'none', display:'flex', flexDirection:'column', gap:3 }}>
              {message.actionResults.map((r: string, i: number) => (
                <li key={i} style={{ display:'flex', alignItems:'flex-start', gap:5, fontSize:12, color:'var(--color-fg-muted)' }}>
                  <Check size={11} style={{ color:'var(--color-success)', flexShrink:0, marginTop:2 }} />
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="fade-in" style={{ display:'flex', flexDirection: isUser ? 'row-reverse' : 'row', gap:10, alignItems:'flex-start' }}>
      {/* Avatar */}
      <div style={{ width:30, height:30, borderRadius:'50%', flexShrink:0, display:'flex', alignItems:'center', justifyContent:'center', background: isUser ? 'var(--color-accent)' : 'var(--color-bg-muted)', color: isUser ? 'white' : 'var(--color-fg-muted)' }}>
        {isUser ? <User size={14} /> : <Bot size={14} />}
      </div>

      {/* Bubble */}
      <div style={{ display:'flex', flexDirection:'column', gap:4, maxWidth:'70%', alignItems: isUser ? 'flex-end' : 'flex-start' }}>
        {!isUser && message.agents && message.agents.length > 0 && (
          <AgentBadges agents={message.agents} />
        )}
        <div
          style={{
            position:'relative',
            padding:'10px 14px',
            borderRadius: isUser ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
            fontSize:14,
            lineHeight:1.6,
            background: message.error
              ? 'oklch(0.52 0.22 25 / 0.1)'
              : isUser
                ? 'var(--color-accent)'
                : 'var(--color-bg-elevated)',
            color: message.error
              ? 'var(--color-danger)'
              : isUser
                ? 'white'
                : 'var(--color-fg)',
            border: isUser ? 'none' : `1px solid var(--color-border)`,
          }}
        >
          {isUser ? (
            <p style={{ margin:0, whiteSpace:'pre-wrap' }}>{message.content}</p>
          ) : (
            <div className={`markdown${message.isStreaming ? ' streaming-cursor' : ''}`}>
              {message.content ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              ) : message.isStreaming ? (
                <span style={{ color:'var(--color-fg-muted)' }}>Thinking…</span>
              ) : null}
            </div>
          )}

          {!isUser && !message.isStreaming && message.content && (
            <button
              onClick={handleCopy}
              title="Copy"
              style={{ position:'absolute', bottom:-10, right:8, width:22, height:22, borderRadius:5, border:'1px solid var(--color-border)', background:'var(--color-bg-elevated)', display:'flex', alignItems:'center', justifyContent:'center', cursor:'pointer', opacity:0, transition:'opacity 0.15s', color:'var(--color-fg-muted)' }}
              onMouseEnter={e => (e.currentTarget.style.opacity = '1')}
              onMouseLeave={e => (e.currentTarget.style.opacity = '0')}
            >
              {copied ? <Check size={11} /> : <Copy size={11} />}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
