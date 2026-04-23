import { AppLayout } from '@/components/layout/AppLayout'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { ChatContainer } from '@/components/chat/ChatContainer'
import { SessionList } from '@/components/chat/SessionList'
import { useChat } from '@/hooks/useChat'
import { useMetrics } from '@/hooks/useMetrics'
import { useSessions } from '@/hooks/useSessions'

export default function App() {
  const {
    sessions,
    activeSessionId,
    newSession,
    switchSession,
    deleteSession,
    notifySessionCreated,
    refresh: refreshSessions,
  } = useSessions()

  const {
    messages,
    pendingActions,
    isStreaming,
    isApproving,
    sendMessage,
    approveActions,
  } = useChat({ sessionId: activeSessionId, onSessionCreated: notifySessionCreated })

  const { metrics, isLoading, error, refresh: refreshMetrics } = useMetrics()

  return (
    <AppLayout
      sidebar={
        <>
          <SessionList
            sessions={sessions}
            activeSessionId={activeSessionId}
            onNew={newSession}
            onSwitch={switchSession}
            onDelete={deleteSession}
          />
          <div style={{ height: 1, background: 'var(--color-border)', margin: '12px 0' }} />
          <Sidebar metrics={metrics} isLoading={isLoading} error={error} />
        </>
      }
      onRefresh={() => { refreshSessions(); refreshMetrics() }}
      isStreaming={isStreaming}
    >
      <ChatContainer
        messages={messages}
        pendingActions={pendingActions}
        isStreaming={isStreaming}
        isApproving={isApproving}
        onSend={sendMessage}
        onApprove={approveActions}
      />
    </AppLayout>
  )
}
