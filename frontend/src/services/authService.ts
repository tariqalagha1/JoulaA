import api from './api'

export interface LoginRequest {
  email_or_username: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  full_name_ar?: string
  full_name_en?: string
  language_preference?: string
  timezone?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: {
    id: string
    email: string
    username: string
    full_name_ar?: string
    full_name_en?: string
    role: string
    language_preference: string
  }
}

export interface User {
  id: string
  email: string
  username: string
  full_name_ar?: string
  full_name_en?: string
  role: string
  language_preference: string
}

class AuthService {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', credentials)
    const { access_token, refresh_token, user } = response.data
    
    // Store tokens and user data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    localStorage.setItem('user', JSON.stringify(user))
    
    return response.data
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register', userData)
    const { access_token, refresh_token, user } = response.data
    
    // Store tokens and user data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    localStorage.setItem('user', JSON.stringify(user))
    
    return response.data
  }

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout API call failed:', error)
    } finally {
      // Clear local storage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  }

  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        return JSON.parse(userStr)
      } catch (error) {
        console.error('Error parsing stored user:', error)
        localStorage.removeItem('user')
      }
    }
    return null
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token')
  }

  isAuthenticated(): boolean {
    const token = this.getAccessToken()
    const user = this.getStoredUser()
    return !!(token && user)
  }
}

export const authService = new AuthService()
export default authService