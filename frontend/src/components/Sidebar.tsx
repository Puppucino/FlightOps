import { useState } from "react"
import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

export const Sidebar = () => {
  const [activeNav, setActiveNav] = useState("dashboard")
  const location = useLocation()

  const isDashboard = location.pathname === '/'
  const isCargoAnalytics = location.pathname.startsWith('/cargo-analytics')

  // For Dashboard, use Tailwind version
  if (isDashboard) {
    const navItems = [
      { id: "dashboard", icon: "📊", label: "Dashboard", active: true },
      { id: "flights", icon: "✈️", label: "Flights" },
      { id: "analytics", icon: "📈", label: "Analytics" },
      { id: "alerts", icon: "🔔", label: "Alerts" },
      { id: "settings", icon: "⚙️", label: "Settings" },
    ]

    const quickLinks = [
      { label: "High Risk Flights", count: 2, color: "text-red-400" },
      { label: "Delayed Today", count: 3, color: "text-orange-400" },
      { label: "On Schedule", count: 1, color: "text-green-400" },
    ]

    return (
      <div className="w-64 bg-gray-900 dark:bg-gray-950 border-r border-gray-800 dark:border-gray-800 h-screen fixed left-0 top-0 overflow-y-auto flex flex-col z-50">
        {/* Logo/Brand Section */}
        <div className="p-4 border-b border-gray-800 dark:border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <span className="text-sm">✈️</span>
            </div>
            <div>
              <div className="text-white font-semibold text-sm">FlightOps</div>
              <div className="text-gray-400 text-xs">Delay Prediction</div>
            </div>
          </div>
        </div>

        {/* Main Navigation */}
        <div className="flex-1 p-3">
          <nav className="space-y-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveNav(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activeNav === item.id
                    ? "bg-purple-600 text-white shadow-lg"
                    : "text-gray-400 hover:text-white hover:bg-gray-800"
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </nav>

          {/* Quick Links Section */}
          <div className="mt-8">
            <div className="px-3 mb-2">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Quick Access</h3>
            </div>
            <div className="space-y-1">
              {quickLinks.map((link, index) => (
                <button
                  key={index}
                  className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                >
                  <span>{link.label}</span>
                  <span className={`text-xs font-semibold ${link.color}`}>{link.count}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Spaces Section */}
          <div className="mt-8">
            <div className="px-3 mb-2 flex items-center justify-between">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Airports</h3>
              <button className="text-gray-500 hover:text-gray-400 text-lg">+</button>
            </div>
            <div className="space-y-1">
              <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors text-left">
                <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                <span>All Airports</span>
              </button>
              <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors text-left">
                <span className="w-2 h-2 rounded-full bg-green-500"></span>
                <span>Kuala Lumpur (KUL)</span>
              </button>
              <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors text-left">
                <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                <span>Singapore (SIN)</span>
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Actions */}
        <div className="p-3 border-t border-gray-800 dark:border-gray-800 space-y-2">
          <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors">
            <span>⬆️</span>
            <span>Upgrade</span>
          </button>
          <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors">
            <span>👤</span>
            <span>Invite Team</span>
          </button>
        </div>
      </div>
    )
  }

  // For Cargo Analytics pages, use CSS version
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
