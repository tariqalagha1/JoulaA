import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Building2,
  Users,
  Settings,
  CreditCard,
  Shield,
  Mail,
  Plus,
  Edit,
  Trash2,
  Crown,
  UserCheck,
  UserX,
  Upload,
  Download,
  Save,
  AlertCircle,
  CheckCircle,
  Clock,
  MoreVertical
} from 'lucide-react'
import { organizationService, Organization, OrganizationMember } from '../services/organizationService'
import toast from 'react-hot-toast'

interface OrganizationStats {
  total_members: number
  active_members: number
  pending_invitations: number
  storage_used: number
  storage_limit: number
  api_calls_this_month: number
  api_calls_limit: number
}

interface Subscription {
  id: string
  plan_name: string
  status: 'active' | 'cancelled' | 'past_due'
  current_period_start: string
  current_period_end: string
  amount: number
  currency: string
}

const OrganizationSettings: React.FC = () => {
  const { t } = useTranslation()
  const [organization, setOrganization] = useState<Organization | null>(null)
  const [members, setMembers] = useState<OrganizationMember[]>([])
  const [stats, setStats] = useState<OrganizationStats | null>(null)
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState('general')
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('member')
  const [showInviteForm, setShowInviteForm] = useState(false)
  const [editingOrg, setEditingOrg] = useState(false)
  const [orgForm, setOrgForm] = useState({
    name: '',
    description: '',
    website: '',
    industry: ''
  })

  useEffect(() => {
    loadOrganizationData()
  }, [])

  const loadOrganizationData = async () => {
    try {
      setLoading(true)
      // This would typically load the current user's organization
      // For now, we'll simulate the API calls
      const mockOrg: Organization = {
        id: '1',
        name_ar: 'شركة أكمي',
        name_en: 'Acme Corporation',
        description_ar: 'شركة تكنولوجيا رائدة في منطقة الشرق الأوسط وشمال أفريقيا',
        description_en: 'Leading technology company in the MENA region',
        website: 'https://acme.com',
        industry: 'technology',
        logo_url: '',
        subscription_plan: 'professional',
        subscription_status: 'active',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      }
      setOrganization(mockOrg)
      setOrgForm({
        name: mockOrg.name_en || mockOrg.name_ar,
        description: mockOrg.description_en || mockOrg.description_ar || '',
        website: mockOrg.website || '',
        industry: mockOrg.industry || ''
      })

      const mockMembers: OrganizationMember[] = [
        {
          id: '1',
          user_id: '1',
          organization_id: '1',
          role: 'owner',
          is_active: true,
          user: {
            id: '1',
            username: 'admin',
            email: 'admin@acme.com',
            full_name_en: 'Admin User',
            full_name_ar: 'المدير العام'
          },
          joined_at: '2024-01-01T00:00:00Z'
        },
        {
          id: '2',
          user_id: '2',
          organization_id: '1',
          role: 'admin',
          is_active: true,
          user: {
            id: '2',
            username: 'manager',
            email: 'manager@acme.com',
            full_name_en: 'Manager User',
            full_name_ar: 'مدير القسم'
          },
          joined_at: '2024-01-02T00:00:00Z'
        }
      ]
      setMembers(mockMembers)

      const mockStats: OrganizationStats = {
        total_members: 15,
        active_members: 12,
        pending_invitations: 3,
        storage_used: 2.5,
        storage_limit: 10,
        api_calls_this_month: 8500,
        api_calls_limit: 10000
      }
      setStats(mockStats)

      const mockSubscription: Subscription = {
        id: '1',
        plan_name: 'Professional',
        status: 'active',
        current_period_start: '2024-01-01T00:00:00Z',
        current_period_end: '2024-02-01T00:00:00Z',
        amount: 99,
        currency: 'USD'
      }
      setSubscription(mockSubscription)
    } catch (error) {
      toast.error(t('organization.loadError'))
    } finally {
      setLoading(false)
    }
  }

  const handleSaveOrganization = async () => {
    if (!organization) return

    try {
      setSaving(true)
      const updatedOrg = await organizationService.updateOrganization(organization.id, orgForm)
      setOrganization(updatedOrg)
      setEditingOrg(false)
      toast.success(t('organization.saveSuccess'))
    } catch (error) {
      toast.error(t('organization.saveError'))
    } finally {
      setSaving(false)
    }
  }

  const handleInviteMember = async () => {
    if (!inviteEmail.trim()) {
      toast.error(t('organization.emailRequired'))
      return
    }

    try {
      setSaving(true)
      await organizationService.inviteUser(organization!.id, {
        email: inviteEmail,
        role: inviteRole as 'admin' | 'member'
      })
      toast.success(t('organization.inviteSuccess'))
      setInviteEmail('')
      setInviteRole('member')
      setShowInviteForm(false)
      loadOrganizationData()
    } catch (error) {
      toast.error(t('organization.inviteError'))
    } finally {
      setSaving(false)
    }
  }

  const handleRemoveMember = async (memberId: string) => {
    if (!confirm(t('organization.confirmRemoveMember'))) return

    try {
      await organizationService.removeMember(organization!.id, memberId)
      toast.success(t('organization.memberRemoved'))
      loadOrganizationData()
    } catch (error) {
      toast.error(t('organization.removeError'))
    }
  }

  const handleUpdateMemberRole = async (memberId: string, newRole: 'admin' | 'member') => {
    try {
      await organizationService.updateMember(organization!.id, memberId, { role: newRole })
      toast.success(t('organization.roleUpdated'))
      loadOrganizationData()
    } catch (error) {
      toast.error(t('organization.roleUpdateError'))
    }
  }

  const handleLogoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (file.size > 5 * 1024 * 1024) {
      toast.error(t('organization.logoTooLarge'))
      return
    }

    try {
      setSaving(true)
      const response = await organizationService.uploadLogo(organization!.id, file)
      setOrganization(prev => prev ? { ...prev, logo_url: response.logo_url } : null)
      toast.success(t('organization.logoUploaded'))
    } catch (error) {
      toast.error(t('organization.logoUploadError'))
    } finally {
      setSaving(false)
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'owner':
        return <Crown className="h-4 w-4 text-yellow-500" />
      case 'admin':
        return <Shield className="h-4 w-4 text-blue-500" />
      default:
        return <Users className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-500'
      case 'pending':
        return 'text-yellow-500'
      case 'inactive':
        return 'text-red-500'
      default:
        return 'text-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4" />
      case 'pending':
        return <Clock className="h-4 w-4" />
      case 'inactive':
        return <AlertCircle className="h-4 w-4" />
      default:
        return <AlertCircle className="h-4 w-4" />
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (!organization) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
            {t('organization.loadError')}
          </h3>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center space-x-4">
              {organization.logo_url ? (
                <img
                  className="h-12 w-12 rounded-lg object-cover"
                  src={organization.logo_url}
                  alt={organization.name_en || organization.name_ar}
                />
              ) : (
                <div className="h-12 w-12 rounded-lg bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                  <Building2 className="h-6 w-6 text-gray-500 dark:text-gray-400" />
                </div>
              )}
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {organization.name_en || organization.name_ar}
                </h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {t('organization.settings')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="lg:grid lg:grid-cols-12 lg:gap-x-5">
          {/* Sidebar */}
          <aside className="py-6 px-2 sm:px-6 lg:py-0 lg:px-0 lg:col-span-3">
            <nav className="space-y-1">
              <button
                onClick={() => setActiveTab('general')}
                className={`group rounded-md px-3 py-2 flex items-center text-sm font-medium w-full text-left ${
                  activeTab === 'general'
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                    : 'text-gray-900 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <Settings className="flex-shrink-0 -ml-1 mr-3 h-6 w-6" />
                <span className="truncate">{t('organization.tabs.general')}</span>
              </button>

              <button
                onClick={() => setActiveTab('members')}
                className={`group rounded-md px-3 py-2 flex items-center text-sm font-medium w-full text-left ${
                  activeTab === 'members'
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                    : 'text-gray-900 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <Users className="flex-shrink-0 -ml-1 mr-3 h-6 w-6" />
                <span className="truncate">{t('organization.tabs.members')}</span>
              </button>

              <button
                onClick={() => setActiveTab('billing')}
                className={`group rounded-md px-3 py-2 flex items-center text-sm font-medium w-full text-left ${
                  activeTab === 'billing'
                    ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                    : 'text-gray-900 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <CreditCard className="flex-shrink-0 -ml-1 mr-3 h-6 w-6" />
                <span className="truncate">{t('organization.tabs.billing')}</span>
              </button>
            </nav>
          </aside>

          {/* Main content */}
          <div className="space-y-6 sm:px-6 lg:px-0 lg:col-span-9">
            {/* General Tab */}
            {activeTab === 'general' && (
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                      {t('organization.generalSettings')}
                    </h3>
                    <button
                      onClick={() => setEditingOrg(!editingOrg)}
                      className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <Edit className="-ml-1 mr-2 h-4 w-4" />
                      {editingOrg ? t('common.cancel') : t('common.edit')}
                    </button>
                  </div>

                  {/* Logo */}
                  <div className="mb-8">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      {t('organization.logo')}
                    </label>
                    <div className="flex items-center space-x-6">
                      {organization.logo_url ? (
                        <img
                          className="h-20 w-20 rounded-lg object-cover"
                          src={organization.logo_url}
                        alt={organization.name_en || organization.name_ar}
                        />
                      ) : (
                        <div className="h-20 w-20 rounded-lg bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                          <Building2 className="h-10 w-10 text-gray-500 dark:text-gray-400" />
                        </div>
                      )}
                      <label className="cursor-pointer inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                        <Upload className="-ml-1 mr-2 h-4 w-4" />
                        {t('organization.uploadLogo')}
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleLogoUpload}
                          className="hidden"
                        />
                      </label>
                    </div>
                  </div>

                  {/* Organization Details */}
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        {t('organization.fields.name')}
                      </label>
                      <input
                        type="text"
                        value={orgForm.name}
                        onChange={(e) => setOrgForm({ ...orgForm, name: e.target.value })}
                        disabled={!editingOrg}
                        className="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-50 dark:disabled:bg-gray-800 disabled:text-gray-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        {t('organization.fields.description')}
                      </label>
                      <textarea
                        value={orgForm.description}
                        onChange={(e) => setOrgForm({ ...orgForm, description: e.target.value })}
                        disabled={!editingOrg}
                        rows={3}
                        className="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-50 dark:disabled:bg-gray-800 disabled:text-gray-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        {t('organization.fields.website')}
                      </label>
                      <input
                        type="url"
                        value={orgForm.website}
                        onChange={(e) => setOrgForm({ ...orgForm, website: e.target.value })}
                        disabled={!editingOrg}
                        className="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-50 dark:disabled:bg-gray-800 disabled:text-gray-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        {t('organization.fields.industry')}
                      </label>
                      <select
                        value={orgForm.industry}
                        onChange={(e) => setOrgForm({ ...orgForm, industry: e.target.value })}
                        disabled={!editingOrg}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:bg-gray-50 dark:disabled:bg-gray-800 disabled:text-gray-500"
                      >
                        <option value="">{t('organization.selectIndustry')}</option>
                        <option value="technology">{t('industries.technology')}</option>
                        <option value="healthcare">{t('industries.healthcare')}</option>
                        <option value="finance">{t('industries.finance')}</option>
                        <option value="manufacturing">{t('industries.manufacturing')}</option>
                        <option value="retail">{t('industries.retail')}</option>
                        <option value="education">{t('industries.education')}</option>
                        <option value="other">{t('industries.other')}</option>
                      </select>
                    </div>
                  </div>

                  {editingOrg && (
                    <div className="mt-8 flex justify-end space-x-3">
                      <button
                        onClick={() => setEditingOrg(false)}
                        className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        {t('common.cancel')}
                      </button>
                      <button
                        onClick={handleSaveOrganization}
                        disabled={saving}
                        className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Save className="-ml-1 mr-2 h-4 w-4" />
                        {saving ? t('common.saving') : t('common.save')}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Members Tab */}
            {activeTab === 'members' && (
              <div className="space-y-6">
                {/* Stats */}
                {stats && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                      <div className="p-5">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <Users className="h-6 w-6 text-gray-400" />
                          </div>
                          <div className="ml-5 w-0 flex-1">
                            <dl>
                              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                                {t('organization.stats.totalMembers')}
                              </dt>
                              <dd className="text-lg font-medium text-gray-900 dark:text-white">
                                {stats.total_members}
                              </dd>
                            </dl>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                      <div className="p-5">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <UserCheck className="h-6 w-6 text-green-400" />
                          </div>
                          <div className="ml-5 w-0 flex-1">
                            <dl>
                              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                                {t('organization.stats.activeMembers')}
                              </dt>
                              <dd className="text-lg font-medium text-gray-900 dark:text-white">
                                {stats.active_members}
                              </dd>
                            </dl>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                      <div className="p-5">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <Clock className="h-6 w-6 text-yellow-400" />
                          </div>
                          <div className="ml-5 w-0 flex-1">
                            <dl>
                              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                                {t('organization.stats.pendingInvitations')}
                              </dt>
                              <dd className="text-lg font-medium text-gray-900 dark:text-white">
                                {stats.pending_invitations}
                              </dd>
                            </dl>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Invite Member */}
                <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                  <div className="px-4 py-5 sm:p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                        {t('organization.inviteMember')}
                      </h3>
                      <button
                        onClick={() => setShowInviteForm(!showInviteForm)}
                        className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        <Plus className="-ml-1 mr-2 h-4 w-4" />
                        {t('organization.inviteNew')}
                      </button>
                    </div>

                    {showInviteForm && (
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            {t('organization.emailAddress')}
                          </label>
                          <input
                            type="email"
                            value={inviteEmail}
                            onChange={(e) => setInviteEmail(e.target.value)}
                            className="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            placeholder={t('organization.emailPlaceholder')}
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                            {t('organization.role')}
                          </label>
                          <select
                            value={inviteRole}
                            onChange={(e) => setInviteRole(e.target.value)}
                            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          >
                            <option value="member">{t('organization.roles.member')}</option>
                            <option value="admin">{t('organization.roles.admin')}</option>
                          </select>
                        </div>
                        <div className="flex justify-end space-x-3">
                          <button
                            onClick={() => setShowInviteForm(false)}
                            className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                          >
                            {t('common.cancel')}
                          </button>
                          <button
                            onClick={handleInviteMember}
                            disabled={saving || !inviteEmail.trim()}
                            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <Mail className="-ml-1 mr-2 h-4 w-4" />
                            {saving ? t('common.sending') : t('organization.sendInvite')}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Members List */}
                <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                  <div className="px-4 py-5 sm:p-6">
                    <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-6">
                      {t('organization.members')}
                    </h3>

                    <div className="space-y-4">
                      {members.map((member) => (
                        <div
                          key={member.id}
                          className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
                        >
                          <div className="flex items-center space-x-4">
                            <div className="flex-shrink-0">
                              <div className="h-10 w-10 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                  {member.user?.full_name_en?.charAt(0) || member.user?.username?.charAt(0) || '?'}
                                </span>
                              </div>
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center space-x-2">
                                  <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                                    {member.user?.full_name_en || member.user?.username || 'Unknown User'}
                                  </h4>
                                  <div className="flex items-center space-x-1">
                                    {getRoleIcon(member.role)}
                                    <span className="text-xs text-gray-500 dark:text-gray-400">
                                      {t(`organization.roles.${member.role}`)}
                                    </span>
                                  </div>
                                  <div className={`flex items-center space-x-1 ${getStatusColor(member.is_active ? 'active' : 'inactive')}`}>
                                    {getStatusIcon(member.is_active ? 'active' : 'inactive')}
                                    <span className="text-xs">
                                      {t(`organization.status.${member.is_active ? 'active' : 'inactive'}`)}
                                    </span>
                                  </div>
                                </div>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                  {member.user?.email || 'No email'}
                                </p>
                              <p className="text-xs text-gray-400 dark:text-gray-500">
                                {t('organization.joinedAt')}: {new Date(member.joined_at).toLocaleDateString()}
                              </p>
                            </div>
                          </div>

                          {member.role !== 'owner' && (
                            <div className="flex items-center space-x-2">
                              <select
                                value={member.role}
                                onChange={(e) => handleUpdateMemberRole(member.id, e.target.value as 'admin' | 'member')}
                                className="text-sm border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                              >
                                <option value="member">{t('organization.roles.member')}</option>
                                <option value="admin">{t('organization.roles.admin')}</option>
                              </select>
                              <button
                                onClick={() => handleRemoveMember(member.id)}
                                className="inline-flex items-center p-2 border border-transparent rounded-md text-gray-400 hover:text-red-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                                title={t('organization.removeMember')}
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Billing Tab */}
            {activeTab === 'billing' && (
              <div className="space-y-6">
                {/* Usage Stats */}
                {stats && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                      <div className="p-5">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                          {t('organization.storageUsage')}
                        </h3>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-500 dark:text-gray-400">
                              {t('organization.used')}
                            </span>
                            <span className="text-gray-900 dark:text-white">
                              {stats.storage_used} GB / {stats.storage_limit} GB
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${(stats.storage_used / stats.storage_limit) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                      <div className="p-5">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                          {t('organization.apiUsage')}
                        </h3>
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-500 dark:text-gray-400">
                              {t('organization.thisMonth')}
                            </span>
                            <span className="text-gray-900 dark:text-white">
                              {stats.api_calls_this_month.toLocaleString()} / {stats.api_calls_limit.toLocaleString()}
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${(stats.api_calls_this_month / stats.api_calls_limit) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Current Subscription */}
                {subscription && (
                  <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                    <div className="px-4 py-5 sm:p-6">
                      <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-6">
                        {t('organization.currentPlan')}
                      </h3>

                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center space-x-3">
                            <h4 className="text-xl font-semibold text-gray-900 dark:text-white">
                              {subscription.plan_name}
                            </h4>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              subscription.status === 'active'
                                ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                                : subscription.status === 'past_due'
                                ? 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                                : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
                            }`}>
                              {t(`organization.subscriptionStatus.${subscription.status}`)}
                            </span>
                          </div>
                          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            ${subscription.amount}/{t('organization.month')} • {t('organization.renewsOn')} {new Date(subscription.current_period_end).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex space-x-3">
                          <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            {t('organization.changePlan')}
                          </button>
                          <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            <Download className="-ml-1 mr-2 h-4 w-4" />
                            {t('organization.downloadInvoice')}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default OrganizationSettings