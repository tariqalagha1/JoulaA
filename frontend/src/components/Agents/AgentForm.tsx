import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X, Bot, Settings, Brain, Zap } from 'lucide-react'
import { Agent, AgentCreate, AgentUpdate } from '../../services/agentService'
import { motion } from 'framer-motion'

const agentSchema = z.object({
  name: z.string().min(1, 'Agent name is required'),
  description: z.string().optional(),
  instructions: z.string().optional(),
  model: z.string().optional(),
  temperature: z.number().min(0).max(2).optional(),
  max_tokens: z.number().min(1).max(4000).optional(),
  is_active: z.boolean().optional(),
  is_public: z.boolean().optional(),
})

type AgentFormData = z.infer<typeof agentSchema>

interface AgentFormProps {
  agent?: Agent
  isOpen: boolean
  onClose: () => void
  onSubmit: (data: AgentCreate | AgentUpdate) => Promise<void>
  isLoading?: boolean
}

const AgentForm: React.FC<AgentFormProps> = ({
  agent,
  isOpen,
  onClose,
  onSubmit,
  isLoading = false
}) => {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState('basic')

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isValid }
  } = useForm<AgentFormData>({
    resolver: zodResolver(agentSchema),
    defaultValues: {
      name: '',
      description: '',
      instructions: '',
      model: 'claude-3-sonnet',
      temperature: 0.7,
      max_tokens: 1000,
      is_active: true,
      is_public: false,
    }
  })

  useEffect(() => {
    if (agent) {
      reset({
        name: agent.name,
        description: agent.description || '',
        instructions: agent.instructions || '',
        model: agent.model || 'claude-3-sonnet',
        temperature: agent.temperature || 0.7,
        max_tokens: agent.max_tokens || 1000,
        is_active: agent.is_active,
        is_public: agent.is_public,
      })
    } else {
      reset({
        name: '',
        description: '',
        instructions: '',
        model: 'claude-3-sonnet',
        temperature: 0.7,
        max_tokens: 1000,
        is_active: true,
        is_public: false,
      })
    }
  }, [agent, reset])

  const handleFormSubmit = async (data: AgentFormData) => {
    await onSubmit(data)
    onClose()
  }

  if (!isOpen) return null

  const models = [
    { value: 'claude-3-sonnet', label: 'Claude 3 Sonnet' },
    { value: 'claude-3-haiku', label: 'Claude 3 Haiku' },
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  ]

  const tabs = [
    { id: 'basic', label: t('agents.form.basicInfo'), icon: Bot },
    { id: 'advanced', label: t('agents.form.advanced'), icon: Settings },
    { id: 'instructions', label: t('agents.form.instructions'), icon: Brain },
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden"
      >
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold">
            {agent ? t('agents.form.editAgent') : t('agents.form.createAgent')}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex border-b border-gray-200">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon size={16} />
                {tab.label}
              </button>
            )
          })}
        </div>

        <form onSubmit={handleSubmit(handleFormSubmit)} className="p-6 overflow-y-auto max-h-[60vh]">
          {activeTab === 'basic' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('agents.form.name')} *
                </label>
                <input
                  {...register('name')}
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder={t('agents.form.namePlaceholder')}
                />
                {errors.name && (
                  <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('agents.form.description')}
                </label>
                <textarea
                  {...register('description')}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder={t('agents.form.descriptionPlaceholder')}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('agents.form.model')}
                </label>
                <select
                  {...register('model')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  {models.map((model) => (
                    <option key={model.value} value={model.value}>
                      {model.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2">
                  <input
                    {...register('is_active')}
                    type="checkbox"
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">{t('agents.form.isActive')}</span>
                </label>

                <label className="flex items-center gap-2">
                  <input
                    {...register('is_public')}
                    type="checkbox"
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">{t('agents.form.isPublic')}</span>
                </label>
              </div>
            </div>
          )}

          {activeTab === 'advanced' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('agents.form.temperature')}
                </label>
                <input
                  {...register('temperature', { valueAsNumber: true })}
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>0 (Conservative)</span>
                  <span>{watch('temperature')}</span>
                  <span>2 (Creative)</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {t('agents.form.maxTokens')}
                </label>
                <input
                  {...register('max_tokens', { valueAsNumber: true })}
                  type="number"
                  min="1"
                  max="4000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {t('agents.form.maxTokensHelp')}
                </p>
              </div>
            </div>
          )}

          {activeTab === 'instructions' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('agents.form.instructions')}
              </label>
              <textarea
                {...register('instructions')}
                rows={10}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder={t('agents.form.instructionsPlaceholder')}
              />
              <p className="text-xs text-gray-500 mt-1">
                {t('agents.form.instructionsHelp')}
              </p>
            </div>
          )}
        </form>

        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onClose}
            className="btn-secondary"
            disabled={isLoading}
          >
            {t('common.cancel')}
          </button>
          <button
            onClick={handleSubmit(handleFormSubmit)}
            disabled={!isValid || isLoading}
            className="btn-primary flex items-center gap-2"
          >
            {isLoading && <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />}
            {agent ? t('common.update') : t('common.create')}
          </button>
        </div>
      </motion.div>
    </div>
  )
}

export default AgentForm