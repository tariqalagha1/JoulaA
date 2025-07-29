import React from 'react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'

const DashboardPage: React.FC = () => {
  const { t } = useTranslation()
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">
            {t('dashboard.welcome')}
          </h1>
          {user && (
            <p className="text-lg text-secondary-600 mt-2">
              مرحباً {user.full_name_ar || user.full_name_en || user.username}
            </p>
          )}
        </div>
        <div className="flex items-center gap-4">
          {user && (
            <div className="text-right">
              <p className="font-medium">{user.full_name_ar || user.full_name_en || user.username}</p>
              <p className="text-sm text-secondary-600">{user.email}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="btn-secondary"
          >
            {t('auth.logout')}
          </button>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">
            {t('dashboard.overview')}
          </h3>
          <p className="text-secondary-600">
            نظرة عامة على نشاطك وأداء النظام
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">
            {t('agents.title')}
          </h3>
          <p className="text-secondary-600">
            إدارة الوكلاء الذكيون والذكاء الاصطناعي
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">
            {t('conversations.title')}
          </h3>
          <p className="text-secondary-600">
            المحادثات والتفاعلات مع النظام
          </p>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage