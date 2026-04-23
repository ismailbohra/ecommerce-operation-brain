import { useCallback, useEffect, useState } from 'react'
import { v4 as uuid } from 'uuid'
import { toast } from 'sonner'
import {
  getSessions,
  deleteSession as apiDeleteSession,
  renameSession as apiRenameSession,
} from '@/lib/api'
import type { Session } from '@/types'

export function useSessions() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [activeSessionId, setActiveSessionId] = useState<string>(() => uuid())
  const [isLoading, setIsLoading] = useState(false)

  const refresh = useCallback(async () => {
    try {
      setIsLoading(true)
      const data = await getSessions()
      setSessions(data)
      // If the active session no longer exists in the list keep the current id
      // (it may not have been saved yet — session is created on first message).
    } catch {
      // Silently ignore — backend may not be ready yet.
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Load sessions on mount.
  useEffect(() => {
    refresh()
  }, [refresh])

  const newSession = useCallback(() => {
    setActiveSessionId(uuid())
  }, [])

  const switchSession = useCallback(
    (id: string) => {
      setActiveSessionId(id)
    },
    [],
  )

  const deleteSession = useCallback(
    async (id: string) => {
      try {
        await apiDeleteSession(id)
        setSessions((prev) => prev.filter((s) => s.id !== id))
        // If we deleted the active session, start a new one.
        if (id === activeSessionId) {
          setActiveSessionId(uuid())
        }
      } catch {
        toast.error('Failed to delete conversation')
      }
    },
    [activeSessionId],
  )

  const renameSession = useCallback(async (id: string, title: string) => {
    try {
      const updated = await apiRenameSession(id, title)
      setSessions((prev) => prev.map((s) => (s.id === id ? updated : s)))
    } catch {
      toast.error('Failed to rename conversation')
    }
  }, [])

  // Refresh session list after a new message is sent (so the new session
  // appears in the sidebar). Called by useChat after first send.
  const notifySessionCreated = useCallback(() => {
    refresh()
  }, [refresh])

  return {
    sessions,
    activeSessionId,
    isLoading,
    newSession,
    switchSession,
    deleteSession,
    renameSession,
    refresh,
    notifySessionCreated,
  }
}
