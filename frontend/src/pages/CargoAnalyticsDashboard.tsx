import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FlightList } from '../components/FlightList'
import CargoCalendar from '../components/CargoCalendar'
import './CargoAnalyticsDashboard.css'

const CargoAnalyticsDashboard: React.FC = () => {
  const navigate = useNavigate()
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar')

  const handleFlightClick = (flightId: string) => {
    navigate(`/cargo-analytics/${flightId}`)
  }

  return (
    <main className="cargo-dashboard" role="main">
      <div className="dashboard-header">
        <h1>Cargo Analytics</h1>
        <div className="view-toggle">
          <button
            className={viewMode === 'calendar' ? 'active' : ''}
            onClick={() => setViewMode('calendar')}
            type="button"
          >
            📅 Calendar View
          </button>
          <button
            className={viewMode === 'list' ? 'active' : ''}
            onClick={() => setViewMode('list')}
            type="button"
          >
            📋 List View
          </button>
        </div>
      </div>
      {viewMode === 'calendar' ? (
        <CargoCalendar />
      ) : (
      <FlightList onFlightClick={handleFlightClick} />
      )}
    </main>
  )
}

export default CargoAnalyticsDashboard
