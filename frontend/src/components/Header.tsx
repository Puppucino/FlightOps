import { useNavigate, useLocation } from 'react-router-dom'
import './Header.css'

interface HeaderProps {
  searchQuery?: string
  onSearchChange?: (value: string) => void
  title?: string
  showBackButton?: boolean
}

export const Header = ({ 
  searchQuery = '', 
  onSearchChange, 
  title, 
  showBackButton 
}: HeaderProps) => {
  const navigate = useNavigate()
  const location = useLocation()

  const isDetailPage = location.pathname.includes('/cargo-analytics/') && location.pathname !== '/cargo-analytics'
  const shouldShowBack = showBackButton !== undefined ? showBackButton : isDetailPage
  const getViewTitle = () => {
    if (title) return title
    if (location.pathname === '/') {
      return 'Dashboard'
    }
    if (location.pathname === '/flight-ops') {
      return 'Flight Operations'
    }
    if (isDetailPage) {
      return 'Flight Analytics'
    }
    if (location.pathname === '/cargo-analytics') {
      return 'All Flights'
    }
    return 'Cargo Analytics Dashboard'
  }

  const getBreadcrumb = () => {
    if (location.pathname === '/') {
      return 'Dashboard'
    }
    if (location.pathname === '/flight-ops') {
      return 'Flight Operations'
    }
    return 'Cargo Analytics'
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
          <span className="breadcrumb-item">{getBreadcrumb()}</span>
          {(isDetailPage || location.pathname === '/flight-ops') && (
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
          value={searchQuery}
          onChange={(e) => onSearchChange?.(e.target.value)}
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
