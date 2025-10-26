import { useState } from 'react'
import { Send, Mail, MessageSquare, BarChart3, Loader2 } from 'lucide-react'
import TaskInput from './components/TaskInput'
import ResultDisplay from './components/ResultDisplay'
import EmailPanel from './components/EmailPanel'
import SMSPanel from './components/SMSPanel'
import AgentStatus from './components/AgentStatus'
import { TaskRouteResponse } from './services/api'

type TabType = 'task' | 'email' | 'sms' | 'stats'

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('task')
  const [result, setResult] = useState<TaskRouteResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">ParaLogic</h1>
              <p className="text-slate-300 mt-1">AI-Powered Legal Assistant</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-slate-300">System Online</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 mt-6">
        <div className="flex space-x-2 bg-slate-800/30 backdrop-blur-sm p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('task')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg transition-all ${
              activeTab === 'task'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Send size={18} />
            <span>Task Assistant</span>
          </button>
          <button
            onClick={() => setActiveTab('email')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg transition-all ${
              activeTab === 'email'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Mail size={18} />
            <span>Email Inbox</span>
          </button>
          <button
            onClick={() => setActiveTab('sms')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg transition-all ${
              activeTab === 'sms'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <MessageSquare size={18} />
            <span>SMS</span>
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg transition-all ${
              activeTab === 'stats'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <BarChart3 size={18} />
            <span>Agent Status</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'task' && (
          <div className="space-y-6">
            <TaskInput
              onResult={setResult}
              onLoadingChange={setIsLoading}
            />
            {isLoading && (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="animate-spin text-blue-500" size={48} />
                <span className="ml-4 text-slate-300 text-lg">Processing your request...</span>
              </div>
            )}
            {!isLoading && result && (
              <ResultDisplay result={result} />
            )}
          </div>
        )}

        {activeTab === 'email' && (
          <EmailPanel />
        )}

        {activeTab === 'sms' && (
          <SMSPanel />
        )}

        {activeTab === 'stats' && (
          <AgentStatus />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 pb-8 text-center text-slate-400 text-sm">
        <p>Morgan Legal Tender &copy; 2025 | AI-Powered Legal Case Management</p>
      </footer>
    </div>
  )
}

export default App
