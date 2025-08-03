import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { MessageSquare, Bot, Settings } from 'lucide-react'
import { motion } from 'framer-motion'

import Layout from '../components/Layout/Layout'
import ConversationsList from '../components/Chat/ConversationsList'
import ChatInterface from '../components/Chat/ChatInterface'
import { conversationService } from '../services/conversationService'
import { agentService } from '../services/agentService'

const ChatPage: React.FC = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { conversationId } = useParams<{ conversationId?: string }>()
  const [selectedConversationId, setSelectedConversationId] = useState<string | undefined>(conversationId)
  const [selectedAgentId, setSelectedAgentId] = useState<string | undefined>()
  const [showAgentSelector, setShowAgentSelector] = useState(false)

  // Fetch conversation details when selected
  const { data: conversation } = useQuery({
    queryKey: ['conversation', selectedConversationId],
    queryFn: () => conversationService.getConversation(selectedConversationId!),
    enabled: !!selectedConversationId,
  })

  // Fetch agents for selection
  const { data: agentsData } = useQuery({
    queryKey: ['agents', 'active'],
    queryFn: () => agentService.listAgents({
      is_active: true,
      page_size: 50
    })
  })

  useEffect(() => {
    if (conversationId && conversationId !== selectedConversationId) {
      setSelectedConversationId(conversationId)
    }
  }, [conversationId, selectedConversationId])

  useEffect(() => {
    if (conversation?.agent_id) {
      setSelectedAgentId(conversation.agent_id)
    }
  }, [conversation])

  const handleSelectConversation = (id: string) => {
    setSelectedConversationId(id)
    navigate(`/dashboard/chat/${id}`)
  }

  const handleNewConversation = () => {
    setSelectedConversationId(undefined)
    setSelectedAgentId(undefined)
    setShowAgentSelector(true)
    navigate('/dashboard/chat')
  }

  const handleAgentSelect = (agentId: string) => {
    setSelectedAgentId(agentId)
    setShowAgentSelector(false)
  }

  const agents = agentsData?.agents || []
  const selectedAgent = agents.find(agent => agent.id === selectedAgentId)

  return (
    <Layout>
      <div className="flex h-full bg-gray-50">
        {/* Conversations Sidebar */}
        <ConversationsList
          selectedConversationId={selectedConversationId}
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
        />

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {selectedConversationId ? (
            <>
              {/* Chat Header */}
              <div className="bg-white border-b border-gray-200 px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <Bot size={16} className="text-primary-600" />
                    </div>
                    <div>
                      <h1 className="text-lg font-semibold text-gray-900">
                        {conversation?.title || t('chat.conversation')}
                      </h1>
                      {selectedAgent && (
                        <p className="text-sm text-gray-500">
                          {t('chat.poweredBy')} {selectedAgent.name}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setShowAgentSelector(true)}
                      className="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
                      title={t('chat.changeAgent')}
                    >
                      <Settings size={18} />
                    </button>
                  </div>
                </div>
              </div>

              {/* Chat Interface */}
              <ChatInterface
                conversationId={selectedConversationId}
                agentId={selectedAgentId}
              />
            </>
          ) : (
            /* Welcome Screen */
            <div className="flex-1 flex items-center justify-center">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center max-w-md mx-auto px-6"
              >
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <MessageSquare size={32} className="text-primary-600" />
                </div>
                
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  {t('chat.welcome.title')}
                </h2>
                
                <p className="text-gray-600 mb-8">
                  {t('chat.welcome.description')}
                </p>

                {showAgentSelector ? (
                  /* Agent Selection */
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      {t('chat.selectAgent')}
                    </h3>
                    
                    <div className="grid gap-3 max-h-64 overflow-y-auto">
                      <button
                        onClick={() => handleAgentSelect('')}
                        className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-all text-left"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                            <MessageSquare size={20} className="text-gray-600" />
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-900">
                              {t('chat.generalAssistant')}
                            </h4>
                            <p className="text-sm text-gray-500">
                              {t('chat.generalAssistantDesc')}
                            </p>
                          </div>
                        </div>
                      </button>
                      
                      {agents.map((agent) => (
                        <button
                          key={agent.id}
                          onClick={() => handleAgentSelect(agent.id)}
                          className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-all text-left"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                              <Bot size={20} className="text-primary-600" />
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900">
                                {agent.name}
                              </h4>
                              {agent.description && (
                                <p className="text-sm text-gray-500 line-clamp-2">
                                  {agent.description}
                                </p>
                              )}
                              <div className="flex items-center gap-2 mt-1">
                                <span className="text-xs px-2 py-1 bg-gray-100 rounded-full">
                                  {agent.model}
                                </span>
                                {agent.is_public && (
                                  <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full">
                                    {t('agents.public')}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                    
                    <button
                      onClick={() => setShowAgentSelector(false)}
                      className="text-gray-500 text-sm hover:text-gray-700 transition-colors"
                    >
                      {t('common.cancel')}
                    </button>
                  </div>
                ) : (
                  /* Start Chat Button */
                  <button
                    onClick={() => setShowAgentSelector(true)}
                    className="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors font-medium"
                  >
                    {t('chat.startNewChat')}
                  </button>
                )}
              </motion.div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default ChatPage