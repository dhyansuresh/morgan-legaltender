import { useState, useEffect } from 'react'
import { Mail, RefreshCw, Inbox, AlertCircle } from 'lucide-react'
import { getEmails } from '../services/api'

interface Email {
  id: string
  subject: string
  from: string
  body: string
  received_at: string
  processed: boolean
  task_id?: string
}

export default function EmailPanel() {
  const [emails, setEmails] = useState<Email[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null)

  const loadEmails = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await getEmails(50)
      setEmails(data.emails || [])
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load emails')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadEmails()
  }, [])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Email List */}
      <div className="lg:col-span-1 bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <Inbox className="text-blue-400" size={24} />
            <h2 className="text-xl font-bold text-white">Inbox</h2>
          </div>
          <button
            onClick={loadEmails}
            disabled={loading}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`text-slate-300 ${loading ? 'animate-spin' : ''}`} size={20} />
          </button>
        </div>

        {error && (
          <div className="flex items-start space-x-2 p-4 bg-red-900/20 border border-red-800 rounded-lg mb-4">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={18} />
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        <div className="space-y-2 max-h-[600px] overflow-y-auto">
          {emails.length === 0 && !loading && (
            <div className="text-center py-12">
              <Mail className="mx-auto text-slate-600 mb-3" size={48} />
              <p className="text-slate-400">No emails yet</p>
              <p className="text-slate-500 text-sm mt-1">
                Configure email forwarding to see messages here
              </p>
            </div>
          )}

          {emails.map((email) => (
            <div
              key={email.id}
              onClick={() => setSelectedEmail(email)}
              className={`p-4 rounded-lg cursor-pointer transition-colors border ${
                selectedEmail?.id === email.id
                  ? 'bg-blue-900/30 border-blue-700'
                  : 'bg-slate-900/30 border-slate-700 hover:bg-slate-900/50'
              }`}
            >
              <div className="flex items-start justify-between mb-1">
                <span className="font-semibold text-white text-sm truncate flex-1">
                  {email.subject}
                </span>
                {email.processed && (
                  <span className="ml-2 px-2 py-0.5 bg-green-900/30 text-green-400 text-xs rounded">
                    Processed
                  </span>
                )}
              </div>
              <p className="text-slate-400 text-xs mb-1">{email.from}</p>
              <p className="text-slate-500 text-xs">
                {new Date(email.received_at).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Email Detail */}
      <div className="lg:col-span-2 bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 p-6">
        {selectedEmail ? (
          <div>
            <div className="mb-6 pb-6 border-b border-slate-700">
              <h2 className="text-2xl font-bold text-white mb-2">{selectedEmail.subject}</h2>
              <div className="flex items-center justify-between text-sm text-slate-400">
                <span>From: {selectedEmail.from}</span>
                <span>{new Date(selectedEmail.received_at).toLocaleString()}</span>
              </div>
            </div>

            <div className="bg-slate-900/50 p-6 rounded-lg border border-slate-700">
              <p className="text-slate-300 whitespace-pre-wrap leading-relaxed">
                {selectedEmail.body}
              </p>
            </div>

            {selectedEmail.task_id && (
              <div className="mt-4 p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
                <p className="text-blue-400 text-sm">
                  This email has been processed. Task ID: {selectedEmail.task_id}
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Mail className="mx-auto text-slate-600 mb-3" size={64} />
              <p className="text-slate-400">Select an email to view details</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
