import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Filter, Grid, List, RefreshCw } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'

import AgentCard from './AgentCard'
import AgentForm from './AgentForm'
import { agentService, Agent, AgentCreate, AgentUpdate } from '../../services/agentService'

const AgentsList: React.FC = () => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  
  const [searchQuery, setSearchQuery] = useState('')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingAgent, setEditingAgent] = useState<Agent | undefined>()
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [filters, setFilters] = useState({
    is_active: undefined as boolean | undefined,
    is_public: undefined as boolean | undefined,
    model: undefined as string | undefined,
  })

  // Fetch agents
  const {
    data: agentsData,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['agents', searchQuery, filters],
    queryFn: () => agentService.listAgents({
      query: searchQuery || undefined,
      ...filters,
      page: 1,
      page_size: 50
    }),
    staleTime: 30000, // 30 seconds
  })

  // Create agent mutation
  const createAgentMutation = useMutation({
    mutationFn: (data: AgentCreate) => agentService.createAgent(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      toast.success(t('agents.createSuccess'))
      setIsFormOpen(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || t('agents.createError'))
    }
  })

  // Update agent mutation
  const updateAgentMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: AgentUpdate }) => 
      agentService.updateAgent(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      toast.success(t('agents.updateSuccess'))
      setEditingAgent(undefined)
      setIsFormOpen(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || t('agents.updateError'))
    }
  })

  // Delete agent mutation
  const deleteAgentMutation = useMutation({
    mutationFn: (agentId: string) => agentService.deleteAgent(agentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      toast.success(t('agents.deleteSuccess'))
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || t('agents.deleteError'))
    }
  })

  // Toggle agent status mutation
  const toggleStatusMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) => 
      agentService.updateAgent(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      toast.success(t('agents.statusUpdated'))
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || t('agents.statusUpdateError'))
    }
  })

  const handleCreateAgent = () => {
    setEditingAgent(undefined)
    setIsFormOpen(true)
  }

  const handleEditAgent = (agent: Agent) => {
    setEditingAgent(agent)
    setIsFormOpen(true)
  }

  const handleDeleteAgent = async (agentId: string) => {
    if (window.confirm(t('agents.deleteConfirm'))) {
      deleteAgentMutation.mutate(agentId)
    }
  }

  const handleToggleStatus = (agentId: string, isActive: boolean) => {
    toggleStatusMutation.mutate({ id: agentId, is_active: isActive })
  }

  const handleFormSubmit = async (data: AgentCreate | AgentUpdate) => {
    if (editingAgent) {
      updateAgentMutation.mutate({ id: editingAgent.id, data: data as AgentUpdate })
    } else {
      createAgentMutation.mutate(data as AgentCreate)
    }
  }

  const handleChat = (agent: Agent) => {
    // Navigate to chat with this agent
    window.location.href = `/dashboard/chat?agent=${agent.id}`
  }

  const filteredAgents = agentsData?.agents || []

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('agents.title')}</h1>
          <p className="text-gray-600 mt-1">{t('agents.subtitle')}</p>
        </div>
        <button
          onClick={handleCreateAgent}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          {t('agents.create')}
        </button>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder={t('agents.searchPlaceholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
              className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              title={viewMode === 'grid' ? t('common.listView') : t('common.gridView')}
            >
              {viewMode === 'grid' ? <List size={20} /> : <Grid size={20} />}
            </button>
            
            <button
              onClick={() => refetch()}
              className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              title={t('common.refresh')}
              disabled={isLoading}
            >
              <RefreshCw size={20} className={isLoading ? 'animate-spin' : ''} />
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-gray-400" />
            <span className="text-sm text-gray-600">{t('common.filters')}:</span>
          </div>
          
          <select
            value={filters.is_active?.toString() || ''}
            onChange={(e) => setFilters(prev => ({
              ...prev,
              is_active: e.target.value ? e.target.value === 'true' : undefined
            }))}
            className="text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="">{t('agents.allStatuses')}</option>
            <option value="true">{t('agents.active')}</option>
            <option value="false">{t('agents.inactive')}</option>
          </select>
          
          <select
            value={filters.is_public?.toString() || ''}
            onChange={(e) => setFilters(prev => ({
              ...prev,
              is_public: e.target.value ? e.target.value === 'true' : undefined
            }))}
            className="text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="">{t('agents.allVisibility')}</option>
            <option value="true">{t('agents.public')}</option>
            <option value="false">{t('agents.private')}</option>
          </select>
          
          <select
            value={filters.model || ''}
            onChange={(e) => setFilters(prev => ({
              ...prev,
              model: e.target.value || undefined
            }))}
            className="text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="">{t('agents.allModels')}</option>
            <option value="claude-3-sonnet">Claude 3 Sonnet</option>
            <option value="claude-3-haiku">Claude 3 Haiku</option>
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
          </select>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-500 border-t-transparent"></div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-600">{t('agents.loadError')}</p>
          <button
            onClick={() => refetch()}
            className="text-red-600 underline mt-2"
          >
            {t('common.tryAgain')}
          </button>
        </div>
      )}

      {/* Agents Grid/List */}
      {!isLoading && !error && (
        <>
          {filteredAgents.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <Plus size={48} className="mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {searchQuery ? t('agents.noResults') : t('agents.noAgents')}
              </h3>
              <p className="text-gray-600 mb-4">
                {searchQuery ? t('agents.noResultsDesc') : t('agents.noAgentsDesc')}
              </p>
              {!searchQuery && (
                <button
                  onClick={handleCreateAgent}
                  className="btn-primary"
                >
                  {t('agents.createFirst')}
                </button>
              )}
            </div>
          ) : (
            <motion.div
              className={viewMode === 'grid' 
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
                : 'space-y-4'
              }
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {filteredAgents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  onEdit={handleEditAgent}
                  onDelete={handleDeleteAgent}
                  onToggleStatus={handleToggleStatus}
                  onChat={handleChat}
                />
              ))}
            </motion.div>
          )}
        </>
      )}

      {/* Agent Form Modal */}
      <AgentForm
        agent={editingAgent}
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false)
          setEditingAgent(undefined)
        }}
        onSubmit={handleFormSubmit}
        isLoading={createAgentMutation.isPending || updateAgentMutation.isPending}
      />
    </div>
  )
}

export default AgentsList