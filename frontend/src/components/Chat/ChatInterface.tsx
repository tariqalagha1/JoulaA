import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
// import { io, Socket } from 'socket.io-client' // Replaced with native WebSocket
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'
import { Bot, AlertCircle, RefreshCw } from 'lucide-react'

import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'
import { 
  conversationService, 
  Conversation, 
  Message, 
  ChatRequest 
} from '../../services/conversationService'
import { agentService, Agent } from '../../services/agentService'
import { useAuth } from '../../contexts/AuthContext'

interface ChatInterfaceProps {
  conversationId?: string
  agentId?: string
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  conversationId: propConversationId,
  agentId: propAgentId
}) => {
  const { t } = useTranslation()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const socketRef = useRef<WebSocket | null>(null)
  
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>(propConversationId)
  const [currentAgentId, setCurrentAgentId] = useState<string | undefined>(
    propAgentId || searchParams.get('agent') || undefined
  )
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingMessage, setStreamingMessage] = useState('')
  const [isConnected, setIsConnected] = useState(false)

  // Fetch conversation
  const {
    data: conversation,
    isLoading: conversationLoading,
    error: conversationError
  } = useQuery({
    queryKey: ['conversation', currentConversationId],
    queryFn: () => currentConversationId 
      ? conversationService.getConversation(currentConversationId, true)
      : null,
    enabled: !!currentConversationId,
  })

  // Fetch agent
  const {
    data: agent,
    isLoading: agentLoading
  } = useQuery({
    queryKey: ['agent', currentAgentId],
    queryFn: () => currentAgentId 
      ? agentService.getAgent(currentAgentId)
      : null,
    enabled: !!currentAgentId,
  })

  // Create conversation mutation
  const createConversationMutation = useMutation({
    mutationFn: (data: { agent_id?: string; initial_message?: string }) => 
      conversationService.createConversation(data),
    onSuccess: (newConversation) => {
      setCurrentConversationId(newConversation.id)
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    }
  })

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: (chatRequest: ChatRequest) => conversationService.chat(chatRequest),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['conversation', currentConversationId] })
      scrollToBottom()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || t('chat.sendError'))
      setIsStreaming(false)
    }
  })

  // WebSocket setup
  useEffect(() => {
    if (!user) return

    const token = localStorage.getItem('access_token')
    if (!token) return

    const wsUrl = (import.meta as any).env?.VITE_WS_URL || 'ws://localhost:8000'
    const socket = new WebSocket(`${wsUrl}/api/v1/ws/chat?token=${encodeURIComponent(token)}`)

    socketRef.current = socket

    socket.onopen = () => {
      setIsConnected(true)
      console.log('Connected to WebSocket')
    }

    socket.onclose = () => {
      setIsConnected(false)
      console.log('Disconnected from WebSocket')
    }

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        switch (data.type) {
          case 'connected':
            console.log('WebSocket connection confirmed:', data.message)
            break
            
          case 'message_chunk':
            if (data.conversation_id === currentConversationId) {
              setStreamingMessage(prev => prev + data.chunk)
            }
            break
            
          case 'message_complete':
            if (data.conversation_id === currentConversationId) {
              setIsStreaming(false)
              setStreamingMessage('')
              queryClient.invalidateQueries({ queryKey: ['conversation', currentConversationId] })
              scrollToBottom()
            }
            break
            
          case 'error':
            console.error('WebSocket error:', data.message)
            toast.error(data.message || t('chat.connectionError'))
            setIsStreaming(false)
            break
            
          default:
            console.log('Unknown WebSocket message type:', data.type)
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    socket.onerror = (error) => {
      console.error('WebSocket error:', error)
      toast.error(t('chat.connectionError'))
      setIsStreaming(false)
    }

    return () => {
      socket.close()
    }
  }, [user, currentConversationId, queryClient, t])

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [conversation?.messages, streamingMessage, scrollToBottom])

  const handleSendMessage = async (message: string, attachments?: File[]) => {
    if (!message.trim()) return

    try {
      let conversationId = currentConversationId
      
      // Create conversation if it doesn't exist
      if (!conversationId) {
        const newConversation = await createConversationMutation.mutateAsync({
          agent_id: currentAgentId,
          initial_message: message
        })
        conversationId = newConversation.id
      }

      setIsStreaming(true)
      setStreamingMessage('')

      // Send message via WebSocket for real-time streaming
      if (socketRef.current && isConnected && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({
          type: 'send_message',
          conversation_id: conversationId,
          message,
          agent_id: currentAgentId,
          attachments: attachments?.map(f => f.name) // TODO: Handle file uploads
        }))
      } else {
        // Fallback to HTTP API
        await sendMessageMutation.mutateAsync({
          message,
          conversation_id: conversationId,
          agent_id: currentAgentId,
          stream: false
        })
        setIsStreaming(false)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setIsStreaming(false)
    }
  }

  const handleRegenerate = () => {
    const messages = conversation?.messages || []
    const lastUserMessage = messages.filter((m: Message) => m.role === 'user').pop()
    if (lastUserMessage) {
      handleSendMessage(lastUserMessage.content)
    }
  }

  const handleFeedback = (messageId: string, feedback: 'positive' | 'negative') => {
    // TODO: Implement feedback API
    console.log('Feedback:', messageId, feedback)
  }

  const messages = conversation?.messages || []
  const isLoading = conversationLoading || agentLoading || sendMessageMutation.isPending

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-100 text-primary-600 rounded-lg">
            <Bot size={20} />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">
              {agent?.name || t('chat.defaultAgent')}
            </h2>
            <p className="text-sm text-gray-500">
              {agent?.description || t('chat.defaultAgentDesc')}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Connection status */}
          <div className={`w-2 h-2 rounded-full ${
            isConnected ? 'bg-green-500' : 'bg-red-500'
          }`} title={isConnected ? t('chat.connected') : t('chat.disconnected')} />
          
          {/* Refresh button */}
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['conversation', currentConversationId] })}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
            title={t('common.refresh')}
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {conversationError && (
          <div className="flex items-center justify-center p-8">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {t('chat.loadError')}
              </h3>
              <p className="text-gray-600 mb-4">{t('chat.loadErrorDesc')}</p>
              <button
                onClick={() => queryClient.invalidateQueries({ queryKey: ['conversation', currentConversationId] })}
                className="btn-primary"
              >
                {t('common.tryAgain')}
              </button>
            </div>
          </div>
        )}

        {!conversationError && (
          <>
            {messages.length === 0 && !isStreaming && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center max-w-md">
                  <div className="p-4 bg-primary-100 text-primary-600 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <Bot size={32} />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    {t('chat.welcome')}
                  </h3>
                  <p className="text-gray-600 mb-6">
                    {agent ? 
                      t('chat.welcomeWithAgent', { agentName: agent.name }) : 
                      t('chat.welcomeDefault')
                    }
                  </p>
                  <div className="text-sm text-gray-500">
                    {t('chat.suggestions')}:
                    <ul className="mt-2 space-y-1">
                      <li>• {t('chat.suggestion1')}</li>
                      <li>• {t('chat.suggestion2')}</li>
                      <li>• {t('chat.suggestion3')}</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            <div className="group">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  onRegenerate={message.role === 'assistant' ? handleRegenerate : undefined}
                  onFeedback={message.role === 'assistant' ? handleFeedback : undefined}
                />
              ))}
              
              {/* Streaming message */}
              {isStreaming && streamingMessage && (
                <ChatMessage
                  message={{
                    id: 'streaming',
                    conversation_id: currentConversationId || '',
                    content: streamingMessage,
                    role: 'assistant',
                    type: 'text',
                    created_at: new Date().toISOString()
                  }}
                  isStreaming={true}
                />
              )}
              
              {/* Loading indicator */}
              {isStreaming && !streamingMessage && (
                <div className="flex gap-4 p-4 bg-gray-50">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary-100 text-secondary-600 flex items-center justify-center">
                    <Bot size={16} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                      <span className="text-sm text-gray-500">{t('chat.thinking')}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading || isStreaming}
        disabled={!!conversationError}
        placeholder={agent ? 
          t('chat.inputPlaceholderWithAgent', { agentName: agent.name }) : 
          t('chat.inputPlaceholder')
        }
      />
    </div>
  )
}

export default ChatInterface