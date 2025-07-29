import React from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

const NotFoundPage: React.FC = () => {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen flex items-center justify-center bg-secondary-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-primary-600 mb-4">404</h1>
        <h2 className="text-2xl font-semibold mb-4">
          {t('errors.notFound')}
        </h2>
        <p className="text-secondary-600 mb-8">
          الصفحة التي تبحث عنها غير موجودة
        </p>
        <Link to="/" className="btn-primary">
          {t('navigation.home')}
        </Link>
      </div>
    </div>
  )
}

export default NotFoundPage 