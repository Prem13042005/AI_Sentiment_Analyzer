import React from 'react'
import { Bell } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const Navbar = ({ title }) => {
  const { user } = useAuth()
  
  const getInitials = (username) => {
    if (!username) return 'UX'
    const parts = username.trim().split(/\s+/)
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase()
    }
    return username.slice(0, 2).toUpperCase()
  }

  const initials = user ? getInitials(user.username) : 'UX'

  return (
    <header className="flex h-16 items-center justify-between border-b border-gray-border bg-white px-6 md:px-8">
      {/* Left: Page Title */}
      <h1 className="text-xl font-semibold text-text-dark">{title}</h1>

      {/* Right: Notifications + User Profile */}
      <div className="flex items-center gap-4">
        {/* Bell Icon */}
        <button className="relative rounded-full p-2 text-text-muted transition-colors hover:bg-gray-bg hover:text-text-dark">
          <Bell className="h-5 w-5" />
          <span className="absolute right-2.5 top-2.5 h-2 w-2 rounded-full bg-[#ef4444]"></span>
        </button>

        {/* User initials circle */}
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-navy text-[13px] font-bold text-white shadow-sm">
            {initials}
          </div>
          {user && (
            <span className="hidden text-sm font-medium text-text-dark md:block">
              {user.username}
            </span>
          )}
        </div>
      </div>
    </header>
  )
}

export default Navbar
