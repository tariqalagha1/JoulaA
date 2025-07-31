import api from './api'
import { AxiosResponse } from 'axios'

// Types
export interface Organization {
  id: string
  name_ar: string
  name_en?: string
  description_ar?: string
  description_en?: string
  website?: string
  industry?: string
  size?: string
  subscription_plan: string
  subscription_status: string
  settings?: Record<string, any>
  contact_email?: string
  contact_phone?: string
  address?: Record<string, any>
  logo_url?: string
  is_active: boolean
  created_at: string
  updated_at?: string
  metadata?: Record<string, any>
}

export interface OrganizationMember {
  id: string
  user_id: string
  organization_id: string
  role: string
  is_active: boolean
  joined_at: string
  user?: {
    id: string
    email: string
    username: string
    full_name_ar?: string
    full_name_en?: string
  }
}

export interface OrganizationCreate {
  name_ar: string
  name_en?: string
  description_ar?: string
  description_en?: string
  website?: string
  industry?: string
  size?: string
  subscription_plan?: string
  contact_email?: string
  contact_phone?: string
  address?: Record<string, any>
  settings?: Record<string, any>
  metadata?: Record<string, any>
}

export interface OrganizationUpdate {
  name_ar?: string
  name_en?: string
  description_ar?: string
  description_en?: string
  website?: string
  industry?: string
  size?: string
  subscription_plan?: string
  contact_email?: string
  contact_phone?: string
  address?: Record<string, any>
  logo_url?: string
  settings?: Record<string, any>
  metadata?: Record<string, any>
}

export interface OrganizationMemberCreate {
  user_id: string
  role: string
}

export interface OrganizationMemberUpdate {
  role?: string
  is_active?: boolean
}

export interface OrganizationListResponse {
  organizations: Organization[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

export interface OrganizationStats {
  total_members: number
  active_members: number
  total_agents: number
  total_conversations: number
  storage_used: number
  api_calls_this_month: number
  subscription_usage: Record<string, any>
  recent_activity: any[]
}

class OrganizationService {
  private readonly baseUrl = '/organizations'

  // List organizations with filtering and pagination
  async listOrganizations(params?: {
    query?: string
    industry?: string
    size?: string
    subscription_plan?: string
    is_active?: boolean
    sort_by?: string
    sort_order?: 'asc' | 'desc'
    page?: number
    page_size?: number
  }): Promise<OrganizationListResponse> {
    const response: AxiosResponse<OrganizationListResponse> = await api.get(this.baseUrl, { params })
    return response.data
  }

  // Create a new organization
  async createOrganization(organizationData: OrganizationCreate): Promise<Organization> {
    const response: AxiosResponse<Organization> = await api.post(this.baseUrl, organizationData)
    return response.data
  }

  // Get organization by ID
  async getOrganization(organizationId: string, includeMembers?: boolean): Promise<Organization> {
    const params = includeMembers ? { include_members: true } : {}
    const response: AxiosResponse<Organization> = await api.get(`${this.baseUrl}/${organizationId}`, { params })
    return response.data
  }

  // Update organization
  async updateOrganization(organizationId: string, updateData: OrganizationUpdate): Promise<Organization> {
    const response: AxiosResponse<Organization> = await api.put(`${this.baseUrl}/${organizationId}`, updateData)
    return response.data
  }

  // Delete organization
  async deleteOrganization(organizationId: string, softDelete: boolean = true): Promise<void> {
    await api.delete(`${this.baseUrl}/${organizationId}`, {
      params: { soft_delete: softDelete }
    })
  }

  // Add member to organization
  async addMember(organizationId: string, memberData: OrganizationMemberCreate): Promise<OrganizationMember> {
    const response: AxiosResponse<OrganizationMember> = await api.post(`${this.baseUrl}/${organizationId}/members`, memberData)
    return response.data
  }

  // Remove member from organization
  async removeMember(organizationId: string, userId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/${organizationId}/members/${userId}`)
  }

  // List organization members
  async listMembers(organizationId: string, params?: {
    role?: string
    is_active?: boolean
    page?: number
    page_size?: number
  }): Promise<{
    members: OrganizationMember[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }> {
    const response = await api.get(`${this.baseUrl}/${organizationId}/members`, { params })
    return response.data
  }

  // Update member role/status
  async updateMember(organizationId: string, userId: string, updateData: OrganizationMemberUpdate): Promise<OrganizationMember> {
    const response: AxiosResponse<OrganizationMember> = await api.put(`${this.baseUrl}/${organizationId}/members/${userId}`, updateData)
    return response.data
  }

  // Get organization statistics
  async getOrganizationStats(organizationId: string): Promise<OrganizationStats> {
    const response: AxiosResponse<OrganizationStats> = await api.get(`${this.baseUrl}/${organizationId}/stats`)
    return response.data
  }

  // Invite user to organization
  async inviteUser(organizationId: string, inviteData: {
    email: string
    role: string
    message?: string
  }): Promise<any> {
    const response = await api.post(`${this.baseUrl}/${organizationId}/invite`, inviteData)
    return response.data
  }

  // Get organization invitations
  async getInvitations(organizationId: string, params?: {
    status?: string
    page?: number
    page_size?: number
  }): Promise<any> {
    const response = await api.get(`${this.baseUrl}/${organizationId}/invitations`, { params })
    return response.data
  }

  // Cancel invitation
  async cancelInvitation(organizationId: string, invitationId: string): Promise<void> {
    await api.delete(`${this.baseUrl}/${organizationId}/invitations/${invitationId}`)
  }

  // Accept invitation
  async acceptInvitation(token: string): Promise<any> {
    const response = await api.post('/invitations/accept', { token })
    return response.data
  }

  // Decline invitation
  async declineInvitation(token: string): Promise<void> {
    await api.post('/invitations/decline', { token })
  }

  // Upload organization logo
  async uploadLogo(organizationId: string, file: File): Promise<{ logo_url: string }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post(`${this.baseUrl}/${organizationId}/logo`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }

  // Get organization usage/billing info
  async getUsageInfo(organizationId: string): Promise<any> {
    const response = await api.get(`${this.baseUrl}/${organizationId}/usage`)
    return response.data
  }

  // Update subscription
  async updateSubscription(organizationId: string, subscriptionData: {
    plan: string
    billing_cycle?: string
  }): Promise<any> {
    const response = await api.put(`${this.baseUrl}/${organizationId}/subscription`, subscriptionData)
    return response.data
  }

  // Get available subscription plans
  async getSubscriptionPlans(): Promise<any> {
    const response = await api.get('/subscription-plans')
    return response.data
  }
}

export const organizationService = new OrganizationService()
export default organizationService