import React from 'react'
import { useTranslation } from 'react-i18next'
import Layout from '../components/Layout/Layout'
import AgentsList from '../components/Agents/AgentsList'

const AgentsPage: React.FC = () => {
  const { t } = useTranslation()

  return (
    <Layout>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {t('agents.title')}
          </h1>
          <p className="text-gray-600">
            {t('agents.description')}
          </p>
        </div>
        
        <AgentsList />
      </div>
    </Layout>

  )
}

export default AgentsPage