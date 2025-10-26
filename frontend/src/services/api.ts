import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface TaskRouteRequest {
  text: string;
  priority?: number;
  metadata?: Record<string, any>;
}

export interface TaskRouteResponse {
  status: string;
  message: string;
  data: {
    processing_id: string;
    normalized_text: string;
    extracted_entities: Record<string, any[]>;
    pii_phi_labels: {
      pii: string[];
      phi: string[];
    };
    detected_tasks: Array<{
      id: string;
      task_type: string;
      description: string;
      priority: string;
      extracted_data: Record<string, any>;
    }>;
    routing_decisions: Array<{
      agent_id: string;
      agent_name: string;
      confidence: number;
      reasoning: string;
      estimated_completion_time: number;
      agent_specialties: string[];
    }>;
    approval_required: string | boolean;
    proposed_actions?: any[];
    specialist_output?: any;
    case_id?: string;
    source_type: string;
    processed_at: string;
  };
}

export interface AgentStatus {
  agent_id: string;
  agent_name: string;
  status: string;
  current_load: number;
  total_tasks_processed: number;
}

export interface EmailForwardRequest {
  subject: string;
  from: string;
  body: string;
  attachments?: string[];
}

export interface SMSRequest {
  to: string;
  message: string;
}

export interface SMSResponse {
  sid: string;
  status: string;
  to: string;
  from: string;
  message: string;
  timestamp: string;
}

// Call specialist agent to get actual output
const callSpecialist = async (agentId: string, text: string, metadata: any = {}) => {
  try {
    let endpoint = '';
    let payload: any = { text };

    switch (agentId) {
      case 'legal_researcher':
        endpoint = '/api/specialists/legal-researcher/analyze';
        payload = { text, metadata };
        break;
      case 'communication_guru':
        endpoint = '/api/specialists/client-communication/draft';
        payload = { text, client_name: metadata.client_name, purpose: metadata.purpose };
        break;
      case 'records_wrangler':
        endpoint = '/api/specialists/records-wrangler/analyze';
        payload = { text };
        break;
      case 'voice_scheduler':
        endpoint = '/api/specialists/voice-scheduler/parse-request';
        payload = { text };
        break;
      case 'evidence_sorter':
        endpoint = '/api/specialists/evidence-sorter/analyze-document';
        payload = { filename: 'input.txt', text_content: text };
        break;
      default:
        return null;
    }

    const response = await api.post(endpoint, payload);
    return response.data;
  } catch (error) {
    console.error('Error calling specialist:', error);
    return null;
  }
};

// Task routing - uses orchestrator for raw text processing
export const routeTask = async (request: TaskRouteRequest): Promise<TaskRouteResponse> => {
  try {
    console.log('Sending request to orchestrator:', request);

    // Process with orchestrator - it now auto-calls specialists via Gemini
    const orchestratorResponse = await api.post('/api/orchestrator/process', {
      raw_text: request.text,
      source_type: 'manual_entry',
      metadata: request.metadata || {}
    });

    console.log('Orchestrator response:', orchestratorResponse.data);

    const result = orchestratorResponse.data;

    // Extract specialist response from orchestrator's specialist_responses
    if (result.data?.specialist_responses && result.data.specialist_responses.length > 0) {
      const specialistResponse = result.data.specialist_responses[0];

      console.log('Specialist response:', specialistResponse);

      // Add specialist output to the expected format
      if (specialistResponse.response && specialistResponse.status === 'success') {
        result.data.specialist_output = specialistResponse.response;
        console.log('Set specialist_output:', result.data.specialist_output);
      }
    }

    console.log('Returning result:', result);
    return result;
  } catch (error) {
    console.error('Error in routeTask:', error);
    throw error;
  }
};

// Get agent status
export const getAgentStatus = async (): Promise<AgentStatus[]> => {
  const response = await api.get('/api/router/agents/status');
  return response.data.agents;
};

// Get routing stats
export const getRoutingStats = async () => {
  const response = await api.get('/api/router/stats');
  return response.data;
};

// Email forwarding
export const forwardEmail = async (email: EmailForwardRequest) => {
  const response = await api.post('/api/email/forward', email);
  return response.data;
};

// Get emails
export const getEmails = async (limit: number = 50) => {
  const response = await api.get(`/api/email/inbox?limit=${limit}`);
  return response.data;
};

// Send SMS
export const sendSMS = async (smsRequest: SMSRequest): Promise<SMSResponse> => {
  const response = await api.post('/api/sms/send', smsRequest);
  return response.data;
};

// Get SMS history
export const getSMSHistory = async (limit: number = 50) => {
  const response = await api.get(`/api/sms/history?limit=${limit}`);
  return response.data;
};

export default api;
