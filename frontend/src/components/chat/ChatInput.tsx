import { Send, Loader2 } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

interface ChatInputProps {
  onSend: (text: string) => void
  disabled?: boolean
  isStreaming?: boolean
}

export function ChatInput({ onSend, disabled, isStreaming }: ChatInputProps) {
  const [value, setValue] = useState('')
  const ref = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 180) + 'px'
  }, [value])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        ref.current?.focus()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const submit = () => {
    if (!value.trim() || disabled) return
    onSend(value.trim())
    setValue('')
  }

  return (
    <div style={{ borderTop:'1px solid var(--color-border)', background:'var(--color-bg-elevated)', padding:'12px 16px', flexShrink:0 }}>
      <div style={{ maxWidth:760, margin:'0 auto', display:'flex', alignItems:'flex-end', gap:8, borderRadius:10, border:'1px solid var(--color-border)', background:'var(--color-bg-muted)', padding:'8px 10px' }}>
        <textarea
          ref={ref}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit() }
          }}
          rows={1}
          placeholder={disabled ? 'Approve actions above to continue…' : 'Ask about your business…'}
          disabled={disabled}
          style={{ flex:1, resize:'none', background:'transparent', border:'none', outline:'none', fontSize:14, lineHeight:1.55, color:'var(--color-fg)', padding:'2px 4px', fontFamily:'inherit', cursor: disabled ? 'not-allowed' : 'text', opacity: disabled ? 0.6 : 1 }}
        />
        <button
          onClick={submit}
          disabled={disabled || !value.trim()}
          style={{ width:34, height:34, borderRadius:7, border:'none', background:'var(--color-accent)', color:'white', display:'flex', alignItems:'center', justifyContent:'center', cursor: (disabled || !value.trim()) ? 'not-allowed' : 'pointer', opacity: (disabled || !value.trim()) ? 0.45 : 1, flexShrink:0, transition:'opacity 0.15s' }}
          aria-label="Send"
        >
          {isStreaming ? <Loader2 size={15} style={{ animation:'spin 1s linear infinite' }} /> : <Send size={15} />}
        </button>
      </div>
      <div style={{ maxWidth:760, margin:'4px auto 0', paddingLeft:4, fontSize:11, color:'var(--color-fg-muted)' }}>
        Enter to send · Shift+Enter for newline · ⌘K to focus
      </div>
    </div>
  )
}
