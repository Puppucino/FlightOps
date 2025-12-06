import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

export const Sidebar = () => {
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/')
  }

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">FlightOps</h2>
        <select className="workspace-selector">
          <option>Default Workspace</option>
        </select>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section">
          <Link to="/" className={`nav-item ${isActive('/') && location.pathname !== '/flight-ops' && !location.pathname.startsWith('/cargo-analytics') ? 'active' : ''}`}>
            <span className="nav-icon">📊</span>
            <span className="nav-label">Dashboard</span>
          </Link>
          <Link to="/flight-ops" className={`nav-item ${location.pathname === '/flight-ops' ? 'active' : ''}`}>
            <span className="nav-icon">✈️</span>
            <span className="nav-label">Flight Operations</span>
          </Link>
          <Link to="/cargo-analytics" className={`nav-item ${location.pathname.startsWith('/cargo-analytics') ? 'active' : ''}`}>
            <span className="nav-icon">📦</span>
            <span className="nav-label">Cargo Analytics</span>
          </Link>
        </div>

        <div className="nav-section">
          <div className="nav-section-title">Quick Access</div>
          <Link to="/" className="nav-item">
            <span className="nav-icon">⚠️</span>
            <span className="nav-label">High Risk Flights</span>
          </Link>
          <Link to="/" className="nav-item">
            <span className="nav-icon">⏱️</span>
            <span className="nav-label">Delayed Today</span>
          </Link>
          <Link to="/" className="nav-item">
            <span className="nav-icon">✅</span>
            <span className="nav-label">On Schedule</span>
          </Link>
        </div>

        <div className="nav-section">
          <div className="nav-section-title">Spaces</div>
          <Link to="/" className="nav-item">
            <span className="nav-icon">🌍</span>
            <span className="nav-label">All Airports</span>
          </Link>
          <Link to="/" className="nav-item">
            <span className="nav-icon">📍</span>
            <span className="nav-label">Kuala Lumpur (KUL)</span>
          </Link>
          <Link to="/" className="nav-item">
            <span className="nav-icon">📍</span>
            <span className="nav-label">Singapore (SIN)</span>
          </Link>
        </div>
      </nav>

      <div className="sidebar-footer">
        <button className="upgrade-btn">Upgrade</button>
        <button className="invite-btn">Invite</button>
      </div>
    </div>
  )
}
