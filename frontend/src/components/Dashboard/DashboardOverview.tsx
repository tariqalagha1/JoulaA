import React from 'react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../../contexts/AuthContext'
import { Link } from 'react-router-dom'
import {
  Bot,
  MessageSquare,
  Users,
  BarChart3,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus
} from 'lucide-react'

const DashboardOverview: React.FC = () => {
  const { t } = useTranslation()
  const { user } = useAuth()

  // Mock data for dashboard stats
  const stats = [
    {
      name: 'إجمالي الوكلاء',
      value: '12',
      change: '+2',
      changeType: 'increase',
      icon: Bot,
      href: '/dashboard/agents'
    },
    {
      name: 'المحادثات النشطة',
      value: '48',
      change: '+12%',
      changeType: 'increase',
      icon: MessageSquare,
      href: '/dashboard/conversations'
    },
    {
      name: 'المستخدمون',
      value: '156',
      change: '+8',
      changeType: 'increase',
      icon: Users,
      href: '/dashboard/organization'
    },
    {
      name: 'معدل النجاح',
      value: '94%',
      change: '+2%',
      changeType: 'increase',
      icon: BarChart3,
      href: '/dashboard/analytics'
    }
  ]

  const recentActivities = [
    {
      id: 1,
      type: 'agent_created',
      message: 'تم إنشاء وكيل جديد: مساعد خدمة العملاء',
      time: 'منذ ساعتين',
      icon: Bot,
      status: 'success'
    },
    {
      id: 2,
      type: 'conversation_completed',
      message: 'تم إكمال 15 محادثة بنجاح',
      time: 'منذ 4 ساعات',
      icon: CheckCircle,
      status: 'success'
    },
    {
      id: 3,
      type: 'integration_warning',
      message: 'تحذير: بطء في الاستجابة من API الخارجي',
      time: 'منذ 6 ساعات',
      icon: AlertCircle,
      status: 'warning'
    }
  ]

  return (
    <div className="p-6">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-secondary-900">
          {t('dashboard.welcome')}
        </h1>
        {user && (
          <p className="text-lg text-secondary-600 mt-2">
            مرحباً {user.full_name_ar || user.full_name_en || user.username}
          </p>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Link
              key={stat.name}
              to={stat.href}
              className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-secondary-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-secondary-900 mt-1">{stat.value}</p>
                  <div className="flex items-center mt-2">
                    <TrendingUp className="h-4 w-4 text-green-500 ml-1" />
                    <span className="text-sm text-green-600">{stat.change}</span>
                  </div>
                </div>
                <div className="p-3 bg-primary-50 rounded-lg">
                  <Icon className="h-6 w-6 text-primary-600" />
                </div>
              </div>
            </Link>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
          <h2 className="text-lg font-semibold text-secondary-900 mb-4">إجراءات سريعة</h2>
          <div className="space-y-3">
            <Link
              to="/dashboard/agent-studio"
              className="flex items-center p-3 rounded-lg border border-secondary-200 hover:bg-secondary-50 transition-colors"
            >
              <div className="p-2 bg-primary-50 rounded-lg ml-3">
                <Plus className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <p className="font-medium text-secondary-900">إنشاء وكيل جديد</p>
                <p className="text-sm text-secondary-600">استخدم استوديو الوكلاء لبناء وكيل ذكي</p>
              </div>
            </Link>
            <Link
              to="/dashboard/chat"
              className="flex items-center p-3 rounded-lg border border-secondary-200 hover:bg-secondary-50 transition-colors"
            >
              <div className="p-2 bg-green-50 rounded-lg ml-3">
                <MessageSquare className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="font-medium text-secondary-900">بدء محادثة جديدة</p>
                <p className="text-sm text-secondary-600">تفاعل مع الوكلاء الذكيين</p>
              </div>
            </Link>
            <Link
              to="/dashboard/integrations"
              className="flex items-center p-3 rounded-lg border border-secondary-200 hover:bg-secondary-50 transition-colors"
            >
              <div className="p-2 bg-blue-50 rounded-lg ml-3">
                <BarChart3 className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="font-medium text-secondary-900">إعداد التكاملات</p>
                <p className="text-sm text-secondary-600">ربط الأنظمة الخارجية</p>
              </div>
            </Link>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
          <h2 className="text-lg font-semibold text-secondary-900 mb-4">النشاط الأخير</h2>
          <div className="space-y-4">
            {recentActivities.map((activity) => {
              const Icon = activity.icon
              return (
                <div key={activity.id} className="flex items-start">
                  <div className={`p-2 rounded-lg ml-3 ${
                    activity.status === 'success' ? 'bg-green-50' :
                    activity.status === 'warning' ? 'bg-yellow-50' : 'bg-red-50'
                  }`}>
                    <Icon className={`h-4 w-4 ${
                      activity.status === 'success' ? 'text-green-600' :
                      activity.status === 'warning' ? 'text-yellow-600' : 'text-red-600'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-secondary-900">{activity.message}</p>
                    <div className="flex items-center mt-1">
                      <Clock className="h-3 w-3 text-secondary-400 ml-1" />
                      <span className="text-xs text-secondary-500">{activity.time}</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardOverview