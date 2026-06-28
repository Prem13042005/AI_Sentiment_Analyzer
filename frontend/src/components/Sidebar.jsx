import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { 
  LayoutDashboard, 
  BarChart3, 
  Upload, 
  History, 
  Settings, 
  LogOut 
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import Logo from './Logo'

const Sidebar = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Analyzer', path: '/analyzer', icon: BarChart3 },
    { name: 'Bulk Upload', path: '/bulk-upload', icon: Upload },
    { name: 'History', path: '/history', icon: History },
    { name: 'Settings', path: '/settings', icon: Settings },
  ]

  const getInitials = (username) => {
    if (!username) return 'UX'
    const parts = username.trim().split(/\s+/)
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase()
    }
    return username.slice(0, 2).toUpperCase()
  }

  const handleLogoutClick = () => {
    logout()
    navigate('/login')
  }

  const initials = user ? getInitials(user.username) : 'UX'

  return (
    <aside className="flex h-full w-[240px] flex-shrink-0 flex-col justify-between bg-navy text-white">
      {/* Top: Logo & Navigation */}
      <div className="flex flex-col">
        {/* Brand Logo Container */}
        <div className="p-6 border-b border-[#162035]">
          <Logo size="lg" />
        </div>

        {/* Navigation list */}
        <nav className="flex flex-col gap-1.5 p-4">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-teal text-white shadow-sm'
                    : 'text-text-muted hover:bg-navy-mid hover:text-white'
                }`
              }
            >
              {({ isActive }) => {
                const Icon = item.icon
                return (
                  <>
                    <Icon className={`h-5 w-5 ${isActive ? 'text-white' : 'text-text-muted hover:text-white'}`} />
                    <span>{item.name}</span>
                  </>
                )
              }}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Bottom: Profile & Logout */}
      <div className="border-t border-[#162035] bg-[#0b1424] p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 overflow-hidden">
            {/* Avatar circle */}
            <div className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-navy-mid border border-teal text-[13px] font-bold text-white shadow-inner">
              {initials}
            </div>
            
            {/* Username */}
            <div className="flex flex-col overflow-hidden">
              <span className="truncate text-sm font-medium text-white">
                {user ? user.username : 'User'}
              </span>
              <span className="truncate text-xs text-text-muted">
                {user ? user.email : 'operator@sentix.ai'}
              </span>
            </div>
          </div>

          {/* Logout Button */}
          <button
            onClick={handleLogoutClick}
            className="rounded-lg p-2 text-text-muted hover:bg-navy-mid hover:text-red-400 transition-colors duration-200"
            title="Log out"
          >
            <LogOut className="h-5 w-5" />
          </button>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
