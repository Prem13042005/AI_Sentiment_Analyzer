import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Sidebar from './Sidebar'
import Navbar from './Navbar'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  // Dynamic page title helper
  const getPageTitle = (pathname) => {
    switch (pathname) {
      case '/dashboard':
        return 'Dashboard'
      case '/analyzer':
        return 'Sentiment Analyzer'
      case '/bulk-upload':
        return 'Bulk Upload'
      case '/history':
        return 'Analysis History'
      case '/settings':
        return 'Settings'
      default:
        return 'Sentix AI'
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[#f5f6fa]">
        <div className="flex flex-col items-center gap-3">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-[#00b8a9] border-t-transparent"></div>
          <span className="text-sm font-medium text-[#8896ab]">Validating session...</span>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  const pageTitle = getPageTitle(location.pathname)

  return (
    <div className="flex h-screen overflow-hidden bg-[#f5f6fa]">
      {/* Sidebar navigation */}
      <Sidebar />

      {/* Main viewport */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top toolbar */}
        <Navbar title={pageTitle} />

        {/* Scrollable contents area */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}

export default ProtectedRoute
