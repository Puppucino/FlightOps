import React from 'react'
import './ProgressBar.css'

interface ProgressBarProps {
  value: number
  max?: number
  label?: string
  showPercentage?: boolean
  color?: 'primary' | 'success' | 'warning' | 'danger'
  size?: 'small' | 'medium' | 'large'
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  label,
  showPercentage = true,
  color = 'primary',
  size = 'medium',
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100)

  return (
    <div className={`progress-bar-container progress-${size}`}>
      {label && (
        <div className="progress-label">
          <span>{label}</span>
          {showPercentage && <span className="progress-percentage">{percentage.toFixed(1)}%</span>}
        </div>
      )}
      <div className={`progress-bar progress-${color}`}>
        <div
          className="progress-fill"
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={percentage}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
      {!label && showPercentage && (
        <div className="progress-percentage-text">{percentage.toFixed(1)}%</div>
      )}
    </div>
  )
}
