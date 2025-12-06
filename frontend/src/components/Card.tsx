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
    <article className={`card ${className}`}>
      {title && (
        <header className="card-header">
          {icon && <span className="card-icon" aria-hidden="true">{icon}</span>}
          <h3 className="card-title">{title}</h3>
        </header>
      )}
      <div className="card-content">{children}</div>
    </article>
  )
}
