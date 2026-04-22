import { useCallback, useEffect, useRef, useState } from 'react'
import { v4 as uuid } from 'uuid'
import { toast } from 'sonner'
import {
  approveActions as apiApproveActions,
  streamMessage,
} from '@/lib/api'
import type { ChatHistoryItem, ChatMessage, ProposedAction } from '@/types'

const STORAGE_KEY = 'ecomx.chat.v1'

interface PersistedState {
  threadId: string
  messages: ChatMessage[]
}

function loadPersisted(): PersistedState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw) as PersistedState
  } catch { /* ignore */ }
  return { threadId: uuid(), messages: [] }
}

export function useChat() {
  const initial = useRef(loadPersisted())
  const [threadId, setThreadId] = useState(initial.current.threadId)
  const [messages, setMessages] = useState<ChatMessage[]>(initial.current.messages)
  const [pendingActions, setPendingActions] = useState<ProposedAction[] | null>(null)
  const [isStreaming, setIsStreaming] = useState(false)
  const [isApproving, setIsApproving] = useState(false)

  // Persist
  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ threadId, messages }),
      )
    } catch { /* ignore */ }
  }, [threadId, messages])

  const buildHistory = useCallback(
    (msgs: ChatMessage[]): ChatHistoryItem[] =>
      msgs
        .filter((m) => m.role !== 'system' && !m.error)
        .map((m) => ({ role: m.role, content: m.content, agents: m.agents })),
    [],
  )

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim()
      if (!trimmed || isStreaming) return

      const userMsg: ChatMessage = {
        id: uuid(),
        role: 'user',
        content: trimmed,
      }
      const assistantMsg: ChatMessage = {
        id: uuid(),
        role: 'assistant',
        content: '',
        isStreaming: true,
      }

      // Snapshot history BEFORE adding the new user message.
      const history = buildHistory(messages)

      setMessages((prev) => [...prev, userMsg, assistantMsg])
      setIsStreaming(true)
      setPendingActions(null)

      try {
        await streamMessage(trimmed, threadId, history, (event: import('@/types').StreamEvent) => {
          setMessages((prev) => {
            const next = [...prev]
            const idx = next.findIndex((m) => m.id === assistantMsg.id)
            if (idx === -1) return prev
            const target = { ...next[idx] }

            switch (event.type) {
              case 'agents':
                target.agents = event.agents
                break
              case 'token':
                target.content = (target.content || '') + event.text
                break
              case 'actions':
                target.actions = event.actions
                setPendingActions(event.actions)
                break
              case 'done':
                target.isStreaming = false
                // Always use the authoritative full response from done event
                // (guards against token accumulation failures)
                if (event.response) target.content = event.response
                if (event.agents_consulted?.length) target.agents = event.agents_consulted
                break
              case 'error':
                target.isStreaming = false
                target.error = true
                target.content = `Error: ${event.message}`
                toast.error(event.message)
                break
            }
            next[idx] = target
            return next
          })
        })
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error'
        toast.error(message)
        setMessages((prev) => {
          const next = [...prev]
          const idx = next.findIndex((m) => m.id === assistantMsg.id)
          if (idx !== -1) {
            next[idx] = {
              ...next[idx],
              isStreaming: false,
              error: true,
              content: next[idx].content || `Error: ${message}`,
            }
          }
          return next
        })
      } finally {
        setIsStreaming(false)
        setMessages((prev) => {
          // Final safety: clear isStreaming flag.
          return prev.map((m) =>
            m.id === assistantMsg.id ? { ...m, isStreaming: false } : m,
          )
        })
      }
    },
    [buildHistory, isStreaming, messages, threadId],
  )

  const approveActions = useCallback(
    async (approvedIds: string[]) => {
      if (isApproving) return
      setIsApproving(true)
      try {
        if (approvedIds.length === 0) {
          setMessages((prev) => [
            ...prev,
            {
              id: uuid(),
              role: 'system',
              content: 'All proposed actions were rejected.',
            },
          ])
        } else {
          const { action_results } = await apiApproveActions(threadId, approvedIds)
          setMessages((prev) => [
            ...prev,
            {
              id: uuid(),
              role: 'system',
              content: 'Executed actions',
              actionResults: action_results,
            },
          ])
          toast.success(`Executed ${approvedIds.length} action(s)`)
        }
        setPendingActions(null)
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unknown error'
        toast.error(message)
      } finally {
        setIsApproving(false)
      }
    },
    [isApproving, threadId],
  )

  const clearChat = useCallback(() => {
    const newId = uuid()
    setThreadId(newId)
    setMessages([])
    setPendingActions(null)
  }, [])

  return {
    threadId,
    messages,
    pendingActions,
    isStreaming,
    isApproving,
    sendMessage,
    approveActions,
    clearChat,
  }
}
