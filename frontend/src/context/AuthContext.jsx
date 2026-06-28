import React, { createContext, useState, useEffect, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe, logout as logoutApi } from '../services/api'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('sentix_token') || localStorage.getItem('token'))
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user')
    try {
      return savedUser ? JSON.parse(savedUser) : null
    } catch {
      return null
    }
  })
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!(localStorage.getItem('sentix_token') || localStorage.getItem('token')))
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  // Verify token validity on mount
  useEffect(() => {
    const verifyToken = async () => {
      const storedToken = localStorage.getItem('sentix_token') || localStorage.getItem('token')
      if (storedToken) {
        try {
          // Temporarily set in state to allow Axios interceptor to run
          setToken(storedToken)
          const userData = await getMe()
          setUser(userData)
          setIsAuthenticated(true)
          localStorage.setItem('user', JSON.stringify(userData))
        } catch (error) {
          console.error('Failed to verify token:', error)
          localStorage.removeItem('sentix_token')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          setToken(null)
          setUser(null)
          setIsAuthenticated(false)
        }
      } else {
        setIsAuthenticated(false)
        setUser(null)
      }
      setIsLoading(false)
    }

    verifyToken()
  }, [])

  // Defensive support for both login(tokenData) and login(token, user)
  const handleLogin = (tokenOrData, userData = null) => {
    let accessToken = ''
    let userObj = userData

    if (typeof tokenOrData === 'string') {
      accessToken = tokenOrData
    } else if (tokenOrData && tokenOrData.access_token) {
      accessToken = tokenOrData.access_token
      if (!userObj) {
        userObj = { id: tokenOrData.user_id, username: tokenOrData.username }
      }
    }

    localStorage.setItem('sentix_token', accessToken)
    localStorage.setItem('token', accessToken)
    if (userObj) {
      localStorage.setItem('user', JSON.stringify(userObj))
    }
    setToken(accessToken)
    setUser(userObj)
    setIsAuthenticated(true)
  }

  const handleLogout = async () => {
    try {
      await logoutApi()
    } catch (error) {
      console.error('Failed API logout request:', error)
    } finally {
      localStorage.removeItem('sentix_token')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      setToken(null)
      setUser(null)
      setIsAuthenticated(false)
      navigate('/login')
    }
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isAuthenticated,
        isLoading,
        login: handleLogin,
        logout: handleLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
