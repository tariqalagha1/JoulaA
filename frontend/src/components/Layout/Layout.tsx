import React from 'react'
import { useTranslation } from 'react-i18next'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-secondary-50">
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold text-primary-600">
              جولة
            </h1>
            <nav className="flex items-center space-x-4 space-x-reverse">
              <button className="text-secondary-600 hover:text-primary-600">
                {t('navigation.profile')}
              </button>
              <button className="text-secondary-600 hover:text-primary-600">
                {t('navigation.settings')}
              </button>
              <button className="text-secondary-600 hover:text-primary-600">
                {t('auth.logout')}
              </button>
            </nav>
          </div>
        </div>
      </header>
      <main className="flex-1">
        {children}
      </main>
    </div>
  )
}

export default Layout 