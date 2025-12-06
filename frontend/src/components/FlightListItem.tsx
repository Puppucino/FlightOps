import React from 'react'
import { FlightDetails } from '../types'
import { format, parseISO } from 'date-fns'
import './FlightListItem.css'

interface FlightListItemProps {
  flight: FlightDetails
  onClick: (flightId: string) => void
}

export const FlightListItem: React.FC<FlightListItemProps> = ({ flight, onClick }) => {
  const formatDate = (dateString: string) => {
    try {
      const date = parseISO(dateString)
      const now = new Date()
      const diffHours = (date.getTime() - now.getTime()) / (1000 * 60 * 60)
      
      if (diffHours < 24 && diffHours > 0) {
        if (diffHours < 1) return 'In < 1h'
        return `In ${Math.floor(diffHours)}h`
      }
      if (diffHours < 0 && diffHours > -24) {
        return 'Today'
      }
      return format(date, 'MMM dd')
    } catch {
      return dateString
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'scheduled':
        return 'blue'
      case 'departed':
      case 'in_progress':
        return 'purple'
      case 'arrived':
      case 'completed':
        return 'green'
      case 'delayed':
        return 'orange'
      case 'cancelled':
        return 'red'
      default:
        return 'gray'
    }
  }

  const getPriority = (flight: FlightDetails) => {
    // Determine priority based on flight status and time
    if (flight.flight_status === 'delayed') return 'urgent'
    if (flight.flight_status === 'cancelled') return 'high'
    const hoursUntilDeparture = (parseISO(flight.scheduled_departure).getTime() - new Date().getTime()) / (1000 * 60 * 60)
    if (hoursUntilDeparture < 2) return 'high'
    if (hoursUntilDeparture < 12) return 'normal'
    return 'low'
  }

  const priority = getPriority(flight)
  const statusColor = getStatusColor(flight.flight_status)

  return (
    <div className="flight-list-item" onClick={() => onClick(flight.id)}>
      <div className="flight-item-main">
        <div className="flight-name-section">
          <span className="flight-number">{flight.flight_number}</span>
          <span className="flight-route">
            {flight.origin_airport_code} → {flight.destination_airport_code}
          </span>
          <div className="flight-tags">
            <span className="tag tag-type">{flight.flight_type}</span>
            <span className={`tag tag-status tag-${statusColor}`}>
              {flight.flight_status}
            </span>
          </div>
        </div>
        <div className="flight-item-details">
          <div className="flight-detail-item">
            <span className="detail-label">Aircraft</span>
            <span className="detail-value">{flight.aircraft_registration}</span>
          </div>
          <div className="flight-detail-item">
            <span className="detail-label">Airline</span>
            <span className="detail-value">{flight.airline_name}</span>
          </div>
          <div className="flight-detail-item">
            <span className="detail-label">Distance</span>
            <span className="detail-value">{flight.distance_km.toLocaleString()} km</span>
          </div>
        </div>
      </div>
      <div className="flight-item-meta">
        <div className="flight-assignee">
          <div className="assignee-avatar">{flight.airline_name.charAt(0)}</div>
        </div>
        <div className="flight-date">
          <span className="date-text">{formatDate(flight.scheduled_departure)}</span>
        </div>
        <div className={`flight-priority priority-${priority}`}>
          {priority === 'urgent' && '🔴'}
          {priority === 'high' && '🟠'}
          {priority === 'normal' && '🟡'}
          {priority === 'low' && '🟢'}
          <span className="priority-text">{priority}</span>
        </div>
      </div>
    </div>
  )
}
