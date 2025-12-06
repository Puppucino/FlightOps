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
    <main className="cargo-dashboard" role="main">
      <FlightList onFlightClick={handleFlightClick} />
    </main>
  )
}

export default CargoAnalyticsDashboard
