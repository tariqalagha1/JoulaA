import React from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

const HomePage: React.FC = () => {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-primary-900 mb-6">
            {t('dashboard.welcome')}
          </h1>
          <p className="text-xl text-secondary-600 mb-8">
            منصة جولة - المساعد الذكي للشركات العربية
          </p>
          <div className="flex justify-center gap-4">
            <Link to="/login" className="btn-primary">
              {t('auth.login')}
            </Link>
            <Link to="/register" className="btn-outline">
              {t('auth.register')}
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage