import React from 'react'
import './Card.css'

interface CardProps {
  title?: string
  children: React.ReactNode
  className?: string
  icon?: React.ReactNode
}

export const Card: React.FC<CardProps> = ({ title, children, className = '', icon }) => {
  return (
    <div className={`card ${className}`}>
      {title && (
        <div className="card-header">
          {icon && <span className="card-icon">{icon}</span>}
          <h3 className="card-title">{title}</h3>
        </div>
      )}
      <div className="card-content">{children}</div>
    </div>
  )
}
