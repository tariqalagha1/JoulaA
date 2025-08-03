import api from './api'
import { AxiosResponse } from 'axios'

// Types
export interface Agent {
  id: string
  name: string
  description?: string
  instructions?: string
  model?: string
  temperature?: number
  max_tokens?: number
  tools?: string[]
  knowledge_base?: any
  integrations?: string[]
  is_active: boolean
  is_public: boolean
  organization_id?: string
  created_by: string
  created_at: string
  updated_at?: string
  metadata?: Record<string, any>
}

export interface AgentCreate {
  name: string
  description?: string
  instructions?: string
  model?: string
  temperature?: number
  max_tokens?: number
  tools?: string[]
  knowledge_base?: any
  integrations?: string[]
  is_active?: boolean
  is_public?: boolean
  organization_id?: string
  metadata?: Record<string, any>
}

export interface AgentUpdate {
  name?: string
  description?: string
  instructions?: string
  model?: string
  temperature?: number
  max_tokens?: number
  tools?: string[]
  knowledge_base?: any
  integrations?: string[]
  is_active?: boolean
  is_public?: boolean
  metadata?: Record<string, any>
}

export interface AgentListResponse {
  agents: Agent[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface AgentStats {
  total_agents: number
  active_agents: number
  public_agents: number
  private_agents: number
  total_conversations: number
  avg_conversations_per_agent: number
  most_used_agent?: Agent
  recent_activity: any[]
}

class AgentService {
  private readonly baseUrl = '/agents'

  // List agents with filtering and pagination
  async listAgents(params?: {
    query?: string
    is_active?: boolean
    is_public?: boolean
    organization_id?: string
    created_by?: string
    model?: string
    sort_by?: string
    sort_order?: 'asc' | 'desc'
    page?: number
    page_size?: number
  }): Promise<AgentListResponse> {
    const response: AxiosResponse<AgentListResponse> = await api.get(this.baseUrl, { params })
    return response.data
  }

  // Create a new agent
  async createAgent(agentData: AgentCreate): Promise<Agent> {
    const response: AxiosResponse<Agent> = await api.post(this.baseUrl, agentData)
    return response.data
  }

  // Get agent by ID
  async getAgent(agentId: string, includeStats?: boolean): Promise<Agent> {
    const params = includeStats ? { include_stats: true } : {}
    const response: AxiosResponse<Agent> = await api.get(`${this.baseUrl}/${agentId}`, { params })
    return response.data
  }

  // Update agent
  async updateAgent(agentId: string, updateData: AgentUpdate): Promise<Agent> {
    const response: AxiosResponse<Agent> = await api.put(`${this.baseUrl}/${agentId}`, updateData)
    return response.data
  }

  // Delete agent
  async deleteAgent(agentId: string, softDelete: boolean = true): Promise<void> {
    await api.delete(`${this.baseUrl}/${agentId}`, {
      params: { soft_delete: softDelete }
    })
  }

  // Clone agent
  async cloneAgent(agentId: string, newName?: string): Promise<Agent> {
    const response: AxiosResponse<Agent> = await api.post(`${this.baseUrl}/${agentId}/clone`, {
      name: newName
    })
    return response.data
  }

  // Test agent
  async testAgent(agentId: string, message: string): Promise<any> {
    const response = await api.post(`${this.baseUrl}/${agentId}/test`, {
      message
    })
    return response.data
  }

  // Get agent statistics
  async getAgentStats(organizationId?: string): Promise<AgentStats> {
    const params = organizationId ? { organization_id: organizationId } : {}
    const response: AxiosResponse<AgentStats> = await api.get(`${this.baseUrl}/stats`, { params })
    return response.data
  }

  // Bulk operations
  async bulkOperation(operation: string, agentIds: string[], options?: Record<string, any>): Promise<any> {
    const response = await api.post(`${this.baseUrl}/bulk`, {
      operation,
      agent_ids: agentIds,
      options: options || {}
    })
    return response.data
  }

  // Export agent configuration
  async exportAgent(agentId: string): Promise<any> {
    const response = await api.get(`${this.baseUrl}/${agentId}/export`)
    return response.data
  }

  // Import agent configuration
  async importAgent(configData: any): Promise<Agent> {
    const response: AxiosResponse<Agent> = await api.post(`${this.baseUrl}/import`, configData)
    return response.data
  }

  // Get agent conversation history
  async getAgentConversations(agentId: string, params?: {
    page?: number
    page_size?: number
    status?: string
  }): Promise<any> {
    const response = await api.get(`${this.baseUrl}/${agentId}/conversations`, { params })
    return response.data
  }
}

export const agentService = new AgentService()
export default agentService