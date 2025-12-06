import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

export const Sidebar: React.FC = () => {
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/')
  }

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">Cargo Analytics</h2>
        <select className="workspace-selector">
          <option>Default Workspace</option>
        </select>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section">
          <Link to="/" className={`nav-item ${isActive('/') && !location.pathname.includes('/cargo-analytics/') ? 'active' : ''}`}>
            <span className="nav-icon">🏠</span>
            <span className="nav-label">Home</span>
          </Link>
          <Link to="/cargo-analytics" className={`nav-item ${location.pathname === '/cargo-analytics' ? 'active' : ''}`}>
            <span className="nav-icon">📦</span>
            <span className="nav-label">All Flights</span>
          </Link>
        </div>

        <div className="nav-section">
          <div className="nav-section-title">Favorites</div>
          <div className="nav-item">
            <span className="nav-icon">⭐</span>
            <span className="nav-label">Cargo Flights</span>
          </div>
        </div>

        <div className="nav-section">
          <div className="nav-section-title">Spaces</div>
          <div className="nav-item">
            <span className="nav-icon">📊</span>
            <span className="nav-label">Analytics Dashboard</span>
          </div>
          <div className="nav-item">
            <span className="nav-icon">✈️</span>
            <span className="nav-label">Flight Operations</span>
          </div>
        </div>
      </nav>

      <div className="sidebar-footer">
        <button className="upgrade-btn">Upgrade</button>
        <button className="invite-btn">Invite</button>
      </div>
    </div>
  )
}
