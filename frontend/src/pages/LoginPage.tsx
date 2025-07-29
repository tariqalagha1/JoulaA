import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

const LoginPage: React.FC = () => {
  const { t } = useTranslation()
  const { login, isLoading } = useAuth()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    email_or_username: '',
    password: ''
  })
  const [errors, setErrors] = useState<{ [key: string]: string }>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {}
    
    if (!formData.email_or_username.trim()) {
      newErrors.email_or_username = t('auth.emailRequired')
    }
    
    if (!formData.password) {
      newErrors.password = t('auth.passwordRequired')
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    try {
      await login(formData)
      navigate('/dashboard')
    } catch (error: any) {
      console.error('Login failed:', error)
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail)
      } else {
        toast.error(t('auth.loginFailed'))
      }
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-secondary-50">
      <div className="card w-full max-w-md">
        <h2 className="text-2xl font-bold text-center mb-6">
          {t('auth.login')}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              {t('auth.emailOrUsername')}
            </label>
            <input
              type="text"
              name="email_or_username"
              value={formData.email_or_username}
              onChange={handleChange}
              className={`input-field ${errors.email_or_username ? 'border-red-500' : ''}`}
              placeholder="example@company.com or username"
              disabled={isLoading}
            />
            {errors.email_or_username && (
              <p className="text-red-500 text-sm mt-1">{errors.email_or_username}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">
              {t('auth.password')}
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`input-field ${errors.password ? 'border-red-500' : ''}`}
              placeholder="••••••••"
              disabled={isLoading}
            />
            {errors.password && (
              <p className="text-red-500 text-sm mt-1">{errors.password}</p>
            )}
          </div>
          <button 
            type="submit" 
            className="btn-primary w-full"
            disabled={isLoading}
          >
            {isLoading ? t('auth.loggingIn') : t('auth.login')}
          </button>
        </form>
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            {t('auth.noAccount')}{' '}
            <Link to="/register" className="text-primary-600 hover:text-primary-700 font-medium">
              {t('auth.register')}
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default LoginPage