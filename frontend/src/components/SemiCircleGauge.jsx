import React from 'react'

const SemiCircleGauge = ({ value = 0, label = 'Positive', color = '#00b8a9' }) => {
  // Ensure value is between 0 and 100
  const clampedValue = Math.round(Math.max(0, Math.min(100, value)))
  const radius = 70
  const pathLength = Math.PI * radius // ~219.911
  const dashOffset = pathLength - (pathLength * clampedValue) / 100

  return (
    <div className="flex flex-col items-center justify-center w-[200px] h-[120px] select-none">
      <svg width="200" height="95" viewBox="0 0 200 95" className="overflow-visible">
        <defs>
          <linearGradient id="gauge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={color} />
            <stop offset="100%" stopColor="#3b82f6" />
          </linearGradient>
        </defs>
        
        {/* Outer Arc (Background) */}
        <path
          d="M 30,90 A 70,70 0 0,1 170,90"
          stroke="#e8ecf0"
          strokeWidth="12"
          strokeLinecap="round"
          fill="none"
        />
        
        {/* Inner Arc (Progress) */}
        <path
          d="M 30,90 A 70,70 0 0,1 170,90"
          stroke="url(#gauge-grad)"
          strokeWidth="12"
          strokeLinecap="round"
          fill="none"
          strokeDasharray={pathLength}
          strokeDashoffset={dashOffset}
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      
      {/* Text indicators in the center of the arc */}
      <div className="-mt-8 flex flex-col items-center">
        <span className="text-2xl font-extrabold text-text-dark tracking-tight leading-none">
          {clampedValue}%
        </span>
        <span className="text-xs font-semibold text-text-muted mt-1 uppercase tracking-wider">
          {label}
        </span>
      </div>
    </div>
  )
}

export default SemiCircleGauge
