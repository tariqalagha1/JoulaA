import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Plus,
  Search,
  Filter,
  MessageSquare,
  Calendar,
  User,
  MoreVertical,
  Trash2,
  Share2,
  Download,
  Eye,
  Clock
} from 'lucide-react'
import { conversationService, Conversation, ConversationStats } from '../services/conversationService'
import toast from 'react-hot-toast'

const ConversationsPage: React.FC = () => {
  const { t } = useTranslation()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [stats, setStats] = useState<ConversationStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterAgent, setFilterAgent] = useState('')
  const [filterDateRange, setFilterDateRange] = useState('')
  const [sortBy, setSortBy] = useState('updated_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [selectedConversations, setSelectedConversations] = useState<string[]>([])
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    loadConversations()
    loadStats()
  }, [searchQuery, filterAgent, filterDateRange, sortBy, sortOrder, page])

  const loadConversations = async () => {
    try {
      setLoading(true)
      const response = await conversationService.listConversations({
        query: searchQuery || undefined,
        agent_id: filterAgent || undefined,
        date_from: filterDateRange === 'today' ? new Date().toISOString().split('T')[0] : undefined,
        date_to: filterDateRange === 'today' ? new Date().toISOString().split('T')[0] : undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
        page,
        page_size: 20
      })
      setConversations(response.conversations)
      setTotalPages(response.total_pages)
    } catch (error) {
      toast.error(t('conversations.loadError'))
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const statsData = await conversationService.getConversationStats()
      setStats(statsData)
    } catch (error) {
      console.error('Failed to load conversation stats:', error)
    }
  }

  const handleDeleteConversation = async (conversationId: string) => {
    if (!confirm(t('conversations.confirmDelete'))) return
    
    try {
      await conversationService.deleteConversation(conversationId)
      toast.success(t('conversations.deleteSuccess'))
      loadConversations()
      loadStats()
    } catch (error) {
      toast.error(t('conversations.deleteError'))
    }
  }

  const handleShareConversation = async (conversationId: string) => {
    try {
      const shareData = await conversationService.shareConversation(conversationId, {
        is_public: true
      })
      navigator.clipboard.writeText(shareData.share_url)
      toast.success(t('conversations.shareSuccess'))
    } catch (error) {
      toast.error(t('conversations.shareError'))
    }
  }

  const handleExportConversation = async (conversationId: string, format: 'json' | 'txt' | 'pdf') => {
    try {
      const blob = await conversationService.exportConversation(conversationId, format)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      a.download = `conversation-${conversationId}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success(t('conversations.exportSuccess'))
    } catch (error) {
      toast.error(t('conversations.exportError'))
    }
  }

  const handleBulkOperation = async (operation: string) => {
    if (selectedConversations.length === 0) {
      toast.error(t('conversations.selectConversationsFirst'))
      return
    }

    try {
      await conversationService.bulkOperation(operation, selectedConversations)
      toast.success(t('conversations.bulkOperationSuccess'))
      setSelectedConversations([])
      loadConversations()
      loadStats()
    } catch (error) {
      toast.error(t('conversations.bulkOperationError'))
    }
  }

  const toggleConversationSelection = (conversationId: string) => {
    setSelectedConversations(prev => 
      prev.includes(conversationId) 
        ? prev.filter(id => id !== conversationId)
        : [...prev, conversationId]
    )
  }

  const selectAllConversations = () => {
    setSelectedConversations(conversations.map(conv => conv.id))
  }

  const clearSelection = () => {
    setSelectedConversations([])
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {t('conversations.title')}
                </h1>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {t('conversations.subtitle')}
                </p>
              </div>
              <Link
                to="/conversations/new"
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Plus className="-ml-1 mr-2 h-5 w-5" />
                {t('conversations.startNew')}
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <MessageSquare className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        {t('conversations.stats.total')}
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-white">
                        {stats.total_conversations}
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
                    <Calendar className="h-6 w-6 text-green-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        {t('conversations.stats.today')}
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-white">
                        {stats.conversations_today}
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
                    <MessageSquare className="h-6 w-6 text-blue-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        {t('conversations.stats.totalMessages')}
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-white">
                        {stats.total_messages}
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
                    <Clock className="h-6 w-6 text-purple-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        {t('conversations.stats.avgLength')}
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-white">
                        {stats.avg_messages_per_conversation.toFixed(1)}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    placeholder={t('conversations.searchPlaceholder')}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
              </div>

              {/* Filter Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Filter className="-ml-1 mr-2 h-5 w-5" />
                {t('common.filters')}
              </button>
            </div>

            {/* Expanded Filters */}
            {showFilters && (
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {t('conversations.filters.agent')}
                    </label>
                    <input
                      type="text"
                      value={filterAgent}
                      onChange={(e) => setFilterAgent(e.target.value)}
                      placeholder={t('conversations.filters.agentPlaceholder')}
                      className="mt-1 block w-full pl-3 pr-3 py-2 text-base border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {t('conversations.filters.dateRange')}
                    </label>
                    <select
                      value={filterDateRange}
                      onChange={(e) => setFilterDateRange(e.target.value)}
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
                    >
                      <option value="">{t('common.all')}</option>
                      <option value="today">{t('conversations.filters.today')}</option>
                      <option value="week">{t('conversations.filters.thisWeek')}</option>
                      <option value="month">{t('conversations.filters.thisMonth')}</option>
                      <option value="year">{t('conversations.filters.thisYear')}</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      {t('common.sortBy')}
                    </label>
                    <select
                      value={`${sortBy}-${sortOrder}`}
                      onChange={(e) => {
                        const [field, order] = e.target.value.split('-')
                        setSortBy(field)
                        setSortOrder(order as 'asc' | 'desc')
                      }}
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
                    >
                      <option value="updated_at-desc">{t('conversations.sort.recentlyUpdated')}</option>
                      <option value="created_at-desc">{t('conversations.sort.newest')}</option>
                      <option value="created_at-asc">{t('conversations.sort.oldest')}</option>
                      <option value="title-asc">{t('conversations.sort.titleAZ')}</option>
                      <option value="title-desc">{t('conversations.sort.titleZA')}</option>
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bulk Actions */}
      {selectedConversations.length > 0 && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <span className="text-sm text-blue-700 dark:text-blue-300">
                  {t('conversations.selectedCount', { count: selectedConversations.length })}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleBulkOperation('export')}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
                >
                  {t('conversations.bulkExport')}
                </button>
                <button
                  onClick={() => handleBulkOperation('delete')}
                  className="text-sm text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
                >
                  {t('conversations.bulkDelete')}
                </button>
                <button
                  onClick={clearSelection}
                  className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                >
                  {t('common.clearSelection')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Conversations List */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6 pb-12">
        {loading ? (
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <div className="animate-pulse">
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : conversations.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 text-center">
            <div className="mx-auto h-12 w-12 text-gray-400">
              <MessageSquare className="h-12 w-12" />
            </div>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              {t('conversations.noConversations')}
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {t('conversations.noConversationsDescription')}
            </p>
            <div className="mt-6">
              <Link
                to="/conversations/new"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Plus className="-ml-1 mr-2 h-5 w-5" />
                {t('conversations.startFirst')}
              </Link>
            </div>
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 shadow overflow-hidden rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <input
                    type="checkbox"
                    checked={selectedConversations.length === conversations.length}
                    onChange={() => selectedConversations.length === conversations.length ? clearSelection() : selectAllConversations()}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {t('common.selectAll')}
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                {conversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    className={`border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors ${
                      selectedConversations.includes(conversation.id) ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <input
                          type="checkbox"
                          checked={selectedConversations.includes(conversation.id)}
                          onChange={() => toggleConversationSelection(conversation.id)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <Link
                              to={`/conversations/${conversation.id}`}
                              className="text-lg font-medium text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400"
                            >
                              {conversation.title || t('conversations.untitled')}
                            </Link>
                          </div>
                          <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                            <div className="flex items-center space-x-1">
                              <User className="h-4 w-4" />
                              <span>{conversation.agent_id || t('conversations.unknownAgent')}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <MessageSquare className="h-4 w-4" />
                              <span>{conversation.message_count} {t('conversations.messages')}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Calendar className="h-4 w-4" />
                              <span>{formatDate(conversation.created_at)}</span>
                            </div>
                            {conversation.updated_at && (
                              <div className="flex items-center space-x-1">
                                <Clock className="h-4 w-4" />
                                <span>{t('conversations.lastActivity')}: {formatTime(conversation.updated_at)}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        <Link
                          to={`/conversations/${conversation.id}`}
                          className="inline-flex items-center p-2 border border-transparent rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                          title={t('conversations.view')}
                        >
                          <Eye className="h-5 w-5" />
                        </Link>
                        <button
                          onClick={() => handleShareConversation(conversation.id)}
                          className="inline-flex items-center p-2 border border-transparent rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                          title={t('conversations.share')}
                        >
                          <Share2 className="h-5 w-5" />
                        </button>
                        <div className="relative">
                          <button
                            onClick={() => handleExportConversation(conversation.id, 'json')}
                            className="inline-flex items-center p-2 border border-transparent rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            title={t('conversations.export')}
                          >
                            <Download className="h-5 w-5" />
                          </button>
                        </div>
                        <button
                          onClick={() => handleDeleteConversation(conversation.id)}
                          className="inline-flex items-center p-2 border border-transparent rounded-md text-gray-400 hover:text-red-500 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                          title={t('conversations.delete')}
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-6 flex items-center justify-between">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {t('common.previous')}
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {t('common.next')}
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {t('common.pagination.showing')} <span className="font-medium">{(page - 1) * 20 + 1}</span> {t('common.pagination.to')}{' '}
                  <span className="font-medium">{Math.min(page * 20, conversations.length)}</span> {t('common.pagination.of')}{' '}
                  <span className="font-medium">{conversations.length}</span> {t('common.pagination.results')}
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {t('common.previous')}
                  </button>
                  {[...Array(totalPages)].map((_, i) => (
                    <button
                      key={i + 1}
                      onClick={() => setPage(i + 1)}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        page === i + 1
                          ? 'z-10 bg-blue-50 dark:bg-blue-900/20 border-blue-500 dark:border-blue-400 text-blue-600 dark:text-blue-400'
                          : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      {i + 1}
                    </button>
                  ))}
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={page === totalPages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {t('common.next')}
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ConversationsPage