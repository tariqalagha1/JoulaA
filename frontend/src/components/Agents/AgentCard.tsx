import React from 'react'
import { useTranslation } from 'react-i18next'
import { Bot, Settings, Play, Pause, MoreVertical, Users, MessageSquare } from 'lucide-react'
import { Agent } from '../../services/agentService'
import { motion } from 'framer-motion'

interface AgentCardProps {
  agent: Agent
  onEdit: (agent: Agent) => void
  onDelete: (agentId: string) => void
  onToggleStatus: (agentId: string, isActive: boolean) => void
  onChat: (agent: Agent) => void
}

const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  onEdit,
  onDelete,
  onToggleStatus,
  onChat
}) => {
  const { t } = useTranslation()

  const handleToggleStatus = () => {
    onToggleStatus(agent.id, !agent.is_active)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${
            agent.is_active ? 'bg-primary-100 text-primary-600' : 'bg-gray-100 text-gray-400'
          }`}>
            <Bot size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{agent.name}</h3>
            <p className="text-sm text-gray-500">
              {agent.model || 'claude-3-sonnet'}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={handleToggleStatus}
            className={`p-1 rounded ${
              agent.is_active 
                ? 'text-green-600 hover:bg-green-50' 
                : 'text-gray-400 hover:bg-gray-50'
            }`}
            title={agent.is_active ? t('agents.pause') : t('agents.activate')}
          >
            {agent.is_active ? <Pause size={16} /> : <Play size={16} />}
          </button>
          
          <div className="relative group">
            <button className="p-1 rounded hover:bg-gray-50 text-gray-400">
              <MoreVertical size={16} />
            </button>
            <div className="absolute left-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg py-1 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
              <button
                onClick={() => onEdit(agent)}
                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2"
              >
                <Settings size={14} />
                {t('common.edit')}
              </button>
              <button
                onClick={() => onDelete(agent.id)}
                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 text-red-600 flex items-center gap-2"
              >
                {t('common.delete')}
              </button>
            </div>
          </div>
        </div>
      </div>

      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {agent.description || t('agents.noDescription')}
      </p>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-1">
            <Users size={14} />
            <span>{agent.is_public ? t('agents.public') : t('agents.private')}</span>
          </div>
          <div className="flex items-center gap-1">
            <MessageSquare size={14} />
            <span>0 {t('conversations.title')}</span>
          </div>
        </div>
        
        <button
          onClick={() => onChat(agent)}
          className="btn-primary text-sm px-4 py-2"
          disabled={!agent.is_active}
        >
          {t('agents.chat')}
        </button>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{t('common.created')}: {new Date(agent.created_at).toLocaleDateString('ar-SA')}</span>
          <span className={`px-2 py-1 rounded-full ${
            agent.is_active 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-600'
          }`}>
            {agent.is_active ? t('agents.active') : t('agents.inactive')}
          </span>
        </div>
      </div>
    </motion.div>
  )
}

export default AgentCard