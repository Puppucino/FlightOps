import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import './Header.css'

interface HeaderProps {
  title?: string
  showBackButton?: boolean
}

export const Header: React.FC<HeaderProps> = ({ title, showBackButton }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const isDetailPage = location.pathname.includes('/cargo-analytics/') && location.pathname !== '/cargo-analytics'
  const shouldShowBack = showBackButton !== undefined ? showBackButton : isDetailPage

  const getViewTitle = () => {
    if (title) return title
    if (isDetailPage) {
      return 'Flight Analytics'
    }
    if (location.pathname === '/cargo-analytics' || location.pathname === '/') {
      return 'All Flights'
    }
    return 'Cargo Analytics Dashboard'
  }

  return (
    <div className="main-header">
      <div className="header-left">
        {shouldShowBack && (
          <button className="back-button" onClick={() => navigate('/cargo-analytics')}>
            ← Back
          </button>
        )}
        <div className="header-breadcrumb">
          <span className="breadcrumb-item">Cargo Analytics</span>
          {location.pathname !== '/cargo-analytics' && location.pathname !== '/' && (
            <>
              <span className="breadcrumb-separator">/</span>
              <span className="breadcrumb-item">{getViewTitle()}</span>
            </>
          )}
        </div>
        <button className="favorite-btn">⭐</button>
      </div>
      <div className="header-center">
        <input
          type="text"
          className="header-search"
          placeholder="Search flights, cargo, aircraft..."
        />
      </div>
      <div className="header-right">
        <button className="header-icon-btn">🔔</button>
        <button className="header-icon-btn">⚙️</button>
        <button className="header-icon-btn">🤖</button>
        <button className="header-icon-btn">👤</button>
        <button className="create-btn">+ Create</button>
      </div>
    </div>
  )
}
