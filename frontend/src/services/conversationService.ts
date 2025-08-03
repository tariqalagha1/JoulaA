import api from './api'
import { AxiosResponse } from 'axios'

// Types
export interface Message {
  id: string
  conversation_id: string
  content: string
  role: 'user' | 'assistant' | 'system'
  type: 'text' | 'image' | 'file' | 'audio'
  language?: string
  tokens_used?: number
  processing_time?: number
  attachments?: any[]
  metadata?: Record<string, any>
  created_at: string
  updated_at?: string
}

export interface Conversation {
  id: string
  title?: string
  summary?: string
  language: string
  status: 'active' | 'archived' | 'deleted'
  message_count: number
  user_id: string
  agent_id?: string
  organization_id?: string
  settings?: Record<string, any>
  metadata?: Record<string, any>
  created_at: string
  updated_at?: string
  last_message_at?: string
  messages?: Message[]
}

export interface ConversationCreate {
  title?: string
  language?: string
  agent_id?: string
  organization_id?: string
  settings?: Record<string, any>
  metadata?: Record<string, any>
  initial_message?: string
}

export interface ConversationUpdate {
  title?: string
  summary?: string
  language?: string
  status?: 'active' | 'archived' | 'deleted'
  settings?: Record<string, any>
  metadata?: Record<string, any>
}

export interface MessageCreate {
  content: string
  role?: 'user' | 'assistant' | 'system'
  type?: 'text' | 'image' | 'file' | 'audio'
  language?: string
  attachments?: any[]
  metadata?: Record<string, any>
}

export interface ConversationListResponse {
  conversations: Conversation[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface MessageListResponse {
  messages: Message[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface ChatRequest {
  message: string
  conversation_id?: string
  agent_id?: string
  language?: string
  attachments?: any[]
  stream?: boolean
}

export interface ChatResponse {
  message: Message
  conversation: Conversation
  agent_response?: Message
}

export interface ConversationStats {
  total_conversations: number
  active_conversations: number
  archived_conversations: number
  total_messages: number
  avg_messages_per_conversation: number
  conversations_today: number
  conversations_this_week: number
  conversations_this_month: number
  most_active_agent?: any
  recent_activity: any[]
}

class ConversationService {
  private readonly baseUrl = '/conversations'

  // List conversations with filtering and pagination
  async listConversations(params?: {
    query?: string
    status?: string
    agent_id?: string
    organization_id?: string
    language?: string
    date_from?: string
    date_to?: string
    sort_by?: string
    sort_order?: 'asc' | 'desc'
    page?: number
    page_size?: number
  }): Promise<ConversationListResponse> {
    const response: AxiosResponse<ConversationListResponse> = await api.get(this.baseUrl, { params })
    return response.data
  }

  // Create a new conversation
  async createConversation(conversationData: ConversationCreate): Promise<Conversation> {
    const response: AxiosResponse<Conversation> = await api.post(this.baseUrl, conversationData)
    return response.data
  }

  // Get conversation by ID
  async getConversation(conversationId: string, includeMessages?: boolean): Promise<Conversation> {
    const params = includeMessages ? { include_messages: true } : {}
    const response: AxiosResponse<Conversation> = await api.get(`${this.baseUrl}/${conversationId}`, { params })
    return response.data
  }

  // Update conversation
  async updateConversation(conversationId: string, updateData: ConversationUpdate): Promise<Conversation> {
    const response: AxiosResponse<Conversation> = await api.put(`${this.baseUrl}/${conversationId}`, updateData)
    return response.data
  }

  // Delete conversation
  async deleteConversation(conversationId: string, softDelete: boolean = true): Promise<void> {
    await api.delete(`${this.baseUrl}/${conversationId}`, {
      params: { soft_delete: softDelete }
    })
  }

  // Add message to conversation
  async addMessage(conversationId: string, messageData: MessageCreate): Promise<Message> {
    const response: AxiosResponse<Message> = await api.post(`${this.baseUrl}/${conversationId}/messages`, messageData)
    return response.data
  }

  // Get messages for a conversation
  async getMessages(conversationId: string, params?: {
    page?: number
    page_size?: number
    sort_order?: 'asc' | 'desc'
  }): Promise<MessageListResponse> {
    const response: AxiosResponse<MessageListResponse> = await api.get(`${this.baseUrl}/${conversationId}/messages`, { params })
    return response.data
  }

  // Send chat message and get AI response
  async chat(chatRequest: ChatRequest): Promise<ChatResponse> {
    const response: AxiosResponse<ChatResponse> = await api.post(`${this.baseUrl}/chat`, chatRequest)
    return response.data
  }

  // Stream chat response
  async streamChat(chatRequest: ChatRequest, onChunk: (chunk: any) => void): Promise<void> {
    const response = await api.post(`${this.baseUrl}/chat`, { ...chatRequest, stream: true }, {
      responseType: 'stream'
    })
    
    const reader = response.data.getReader()
    const decoder = new TextDecoder()
    
    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              onChunk(data)
            } catch (e) {
              // Ignore parsing errors
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  }

  // Get conversation statistics
  async getConversationStats(organizationId?: string): Promise<ConversationStats> {
    const params = organizationId ? { organization_id: organizationId } : {}
    const response: AxiosResponse<ConversationStats> = await api.get(`${this.baseUrl}/stats`, { params })
    return response.data
  }

  // Bulk operations on conversations
  async bulkOperation(operation: string, conversationIds: string[], options?: Record<string, any>): Promise<any> {
    const response = await api.post(`${this.baseUrl}/bulk`, {
      operation,
      conversation_ids: conversationIds,
      options: options || {}
    })
    return response.data
  }

  // Search conversations
  async searchConversations(query: string, params?: {
    agent_id?: string
    organization_id?: string
    date_from?: string
    date_to?: string
    page?: number
    page_size?: number
  }): Promise<ConversationListResponse> {
    const response: AxiosResponse<ConversationListResponse> = await api.get(`${this.baseUrl}/search`, {
      params: { query, ...params }
    })
    return response.data
  }

  // Export conversation
  async exportConversation(conversationId: string, format: 'json' | 'txt' | 'pdf' = 'json'): Promise<any> {
    const response = await api.get(`${this.baseUrl}/${conversationId}/export`, {
      params: { format }
    })
    return response.data
  }

  // Share conversation
  async shareConversation(conversationId: string, shareSettings: {
    is_public?: boolean
    expires_at?: string
    password?: string
  }): Promise<any> {
    const response = await api.post(`${this.baseUrl}/${conversationId}/share`, shareSettings)
    return response.data
  }
}

export const conversationService = new ConversationService()
export default conversationService