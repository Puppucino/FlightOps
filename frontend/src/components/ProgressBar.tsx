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
          <span id={`progress-label-${Math.random().toString(36).substr(2, 9)}`}>{label}</span>
          {showPercentage && (
            <span className="progress-percentage" aria-hidden="true">
              {percentage.toFixed(1)}%
            </span>
          )}
        </div>
      )}
      <div 
        className={`progress-bar progress-${color}`}
        role="progressbar"
        aria-valuenow={percentage}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || `Progress: ${percentage.toFixed(1)}%`}
        aria-live="polite"
      >
        <div
          className="progress-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
      {!label && showPercentage && (
        <div className="progress-percentage-text" aria-hidden="true">
          {percentage.toFixed(1)}%
        </div>
      )}
    </div>
  )
}
