import React from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import { 
  Home, 
  Bot, 
  MessageSquare, 
  Settings, 
  BarChart3, 
  Users, 
  Palette,
  Building2,
  CreditCard
} from 'lucide-react'

// Import page components
import DashboardOverview from '../components/Dashboard/DashboardOverview'
import AgentsList from '../components/Agents/AgentsList'
import ChatInterface from '../components/Chat/ChatInterface'
import AgentStudioPage from './AgentStudioPage'
import ConversationsPage from './ConversationsPage'
import AgentsPage from './AgentsPage'
import IntegrationsPage from './IntegrationsPage'
import OrganizationSettings from './OrganizationSettings'

const DashboardPage: React.FC = () => {
  const { t } = useTranslation()
  const { user, logout } = useAuth()
  const location = useLocation()

  const handleLogout = async () => {
    await logout()
  }

  const navigation = [
    { name: 'نظرة عامة', href: '/dashboard', icon: Home, current: location.pathname === '/dashboard' },
    { name: 'الوكلاء', href: '/dashboard/agents', icon: Bot, current: location.pathname.startsWith('/dashboard/agents') },
    { name: 'استوديو الوكلاء', href: '/dashboard/agent-studio', icon: Palette, current: location.pathname === '/dashboard/agent-studio' },
    { name: 'المحادثات', href: '/dashboard/conversations', icon: MessageSquare, current: location.pathname.startsWith('/dashboard/conversations') },
    { name: 'الدردشة', href: '/dashboard/chat', icon: MessageSquare, current: location.pathname === '/dashboard/chat' },
    { name: 'التكاملات', href: '/dashboard/integrations', icon: Settings, current: location.pathname === '/dashboard/integrations' },
    { name: 'التحليلات', href: '/dashboard/analytics', icon: BarChart3, current: location.pathname === '/dashboard/analytics' },
    { name: 'المؤسسة', href: '/dashboard/organization', icon: Building2, current: location.pathname === '/dashboard/organization' },
  ]

  return (
    <div className="flex h-screen bg-secondary-50">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-sm border-r border-secondary-200">
        <div className="p-6">
          <h1 className="text-xl font-bold text-primary-600">جولة</h1>
        </div>
        <nav className="mt-6">
          <div className="px-3">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 ${
                    item.current
                      ? 'bg-primary-50 text-primary-600 border-r-2 border-primary-600'
                      : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900'
                  }`}
                >
                  <Icon className="ml-3 h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </nav>
        
        {/* User info and logout */}
        <div className="absolute bottom-0 w-64 p-4 border-t border-secondary-200">
          {user && (
            <div className="flex items-center">
              <div className="flex-1">
                <p className="text-sm font-medium text-secondary-900">
                  {user.full_name_ar || user.full_name_en || user.username}
                </p>
                <p className="text-xs text-secondary-500">{user.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="text-xs text-secondary-500 hover:text-secondary-700"
              >
                خروج
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto">
        <Routes>
          <Route index element={<DashboardOverview />} />
          <Route path="agents" element={<AgentsPage />} />
          <Route path="agent-studio" element={<AgentStudioPage />} />
          <Route path="conversations" element={<ConversationsPage />} />
          <Route path="chat" element={<ChatInterface />} />
          <Route path="integrations" element={<IntegrationsPage />} />
          <Route path="organization" element={<OrganizationSettings />} />
          <Route path="analytics" element={<div className="p-6"><h1 className="text-2xl font-bold">التحليلات - قريباً</h1></div>} />
        </Routes>
      </div>
    </div>
  )
}

export default DashboardPage