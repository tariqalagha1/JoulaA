import React from 'react'
import { useTranslation } from 'react-i18next'
import AgentStudio from '../components/AgentStudio/AgentStudio'

const AgentStudioPage: React.FC = () => {
  const { t } = useTranslation()

  return (
    <div className="h-screen">
      <AgentStudio />
    </div>
  )
}

export default AgentStudioPage