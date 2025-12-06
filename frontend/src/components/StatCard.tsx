import React from 'react'
import './StatCard.css'

interface StatCardProps {
  label: string
  value: string | number
  unit?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  icon?: React.ReactNode
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple'
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  unit,
  trend,
  trendValue,
  icon,
  color = 'blue',
}) => {
  return (
    <div className={`stat-card stat-${color}`}>
      {icon && <div className="stat-icon">{icon}</div>}
      <div className="stat-content">
        <div className="stat-label">{label}</div>
        <div className="stat-value">
          {typeof value === 'number' ? value.toLocaleString() : value}
          {unit && <span className="stat-unit">{unit}</span>}
        </div>
        {trend && trendValue && (
          <div className={`stat-trend stat-trend-${trend}`}>
            {trend === 'up' && '↑'}
            {trend === 'down' && '↓'}
            {trend === 'neutral' && '→'}
            {trendValue}
          </div>
        )}
      </div>
    </div>
  )
}
