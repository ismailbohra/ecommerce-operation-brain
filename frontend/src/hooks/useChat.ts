import { useCallback, useEffect, useRef, useState } from 'react'
import { v4 as uuid } from 'uuid'
import { toast } from 'sonner'
import {
  approveActions as apiApproveActions,
  getSession,
  streamMessage,
} from '@/lib/api'
import type { ChatHistoryItem, ChatMessage, ProposedAction } from '@/types'

interface UseChatOptions {
  sessionId: string
  onSessionCreated?: () => void
}

export function useChat({ sessionId, onSessionCreated }: UseChatOptions) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [pendingActions, setPendingActions] = useState<ProposedAction[] | null>(null)
  const [isStreaming, setIsStreaming] = useState(false)
  const [isApproving, setIsApproving] = useState(false)
  const notifiedRef = useRef<string | null>(null)

  useEffect(() => {
    setMessages([])
    setPendingActions(null)
    if (!sessionId) return
    let cancelled = false
    getSession(sessionId)
      .then((detail) => {
        if (cancelled) return
        const loaded: ChatMessage[] = detail.messages.map((m) => ({
          id: m.id,
          role: m.role as ChatMessage['role'],
          content: m.content,
          agents: m.agents ?? [],
          actions: (m.actions as ProposedAction[] | undefined) ?? undefined,
          actionResults: m.action_results ?? undefined,
        }))
        setMessages(loaded)
      })
      .catch(() => {
        // Session does not exist yet -- fine, created on first message.
      })
    return () => { cancelled = true }
  }, [sessionId])

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

      const userMsg: ChatMessage = { id: uuid(), role: 'user', content: trimmed }
      const assistantMsg: ChatMessage = { id: uuid(), role: 'assistant', content: '', isStreaming: true }

      const history = buildHistory(messages)
      setMessages((prev) => [...prev, userMsg, assistantMsg])
      setIsStreaming(true)
      setPendingActions(null)

      try {
        await streamMessage(
          trimmed,
          sessionId,
          history,
          (event: import('@/types').StreamEvent) => {
            setMessages((prev) => {
              const next = [...prev]
              const idx = next.findIndex((m) => m.id === assistantMsg.id)
              if (idx === -1) return prev
              const target = { ...next[idx] }

              switch (event.type) {
                case 'router_start':
                  target.progress = { stage: 'routing', agents: [] }
                  break
                case 'router_done':
                  target.progress = {
                    stage: 'agents',
                    agents: event.agents.map((name) => ({ name, status: 'running' as const })),
                  }
                  break
                case 'agents_start':
                  target.progress = {
                    stage: 'agents',
                    agents: event.agents.map((name) => ({ name, status: 'running' as const })),
                  }
                  break
                case 'agent_start': {
                  const prev_agents = target.progress?.agents ?? []
                  const exists = prev_agents.some((a) => a.name === event.name)
                  target.progress = {
                    stage: 'agents',
                    agents: exists
                      ? prev_agents.map((a) => a.name === event.name ? { ...a, status: 'running' as const } : a)
                      : [...prev_agents, { name: event.name, status: 'running' as const }],
                  }
                  break
                }
                case 'agent_done': {
                  const prev_agents = target.progress?.agents ?? []
                  target.progress = {
                    stage: 'agents',
                    agents: prev_agents.map((a) =>
                      a.name === event.name ? { ...a, status: 'done' as const } : a
                    ),
                  }
                  break
                }
                case 'agents_done':
                  if (target.progress) target.progress = { ...target.progress, stage: 'synthesizing' }
                  break
                case 'synthesis_start':
                  target.progress = { stage: 'synthesizing', agents: target.progress?.agents ?? [] }
                  break
                case 'synthesis_done':
                  if (target.progress) target.progress = { ...target.progress, stage: 'checking_actions' }
                  break
                case 'action_start':
                  target.progress = { stage: 'checking_actions', agents: target.progress?.agents ?? [] }
                  break
                case 'action_done':
                  // keep progress until first token arrives
                  break
                case 'agents':
                  target.agents = event.agents
                  break
                case 'token':
                  target.content = (target.content || '') + event.text
                  target.progress = undefined // clear progress once text starts arriving
                  break
                case 'actions':
                  target.actions = event.actions
                  setPendingActions(event.actions)
                  break
                case 'done':
                  target.isStreaming = false
                  target.progress = undefined
                  if (event.response) target.content = event.response
                  if (event.agents_consulted?.length) target.agents = event.agents_consulted
                  break
                case 'error':
                  target.isStreaming = false
                  target.progress = undefined
                  target.error = true
                  target.content = `Error: ${event.message}`
                  toast.error(event.message)
                  break
              }
              next[idx] = target
              return next
            })

            if (event.type === 'done' && notifiedRef.current !== sessionId) {
              notifiedRef.current = sessionId
              onSessionCreated?.()
            }
          },
        )
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
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantMsg.id ? { ...m, isStreaming: false } : m)),
        )
      }
    },
    [buildHistory, isStreaming, messages, sessionId, onSessionCreated],
  )

  const approveActions = useCallback(
    async (approvedIds: string[]) => {
      if (isApproving) return
      setIsApproving(true)
      try {
        if (approvedIds.length === 0) {
          setMessages((prev) => [
            ...prev,
            { id: uuid(), role: 'system', content: 'All proposed actions were rejected.' },
          ])
        } else {
          const { action_results } = await apiApproveActions(sessionId, approvedIds)
          setMessages((prev) => [
            ...prev,
            { id: uuid(), role: 'system', content: 'Executed actions', actionResults: action_results },
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
    [isApproving, sessionId],
  )

  return {
    messages,
    pendingActions,
    isStreaming,
    isApproving,
    sendMessage,
    approveActions,
  }
}
