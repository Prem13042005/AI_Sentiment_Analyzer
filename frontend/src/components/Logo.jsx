import React from 'react'

const Logo = ({ size = 'lg', className = '' }) => {
  const iconSize = size === 'sm' ? 24 : 36
  const textSize = size === 'sm' ? 'text-lg' : 'text-2xl'
  
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <svg
        width={iconSize}
        height={iconSize}
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="flex-shrink-0"
      >
        <defs>
          <linearGradient id="logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#00b8a9" />
            <stop offset="100%" stopColor="#0052d4" />
          </linearGradient>
        </defs>
        <circle cx="50" cy="50" r="48" fill="url(#logo-grad)" />
        {/* Stylized S shape path */}
        <path
          d="M 35 32 
             C 35 22, 65 22, 65 35 
             C 65 48, 35 48, 35 62 
             C 35 75, 65 75, 65 65"
          stroke="white"
          strokeWidth="12"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
      </svg>
      <span className={`${textSize} font-bold tracking-tight select-none`}>
        <span className="text-[#0f1a2e] dark:text-white">Sentix</span>
        <span className="text-[#00b8a9] font-extrabold"> AI</span>
      </span>
    </div>
  )
}

export default Logo
