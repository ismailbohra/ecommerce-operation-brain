import { useEffect, useRef } from 'react'
import { ChatMessageItem } from './ChatMessage'
import { ChatInput } from './ChatInput'
import { EmptyState } from './EmptyState'
import { ActionApproval } from '@/components/actions/ActionApproval'
import type { ChatMessage, ProposedAction } from '@/types'

interface ChatContainerProps {
  messages: ChatMessage[]
  pendingActions: ProposedAction[] | null
  isStreaming: boolean
  isApproving: boolean
  onSend: (text: string) => void
  onApprove: (ids: string[]) => void
}

export function ChatContainer({
  messages,
  pendingActions,
  isStreaming,
  isApproving,
  onSend,
  onApprove,
}: ChatContainerProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages or tokens arrive
  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [messages, pendingActions])

  const isEmpty = messages.length === 0

  return (
    <div style={{ display:'flex', flexDirection:'column', height:'100%', overflow:'hidden' }}>
      <div ref={scrollRef} style={{ flex:1, overflowY:'auto', minHeight:0 }}>
        {isEmpty ? (
          <EmptyState onPick={(t) => onSend(t)} />
        ) : (
          <div style={{ maxWidth:760, margin:'0 auto', display:'flex', flexDirection:'column', gap:20, padding:'24px 16px' }}>
            {messages.map((m) => (
              <ChatMessageItem key={m.id} message={m} />
            ))}
            {pendingActions && pendingActions.length > 0 && (
              <ActionApproval
                actions={pendingActions}
                onSubmit={onApprove}
                isSubmitting={isApproving}
              />
            )}
          </div>
        )}
      </div>
      <ChatInput
        onSend={onSend}
        disabled={isStreaming || !!pendingActions}
        isStreaming={isStreaming}
      />
    </div>
  )
}
