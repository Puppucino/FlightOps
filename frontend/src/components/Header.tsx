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
  const isDashboard = location.pathname === '/'

  // For Dashboard, use the Tailwind version
  if (isDashboard && onSearchChange) {
    return (
      <div className="h-16 bg-gray-800 dark:bg-gray-900 border-b border-gray-700 dark:border-gray-800 flex items-center justify-between px-4 sm:px-6 fixed top-0 left-64 right-0 z-40">
        {/* Left: Create Button */}
        <div className="flex items-center gap-4">
          <button className="px-3 sm:px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium flex items-center gap-2 transition-colors">
            <span>+</span>
            <span className="hidden sm:inline">New Alert</span>
          </button>
        </div>

        {/* Center: Search */}
        <div className="flex-1 max-w-2xl mx-4 sm:mx-8">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Q Search ⌘K"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-700 dark:bg-gray-800 border border-gray-600 dark:border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500 transition-all"
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
              <div className="w-6 h-6 rounded bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-xs text-white font-bold">
                Q
              </div>
            </div>
          </div>
        </div>

        {/* Right: Action Icons */}
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <button className="relative p-2 text-gray-400 hover:text-white transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border-2 border-gray-800"></span>
          </button>

          {/* Automate */}
          <button className="p-2 text-gray-400 hover:text-white transition-colors" title="Automate">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </button>

          {/* AI Assistant */}
          <button className="p-2 text-gray-400 hover:text-white transition-colors" title="Ask AI">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </button>

          {/* Share */}
          <button className="relative p-2 text-gray-400 hover:text-white transition-colors" title="Share">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.885 12.938 9 12.482 9 12c0-.482-.115-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
            <span className="absolute top-1 right-1 w-2 h-2 bg-blue-500 rounded-full border-2 border-gray-800"></span>
          </button>

          {/* User Avatar */}
          <button className="flex items-center gap-2 pl-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white text-sm font-semibold">
              FO
            </div>
            <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>
    )
  }

  // For Cargo Analytics pages, use the CSS version
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
