import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

export const Sidebar = () => {
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/')
  }

  return (
    <aside className="sidebar" role="complementary" aria-label="Main navigation">
      <div className="sidebar-header">
        <h2 className="sidebar-title">FlightOps</h2>
      </div>

      <nav className="sidebar-nav" aria-label="Primary navigation">
        <div className="nav-section">
          <Link 
            to="/" 
            className={`nav-item ${isActive('/') && location.pathname !== '/flight-ops' && !location.pathname.startsWith('/cargo-analytics') ? 'active' : ''}`}
            aria-current={isActive('/') && location.pathname !== '/flight-ops' && !location.pathname.startsWith('/cargo-analytics') ? 'page' : undefined}
          >
            <span className="nav-icon" aria-hidden="true">📊</span>
            <span className="nav-label">Dashboard</span>
          </Link>
          <Link 
            to="/flight-ops" 
            className={`nav-item ${location.pathname === '/flight-ops' ? 'active' : ''}`}
            aria-current={location.pathname === '/flight-ops' ? 'page' : undefined}
          >
            <span className="nav-icon" aria-hidden="true">✈️</span>
            <span className="nav-label">Flight Operations</span>
          </Link>
          <Link 
            to="/cargo-analytics" 
            className={`nav-item ${location.pathname.startsWith('/cargo-analytics') ? 'active' : ''}`}
            aria-current={location.pathname.startsWith('/cargo-analytics') ? 'page' : undefined}
          >
            <span className="nav-icon" aria-hidden="true">📦</span>
            <span className="nav-label">Cargo Analytics</span>
          </Link>
        </div>
      </nav>
    </aside>
  )
}
