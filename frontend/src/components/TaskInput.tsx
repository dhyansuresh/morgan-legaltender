import { useState } from 'react'
import { Send, AlertCircle } from 'lucide-react'
import { routeTask, TaskRouteResponse } from '../services/api'

interface TaskInputProps {
  onResult: (result: TaskRouteResponse) => void
  onLoadingChange: (loading: boolean) => void
}

export default function TaskInput({ onResult, onLoadingChange }: TaskInputProps) {
  const [text, setText] = useState('')
  const [priority, setPriority] = useState(5)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!text.trim()) {
      setError('Please enter some text')
      return
    }

    setError('')
    onLoadingChange(true)

    try {
      const result = await routeTask({
        text: text.trim(),
        priority,
      })
      onResult(result)
      setText('')
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to process request. Please try again.')
    } finally {
      onLoadingChange(false)
    }
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white mb-2">Submit Legal Task</h2>
        <p className="text-slate-400">
          Enter any legal information, client message, or task. Our AI will automatically route it to the appropriate specialist.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Text Input */}
        <div>
          <label htmlFor="task-text" className="block text-sm font-medium text-slate-300 mb-2">
            Task Description
          </label>
          <textarea
            id="task-text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Example: I need case law about negligence in car accidents from the past 5 years..."
            rows={8}
            className="w-full px-4 py-3 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />
          <p className="mt-2 text-xs text-slate-500">
            {text.length} characters
          </p>
        </div>

        {/* Priority Selector */}
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-slate-300 mb-2">
            Priority Level: {priority}
          </label>
          <input
            type="range"
            id="priority"
            min="1"
            max="10"
            value={priority}
            onChange={(e) => setPriority(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>Low (1)</span>
            <span>Medium (5)</span>
            <span>High (10)</span>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="flex items-start space-x-2 p-4 bg-red-900/20 border border-red-800 rounded-lg">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={18} />
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!text.trim()}
          className="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors shadow-lg"
        >
          <Send size={20} />
          <span>Process Task</span>
        </button>
      </form>
    </div>
  )
}
