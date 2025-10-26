import { useState, useEffect } from 'react'
import { MessageSquare, Send, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react'
import { sendSMS, getSMSHistory, SMSResponse } from '../services/api'

interface SMSMessage {
  sid: string
  to: string
  from: string
  message: string
  status: string
  timestamp: string
  direction: 'inbound' | 'outbound'
}

export default function SMSPanel() {
  const [to, setTo] = useState('')
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<SMSMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const loadMessages = async () => {
    setLoading(true)
    try {
      const data = await getSMSHistory(50)
      setMessages(data.messages || [])
    } catch (err: any) {
      console.error('Failed to load SMS history:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMessages()
  }, [])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!to.trim() || !message.trim()) {
      setError('Please enter both phone number and message')
      return
    }

    setError('')
    setSuccess('')
    setSending(true)

    try {
      const result: SMSResponse = await sendSMS({ to: to.trim(), message: message.trim() })
      setSuccess(`Message sent successfully to ${result.to}`)
      setTo('')
      setMessage('')

      // Reload messages to show the new one
      await loadMessages()
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to send SMS')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Send SMS Form */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 p-6">
        <div className="flex items-center space-x-2 mb-6">
          <Send className="text-blue-400" size={24} />
          <h2 className="text-xl font-bold text-white">Send SMS</h2>
        </div>

        <form onSubmit={handleSend} className="space-y-4">
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-slate-300 mb-2">
              Recipient Phone Number
            </label>
            <input
              type="tel"
              id="phone"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              placeholder="+1234567890"
              className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="message" className="block text-sm font-medium text-slate-300 mb-2">
              Message
            </label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Enter your message..."
              rows={6}
              maxLength={1600}
              className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            <p className="mt-2 text-xs text-slate-500">
              {message.length} / 1600 characters
            </p>
          </div>

          {error && (
            <div className="flex items-start space-x-2 p-4 bg-red-900/20 border border-red-800 rounded-lg">
              <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={18} />
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          {success && (
            <div className="flex items-start space-x-2 p-4 bg-green-900/20 border border-green-800 rounded-lg">
              <CheckCircle className="text-green-500 flex-shrink-0 mt-0.5" size={18} />
              <p className="text-green-400 text-sm">{success}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={sending || !to.trim() || !message.trim()}
            className="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors shadow-lg"
          >
            <Send size={20} />
            <span>{sending ? 'Sending...' : 'Send Message'}</span>
          </button>
        </form>
      </div>

      {/* SMS History */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <MessageSquare className="text-purple-400" size={24} />
            <h2 className="text-xl font-bold text-white">Message History</h2>
          </div>
          <button
            onClick={loadMessages}
            disabled={loading}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`text-slate-300 ${loading ? 'animate-spin' : ''}`} size={20} />
          </button>
        </div>

        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {messages.length === 0 && !loading && (
            <div className="text-center py-12">
              <MessageSquare className="mx-auto text-slate-600 mb-3" size={48} />
              <p className="text-slate-400">No messages yet</p>
            </div>
          )}

          {messages.map((msg) => (
            <div
              key={msg.sid}
              className={`p-4 rounded-lg border ${
                msg.direction === 'outbound'
                  ? 'bg-blue-900/20 border-blue-800 ml-8'
                  : 'bg-slate-900/30 border-slate-700 mr-8'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <p className="text-white font-medium text-sm">
                    {msg.direction === 'outbound' ? `To: ${msg.to}` : `From: ${msg.from}`}
                  </p>
                  <p className="text-slate-400 text-xs mt-1">
                    {new Date(msg.timestamp).toLocaleString()}
                  </p>
                </div>
                <span className={`px-2 py-1 text-xs rounded ${
                  msg.status === 'delivered' || msg.status === 'sent'
                    ? 'bg-green-900/30 text-green-400'
                    : msg.status === 'failed'
                    ? 'bg-red-900/30 text-red-400'
                    : 'bg-yellow-900/30 text-yellow-400'
                }`}>
                  {msg.status}
                </span>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed">{msg.message}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
