import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
})

// Request Interceptor: Inject sentix_token into Authorization header
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sentix_token') || localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response Interceptor: Redirect to /login on 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.clear()
      if (
        window.location.pathname !== '/login' &&
        window.location.pathname !== '/register' &&
        window.location.pathname !== '/'
      ) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Helper to extract detail string from Axios error
export const getErrorMessage = (error) => {
  if (!error) return 'An unknown error occurred.'
  if (!error.response) return 'Cannot connect to the backend server. Please verify the API is running.'
  
  const detail = error.response.data?.detail
  if (typeof detail === 'string') {
    return detail
  } else if (Array.isArray(detail)) {
    return detail.map(d => {
      const field = d.loc ? d.loc[d.loc.length - 1] : ''
      return `${field ? field + ': ' : ''}${d.msg}`
    }).join(', ')
  }
  return 'An error occurred during execution.'
}

// Named functions
export const register = async (username, email, password) => {
  const response = await api.post('/api/v1/auth/register', {
    username,
    email,
    password,
  })
  return response.data
}

export const login = async (username, password) => {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('password', password)
  
  const response = await api.post('/api/v1/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
  return response.data
}

export const loginWithGoogle = async (email, name) => {
  const response = await api.post('/api/v1/auth/google', { email, name })
  return response.data
}

export const getMe = async () => {
  const response = await api.get('/api/v1/auth/me')
  return response.data
}

export const logout = async () => {
  try {
    const response = await api.post('/api/v1/auth/logout')
    return response.data
  } finally {
    localStorage.clear()
  }
}

export const predict = async (text, modelName = 'ensemble') => {
  const response = await api.post('/api/v1/predict', { text })
  return response.data
}

export const predictBulk = async (texts) => {
  const response = await api.post('/api/v1/predict/bulk', { texts })
  return response.data
}

export const getHistory = async (params = {}) => {
  const response = await api.get('/api/v1/history/', { params })
  return response.data
}

export const getStats = async () => {
  const response = await api.get('/api/v1/history/stats')
  return response.data
}

export const deleteHistoryItem = async (id) => {
  const response = await api.delete(`/api/v1/history/${id}`)
  return response.data
}

// Backwards-compatible alias for existing page components
export const deleteHistory = deleteHistoryItem

export default api
