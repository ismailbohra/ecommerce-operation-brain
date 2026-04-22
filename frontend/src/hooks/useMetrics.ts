import { useCallback, useEffect, useRef, useState } from 'react'
import { fetchMetrics } from '@/lib/api'
import type { DashboardMetrics } from '@/types'

const POLL_INTERVAL = 60_000

export function useMetrics() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const timer = useRef<number | null>(null)

  const refresh = useCallback(async () => {
    try {
      setError(null)
      const data = await fetchMetrics()
      setMetrics(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load metrics')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
    timer.current = window.setInterval(refresh, POLL_INTERVAL)
    return () => {
      if (timer.current) window.clearInterval(timer.current)
    }
  }, [refresh])

  return { metrics, isLoading, error, refresh }
}
