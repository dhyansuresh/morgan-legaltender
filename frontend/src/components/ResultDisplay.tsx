import { CheckCircle, Clock, User, Zap, FileText } from 'lucide-react'
import { TaskRouteResponse } from '../services/api'

interface ResultDisplayProps {
  result: TaskRouteResponse
}

export default function ResultDisplay({ result }: ResultDisplayProps) {
  const formatTaskType = (type: string) => {
    return type.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  const formatAgentName = (agent: string) => {
    return agent.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ')
  }

  // Safety check: ensure data exists
  if (!result || !result.data || !result.data.detected_tasks || result.data.detected_tasks.length === 0) {
    return (
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 p-8">
        <p className="text-slate-400">No tasks detected. Try entering a different query.</p>
      </div>
    )
  }

  // Extract first detected task and routing decision for display
  const firstTask = result.data.detected_tasks[0]
  const routing = result.data.routing_decisions?.[0]

  const renderAgentResult = () => {
    if (!firstTask) return null

    const agentId = routing?.agent_id || 'unknown'
    const specialistOutput = result.data.specialist_output

    // Display specialist-specific output
    const renderSpecialistOutput = () => {
      if (!specialistOutput) return null

      // Client Communication output
      if (agentId === 'communication_guru' && specialistOutput.draft_message) {
        return (
          <div className="space-y-4">
            {specialistOutput.subject && (
              <div>
                <h4 className="font-semibold text-white mb-2">Subject:</h4>
                <p className="text-slate-300">{specialistOutput.subject}</p>
              </div>
            )}
            <div>
              <h4 className="font-semibold text-white mb-2">Draft Message:</h4>
              <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
                <p className="text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {specialistOutput.draft_message}
                </p>
              </div>
            </div>
            {specialistOutput.suggested_followups && specialistOutput.suggested_followups.length > 0 && (
              <div>
                <h4 className="font-semibold text-white mb-2">Suggested Follow-ups:</h4>
                <ul className="list-disc list-inside space-y-1 text-slate-300">
                  {specialistOutput.suggested_followups.map((followup: string, idx: number) => (
                    <li key={idx}>{followup}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )
      }

      // Legal Research output
      if (agentId === 'legal_researcher') {
        return (
          <div className="space-y-4">
            {specialistOutput.issues && specialistOutput.issues.length > 0 && (
              <div>
                <h4 className="font-semibold text-white mb-2">Key Issues Identified:</h4>
                <ul className="list-disc list-inside space-y-1 text-slate-300">
                  {specialistOutput.issues.map((issue: string, idx: number) => (
                    <li key={idx}>{issue}</li>
                  ))}
                </ul>
              </div>
            )}
            {specialistOutput.citations && specialistOutput.citations.length > 0 && (
              <div>
                <h4 className="font-semibold text-white mb-2">Relevant Citations:</h4>
                <ul className="list-disc list-inside space-y-2 text-slate-300">
                  {specialistOutput.citations.map((citation: any, idx: number) => (
                    <li key={idx} className="font-mono text-sm">
                      {typeof citation === 'string' ? citation : (
                        <div>
                          <div className="font-semibold">{citation.title || 'Untitled'}</div>
                          {citation.citation && <div className="text-xs text-slate-400">{citation.citation}</div>}
                          {citation.url && (
                            <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 text-xs">
                              View Source
                            </a>
                          )}
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {specialistOutput.suggested_actions && specialistOutput.suggested_actions.length > 0 && (
              <div>
                <h4 className="font-semibold text-white mb-2">Suggested Actions:</h4>
                <ul className="list-disc list-inside space-y-1 text-slate-300">
                  {specialistOutput.suggested_actions.map((action: string, idx: number) => (
                    <li key={idx}>{action}</li>
                  ))}
                </ul>
              </div>
            )}
            {specialistOutput.brief && (
              <div>
                <h4 className="font-semibold text-white mb-2">Summary Brief:</h4>
                <p className="text-slate-300 leading-relaxed">{specialistOutput.brief}</p>
              </div>
            )}
          </div>
        )
      }

      // Generic output for other specialists
      return (
        <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
          <pre className="text-slate-300 text-sm whitespace-pre-wrap overflow-x-auto">
            {JSON.stringify(specialistOutput, null, 2)}
          </pre>
        </div>
      )
    }

    // Display task information
    return (
      <div className="space-y-4">
        <div>
          <h4 className="font-semibold text-white mb-2">Task Description:</h4>
          <p className="text-slate-300">{firstTask.description}</p>
        </div>

        {routing && (
          <>
            <div>
              <h4 className="font-semibold text-white mb-2">Routing Decision:</h4>
              <p className="text-slate-300">{routing.reasoning}</p>
              <p className="text-sm text-slate-400 mt-1">
                Confidence: {(routing.confidence * 100).toFixed(1)}%
              </p>
            </div>
          </>
        )}

        {specialistOutput && (
          <div>
            <h4 className="font-semibold text-white mb-3">Agent Output:</h4>
            {renderSpecialistOutput()}
          </div>
        )}

        {!specialistOutput && Object.keys(firstTask.extracted_data || {}).length > 0 && (
          <div>
            <h4 className="font-semibold text-white mb-2">Extracted Information:</h4>
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
              <pre className="text-slate-300 text-sm whitespace-pre-wrap overflow-x-auto">
                {JSON.stringify(firstTask.extracted_data, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {result.data.detected_tasks.length > 1 && (
          <div>
            <h4 className="font-semibold text-white mb-2">Additional Tasks Detected:</h4>
            <ul className="list-disc list-inside space-y-1 text-slate-300">
              {result.data.detected_tasks.slice(1).map((task, idx) => (
                <li key={idx}>{task.description}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    )

    // Legacy handling - keeping for reference but won't be reached
    if (agentId === 'legal_researcher' && false) {
      return (
        <div className="space-y-4">
          {result.result.issues && result.result.issues.length > 0 && (
            <div>
              <h4 className="font-semibold text-white mb-2">Key Issues Identified:</h4>
              <ul className="list-disc list-inside space-y-1 text-slate-300">
                {result.result.issues.map((issue: string, idx: number) => (
                  <li key={idx}>{issue}</li>
                ))}
              </ul>
            </div>
          )}

          {result.result.citations && result.result.citations.length > 0 && (
            <div>
              <h4 className="font-semibold text-white mb-2">Relevant Citations:</h4>
              <ul className="list-disc list-inside space-y-1 text-slate-300">
                {result.result.citations.map((citation: string, idx: number) => (
                  <li key={idx} className="font-mono text-sm">{citation}</li>
                ))}
              </ul>
            </div>
          )}

          {result.result.suggested_actions && result.result.suggested_actions.length > 0 && (
            <div>
              <h4 className="font-semibold text-white mb-2">Suggested Actions:</h4>
              <ul className="list-disc list-inside space-y-1 text-slate-300">
                {result.result.suggested_actions.map((action: string, idx: number) => (
                  <li key={idx}>{action}</li>
                ))}
              </ul>
            </div>
          )}

          {result.result.brief && (
            <div>
              <h4 className="font-semibold text-white mb-2">Summary Brief:</h4>
              <p className="text-slate-300 leading-relaxed">{result.result.brief}</p>
            </div>
          )}
        </div>
      )
    }

    if (result.assigned_agent === 'communication_guru' && result.result.draft_message) {
      return (
        <div className="space-y-4">
          {result.result.subject && (
            <div>
              <h4 className="font-semibold text-white mb-2">Subject:</h4>
              <p className="text-slate-300">{result.result.subject}</p>
            </div>
          )}

          {result.result.draft_message && (
            <div>
              <h4 className="font-semibold text-white mb-2">Draft Message:</h4>
              <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
                <p className="text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {result.result.draft_message}
                </p>
              </div>
            </div>
          )}

          {result.result.suggested_followups && result.result.suggested_followups.length > 0 && (
            <div>
              <h4 className="font-semibold text-white mb-2">Suggested Follow-ups:</h4>
              <ul className="list-disc list-inside space-y-1 text-slate-300">
                {result.result.suggested_followups.map((followup: string, idx: number) => (
                  <li key={idx}>{followup}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )
    }

    // Generic result display
    return (
      <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
        <pre className="text-slate-300 text-sm whitespace-pre-wrap overflow-x-auto">
          {JSON.stringify(result.result, null, 2)}
        </pre>
      </div>
    )
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700 p-8">
      {/* Header */}
      <div className="flex items-center space-x-3 mb-6 pb-6 border-b border-slate-700">
        <CheckCircle className="text-green-500" size={32} />
        <div>
          <h2 className="text-2xl font-bold text-white">Input Processed Successfully</h2>
          <p className="text-slate-400 text-sm">Processing ID: {result.data.processing_id}</p>
        </div>
      </div>

      {/* Task Info Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
          <div className="flex items-center space-x-2 text-blue-400 mb-2">
            <FileText size={18} />
            <span className="text-sm font-medium">Tasks Detected</span>
          </div>
          <p className="text-white font-semibold">{result.data.detected_tasks.length}</p>
        </div>

        {firstTask && (
          <>
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
              <div className="flex items-center space-x-2 text-purple-400 mb-2">
                <User size={18} />
                <span className="text-sm font-medium">Primary Agent</span>
              </div>
              <p className="text-white font-semibold">
                {routing ? formatAgentName(routing.agent_name) : 'Pending'}
              </p>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
              <div className="flex items-center space-x-2 text-green-400 mb-2">
                <CheckCircle size={18} />
                <span className="text-sm font-medium">Task Type</span>
              </div>
              <p className="text-white font-semibold capitalize">{formatTaskType(firstTask.task_type)}</p>
            </div>

            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700">
              <div className="flex items-center space-x-2 text-yellow-400 mb-2">
                <Zap size={18} />
                <span className="text-sm font-medium">Priority</span>
              </div>
              <p className="text-white font-semibold capitalize">{firstTask.priority}</p>
            </div>
          </>
        )}
      </div>

      {/* Agent Response */}
      <div className="bg-gradient-to-br from-slate-900/80 to-slate-800/80 p-6 rounded-lg border border-slate-600">
        <div className="flex items-center space-x-2 mb-4">
          <FileText className="text-blue-400" size={20} />
          <h3 className="text-xl font-bold text-white">Agent Response</h3>
        </div>
        {renderAgentResult()}
      </div>

      {/* Timestamp and Metadata */}
      <div className="mt-6 flex items-center justify-between text-sm text-slate-400">
        <div className="flex items-center space-x-2">
          <Clock size={16} />
          <span>Processed at: {new Date(result.data.processed_at).toLocaleString()}</span>
        </div>
        {result.data.approval_required && (
          <div className="flex items-center space-x-2">
            <CheckCircle size={16} className="text-yellow-400" />
            <span className="text-yellow-400">Approval Required</span>
          </div>
        )}
      </div>
    </div>
  )
}
