import React from 'react'
import { useNavigate } from 'react-router-dom'
import { FlightList } from '../components/FlightList'
import './CargoAnalyticsDashboard.css'

const CargoAnalyticsDashboard: React.FC = () => {
  const navigate = useNavigate()

  const handleFlightClick = (flightId: string) => {
    navigate(`/cargo-analytics/${flightId}`)
  }

  return (
    <div className="cargo-dashboard">
      <div className="dashboard-view-tabs">
        <button className="view-tab active">List</button>
        <button className="view-tab">Board</button>
        <button className="view-tab">Timeline</button>
        <button className="view-tab">Table</button>
        <button className="view-tab">Map</button>
        <button className="view-tab">+ View</button>
      </div>
      <FlightList onFlightClick={handleFlightClick} />
    </div>
  )
}

export default CargoAnalyticsDashboard
