import { AppLayout } from '@/components/layout/AppLayout'
import { Sidebar } from '@/components/dashboard/Sidebar'
import { ChatContainer } from '@/components/chat/ChatContainer'
import { useChat } from '@/hooks/useChat'
import { useMetrics } from '@/hooks/useMetrics'

export default function App() {
  const {
    messages,
    pendingActions,
    isStreaming,
    isApproving,
    sendMessage,
    approveActions,
    clearChat,
  } = useChat()
  const { metrics, isLoading, error, refresh } = useMetrics()

  return (
    <AppLayout
      sidebar={<Sidebar metrics={metrics} isLoading={isLoading} error={error} />}
      onNewChat={clearChat}
      onRefresh={refresh}
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