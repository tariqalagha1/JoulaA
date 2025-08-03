import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { MessageSquare, Plus, Search, MoreVertical, Archive, Trash2, Edit3 } from 'lucide-react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'

import { 
  conversationService, 
  Conversation, 
  ConversationCreate 
} from '../../services/conversationService'
import { agentService } from '../../services/agentService'

interface ConversationsListProps {
  selectedConversationId?: string
  onSelectConversation: (conversationId: string) => void
  onNewConversation: () => void
}

const ConversationsList: React.FC<ConversationsListProps> = ({
  selectedConversationId,
  onSelectConversation,
  onNewConversation
}) => {
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [editingTitle, setEditingTitle] = useState<string | null>(null)
  const [newTitle, setNewTitle] = useState('')

  // Fetch conversations
  const {
    data: conversationsData,
    isLoading,
    error
  } = useQuery({
    queryKey: ['conversations', searchQuery],
    queryFn: () => conversationService.listConversations({
      query: searchQuery || undefined,
      sort_by: 'last_message_at',
      sort_order: 'desc',
      page: 1,
      page_size: 50
    }),
    staleTime: 10000, // 10 seconds
  })

  // Fetch agents for new conversation
  const { data: agentsData } = useQuery({
    queryKey: ['agents', 'active'],
    queryFn: () => agentService.listAgents({
      is_active: true,
      page_size: 20
    })
  })

  // Create conversation mutation
  const createConversationMutation = useMutation({
    mutationFn: (data: ConversationCreate) => conversationService.createConversation(data),
    onSuccess: (newConversation) => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      onSelectConversation(newConversation.id)
      toast.success(t('conversations.createSuccess'))
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || t('conversations.createError'))
    }
  })

  // Update conversation mutation
  const updateConversationMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => 
      conversationService.updateConversation(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      setEditingTitle(null)
      toast.success(t('conversations.updateSuccess'))
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || t('conversations.updateError'))
    }
  })

  // Delete conversation mutation
  const deleteConversationMutation = useMutation({
    mutationFn: (conversationId: string) => conversationService.deleteConversation(conversationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      toast.success(t('conversations.deleteSuccess'))
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || t('conversations.deleteError'))
    }
  })

  const handleCreateConversation = (agentId?: string) => {
    createConversationMutation.mutate({
      agent_id: agentId,
      title: t('conversations.newConversation')
    })
  }

  const handleEditTitle = (conversation: Conversation) => {
    setEditingTitle(conversation.id)
    setNewTitle(conversation.title || '')
  }

  const handleSaveTitle = (conversationId: string) => {
    if (newTitle.trim()) {
      updateConversationMutation.mutate({
        id: conversationId,
        data: { title: newTitle.trim() }
      })
    } else {
      setEditingTitle(null)
    }
  }

  const handleDeleteConversation = (conversationId: string) => {
    if (window.confirm(t('conversations.deleteConfirm'))) {
      deleteConversationMutation.mutate(conversationId)
    }
  }

  const handleArchiveConversation = (conversationId: string) => {
    updateConversationMutation.mutate({
      id: conversationId,
      data: { status: 'archived' }
    })
  }

  const conversations = conversationsData?.conversations || []
  const agents = agentsData?.agents || []

  const formatLastMessage = (conversation: Conversation) => {
    if (!conversation.last_message_at) return t('conversations.noMessages')
    
    const date = new Date(conversation.last_message_at)
    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' })
    } else if (diffInHours < 24 * 7) {
      return date.toLocaleDateString('ar-SA', { weekday: 'short' })
    } else {
      return date.toLocaleDateString('ar-SA', { month: 'short', day: 'numeric' })
    }
  }

  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {t('conversations.title')}
          </h2>
          <div className="relative group">
            <button
              onClick={onNewConversation}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
              title={t('conversations.new')}
            >
              <Plus size={20} />
            </button>
            
            {/* Quick agent selection */}
            {agents.length > 0 && (
              <div className="absolute right-0 top-10 bg-white border border-gray-200 rounded-lg shadow-lg py-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 min-w-48">
                <div className="px-3 py-2 text-xs text-gray-500 border-b border-gray-100">
                  {t('conversations.selectAgent')}
                </div>
                <button
                  onClick={() => handleCreateConversation()}
                  className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
                >
                  <MessageSquare size={14} />
                  {t('conversations.generalChat')}
                </button>
                {agents.slice(0, 5).map((agent) => (
                  <button
                    key={agent.id}
                    onClick={() => handleCreateConversation(agent.id)}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
                  >
                    <div className="w-3 h-3 bg-primary-100 rounded-full"></div>
                    {agent.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
          <input
            type="text"
            placeholder={t('conversations.search')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary-500 border-t-transparent"></div>
          </div>
        )}

        {error && (
          <div className="p-4 text-center">
            <p className="text-red-600 text-sm">{t('conversations.loadError')}</p>
          </div>
        )}

        {!isLoading && !error && conversations.length === 0 && (
          <div className="p-4 text-center">
            <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">
              {searchQuery ? t('conversations.noResults') : t('conversations.noConversations')}
            </p>
            {!searchQuery && (
              <button
                onClick={onNewConversation}
                className="text-primary-600 text-sm mt-2 hover:underline"
              >
                {t('conversations.startFirst')}
              </button>
            )}
          </div>
        )}

        {conversations.map((conversation) => (
          <motion.div
            key={conversation.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`group relative border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
              selectedConversationId === conversation.id ? 'bg-primary-50 border-primary-200' : ''
            }`}
            onClick={() => onSelectConversation(conversation.id)}
          >
            <div className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {editingTitle === conversation.id ? (
                    <input
                      type="text"
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      onBlur={() => handleSaveTitle(conversation.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveTitle(conversation.id)
                        if (e.key === 'Escape') setEditingTitle(null)
                      }}
                      className="w-full text-sm font-medium bg-transparent border-none outline-none focus:ring-0 p-0"
                      autoFocus
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {conversation.title || t('conversations.untitled')}
                    </h3>
                  )}
                  
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-gray-500">
                      {conversation.message_count} {t('conversations.messages')}
                    </span>
                    <span className="text-xs text-gray-400">•</span>
                    <span className="text-xs text-gray-500">
                      {formatLastMessage(conversation)}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleEditTitle(conversation)
                    }}
                    className="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors"
                    title={t('conversations.editTitle')}
                  >
                    <Edit3 size={12} />
                  </button>
                  
                  <div className="relative group/menu">
                    <button
                      onClick={(e) => e.stopPropagation()}
                      className="p-1 text-gray-400 hover:text-gray-600 rounded transition-colors"
                    >
                      <MoreVertical size={12} />
                    </button>
                    
                    <div className="absolute right-0 top-6 bg-white border border-gray-200 rounded-lg shadow-lg py-1 opacity-0 invisible group-hover/menu:opacity-100 group-hover/menu:visible transition-all z-20">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleArchiveConversation(conversation.id)
                        }}
                        className="w-full px-3 py-2 text-left text-xs hover:bg-gray-50 flex items-center gap-2"
                      >
                        <Archive size={12} />
                        {t('conversations.archive')}
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteConversation(conversation.id)
                        }}
                        className="w-full px-3 py-2 text-left text-xs hover:bg-gray-50 text-red-600 flex items-center gap-2"
                      >
                        <Trash2 size={12} />
                        {t('conversations.delete')}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              {conversation.status === 'archived' && (
                <div className="mt-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-600">
                    <Archive size={10} className="mr-1" />
                    {t('conversations.archived')}
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default ConversationsList