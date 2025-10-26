import { useState, useEffect } from 'react'
import { Activity, RefreshCw, Users, TrendingUp, AlertCircle } from 'lucide-react'
import { getAgentStatus, getRoutingStats } from '../services/api'

interface Agent {
  agent_id: string
  agent_name: string
  status: string
  current_load: number
  total_tasks_processed: number
}

interface Stats {
  total_tasks_routed: number
  tasks_by_type: Record<string, number>
  tasks_by_agent: Record<string, number>
  average_processing_time_ms: number
}

export default function AgentStatus() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const [agentData, statsData] = await Promise.all([
        getAgentStatus(),
        getRoutingStats()
      ])
      setAgents(agentData)
      setStats(statsData)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load agent status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    // Refresh every 10 seconds
    const interval = setInterval(loadData, 10000)
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'available':
        return 'bg-green-500'
      case 'busy':
        return 'bg-yellow-500'
      case 'offline':
      case 'unavailable':
        return 'bg-red-500'
      default:
        return 'bg-slate-500'
    }
  }

  const formatAgentName = (name: string) => {
    return name.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="text-blue-400" size={24} />
            <h2 className="text-xl font-bold text-white">Agent Status Dashboard</h2>
          </div>
          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`text-slate-300 ${loading ? 'animate-spin' : ''}`} size={20} />
          </button>
        </div>
      </div>

      {error && (
        <div className="flex items-start space-x-2 p-4 bg-red-900/20 border border-red-800 rounded-lg">
          <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={18} />
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-blue-900/50 to-blue-800/30 backdrop-blur-sm rounded-xl shadow-xl border border-blue-700 p-6">
            <div className="flex items-center space-x-2 text-blue-400 mb-2">
              <TrendingUp size={20} />
              <span className="text-sm font-medium">Total Tasks Routed</span>
            </div>
            <p className="text-3xl font-bold text-white">{stats.total_tasks_routed}</p>
          </div>

          <div className="bg-gradient-to-br from-purple-900/50 to-purple-800/30 backdrop-blur-sm rounded-xl shadow-xl border border-purple-700 p-6">
            <div className="flex items-center space-x-2 text-purple-400 mb-2">
              <Users size={20} />
              <span className="text-sm font-medium">Active Agents</span>
            </div>
            <p className="text-3xl font-bold text-white">
              {agents.filter(a => a.status.toLowerCase() === 'active' || a.status.toLowerCase() === 'available').length}
            </p>
          </div>

          <div className="bg-gradient-to-br from-green-900/50 to-green-800/30 backdrop-blur-sm rounded-xl shadow-xl border border-green-700 p-6">
            <div className="flex items-center space-x-2 text-green-400 mb-2">
              <Activity size={20} />
              <span className="text-sm font-medium">Avg Processing Time</span>
            </div>
            <p className="text-3xl font-bold text-white">{stats.average_processing_time_ms}ms</p>
          </div>

          <div className="bg-gradient-to-br from-yellow-900/50 to-yellow-800/30 backdrop-blur-sm rounded-xl shadow-xl border border-yellow-700 p-6">
            <div className="flex items-center space-x-2 text-yellow-400 mb-2">
              <TrendingUp size={20} />
              <span className="text-sm font-medium">Task Types</span>
            </div>
            <p className="text-3xl font-bold text-white">{Object.keys(stats.tasks_by_type).length}</p>
          </div>
        </div>
      )}

      {/* Agents List */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 p-6">
        <h3 className="text-lg font-bold text-white mb-4">AI Specialist Agents</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <div
              key={agent.agent_id}
              className="bg-slate-900/50 p-5 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <h4 className="font-semibold text-white">{formatAgentName(agent.agent_name)}</h4>
                <div className="flex items-center space-x-2">
                  <div className={`h-3 w-3 rounded-full ${getStatusColor(agent.status)}`}></div>
                  <span className="text-xs text-slate-400 capitalize">{agent.status}</span>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Current Load:</span>
                  <span className="text-white font-medium">{agent.current_load}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Tasks Processed:</span>
                  <span className="text-white font-medium">{agent.total_tasks_processed}</span>
                </div>
              </div>

              {/* Load Bar */}
              <div className="mt-3">
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      agent.current_load > 80 ? 'bg-red-500' :
                      agent.current_load > 50 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(agent.current_load, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Task Distribution */}
      {stats && Object.keys(stats.tasks_by_type).length > 0 && (
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 p-6">
          <h3 className="text-lg font-bold text-white mb-4">Task Distribution by Type</h3>
          <div className="space-y-3">
            {Object.entries(stats.tasks_by_type).map(([type, count]) => (
              <div key={type} className="flex items-center space-x-3">
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-slate-300 capitalize">
                      {type.split('_').join(' ')}
                    </span>
                    <span className="text-sm text-white font-semibold">{count}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{
                        width: `${(count / Math.max(...Object.values(stats.tasks_by_type))) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
