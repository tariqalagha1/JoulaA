import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import Layout from '../components/Layout/Layout'
import ConversationsList from '../components/Chat/ConversationsList'

const ConversationsPage: React.FC = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const handleSelectConversation = (conversationId: string) => {
    navigate(`/dashboard/chat/${conversationId}`)
  }

  const handleNewConversation = () => {
    navigate('/dashboard/chat')
  }



  return (
    <Layout>
      <div className="flex h-full">
        <ConversationsList
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
        />
        
        <div className="flex-1 flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {t('conversations.selectToView')}
            </h2>
            <p className="text-gray-600">
              {t('conversations.selectDescription')}
            </p>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default ConversationsPage