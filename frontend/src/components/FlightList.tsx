import React, { useState, useEffect } from 'react'
import { FlightListItem } from './FlightListItem'
import { FlightDetails } from '../types'
import { getCargoFlights } from '../api/cargoService'
import './FlightList.css'

interface FlightListProps {
  onFlightClick: (flightId: string) => void
  groupBy?: 'status' | 'destination' | 'airline' | 'date'
}

export const FlightList: React.FC<FlightListProps> = ({ onFlightClick, groupBy = 'status' }) => {
  const [flights, setFlights] = useState<FlightDetails[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set())
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  useEffect(() => {
    const fetchFlights = async () => {
      try {
        setLoading(true)
        const data = await getCargoFlights()
        setFlights(data)
        // Expand all groups by default
        const groups = getGroupedFlights(data, groupBy)
        setExpandedGroups(new Set(Object.keys(groups)))
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load flights')
      } finally {
        setLoading(false)
      }
    }

    fetchFlights()
  }, [groupBy])

  const getGroupedFlights = (flightList: FlightDetails[], groupKey: string) => {
    const grouped: Record<string, FlightDetails[]> = {}

    flightList.forEach((flight) => {
      let key: string
      switch (groupKey) {
        case 'status':
          key = flight.flight_status.toUpperCase()
          break
        case 'destination':
          key = flight.destination_airport_code
          break
        case 'airline':
          key = flight.airline_name
          break
        case 'date':
          try {
            const date = new Date(flight.scheduled_departure)
            key = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
          } catch {
            key = 'Unknown'
          }
          break
        default:
          key = 'Other'
      }

      if (!grouped[key]) {
        grouped[key] = []
      }
      grouped[key].push(flight)
    })

    return grouped
  }

  const toggleGroup = (groupName: string) => {
    const newExpanded = new Set(expandedGroups)
    if (newExpanded.has(groupName)) {
      newExpanded.delete(groupName)
    } else {
      newExpanded.add(groupName)
    }
    setExpandedGroups(newExpanded)
  }

  const filteredFlights = flights.filter((flight) => {
    const matchesSearch =
      flight.flight_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      flight.origin_airport_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      flight.destination_airport_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      flight.airline_name.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesStatus = filterStatus === 'all' || flight.flight_status === filterStatus

    return matchesSearch && matchesStatus
  })

  const groupedFlights = getGroupedFlights(filteredFlights, groupBy)

  const getGroupColor = (groupName: string) => {
    // Use CSS variables for colors that work in both light and dark mode
    const root = document.documentElement
    const getCSSVar = (varName: string, fallback: string) => {
      return getComputedStyle(root).getPropertyValue(varName).trim() || fallback
    }
    
    const statusColors: Record<string, string> = {
      SCHEDULED: getCSSVar('--color-status-blue', '#3b82f6'),
      DEPARTED: getCSSVar('--color-status-purple', '#8b5cf6'),
      IN_PROGRESS: getCSSVar('--color-status-purple', '#8b5cf6'),
      ARRIVED: getCSSVar('--color-status-green', '#10b981'),
      COMPLETED: getCSSVar('--color-status-green', '#10b981'),
      DELAYED: getCSSVar('--color-status-orange', '#f59e0b'),
      CANCELLED: getCSSVar('--color-status-red', '#ef4444'),
    }
    return statusColors[groupName] || getCSSVar('--color-status-gray', '#6b7280')
  }

  if (loading) {
    return (
      <div className="flight-list-loading">
        <div className="spinner"></div>
        <p>Loading flights...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flight-list-error">
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    )
  }

  return (
    <div className="flight-list-container">
      <div className="flight-list-controls" role="toolbar" aria-label="Flight list controls">
        <div className="controls-left">
          <label htmlFor="group-selector" className="sr-only">
            Group flights by
          </label>
          <select
            id="group-selector"
            className="group-selector"
            value={groupBy}
            onChange={(e) => {
              const newGroupBy = e.target.value as 'status' | 'destination' | 'airline' | 'date'
              const groups = getGroupedFlights(filteredFlights, newGroupBy)
              setExpandedGroups(new Set(Object.keys(groups)))
            }}
            aria-label="Group flights by"
          >
            <option value="status">Group: Status</option>
            <option value="destination">Group: Destination</option>
            <option value="airline">Group: Airline</option>
            <option value="date">Group: Date</option>
          </select>
        </div>
        <div className="controls-right">
          <label htmlFor="flight-search-input" className="sr-only">
            Search flights
          </label>
          <input
            id="flight-search-input"
            type="search"
            className="search-input"
            placeholder="Search flights..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search flights"
          />
          <label htmlFor="status-filter-selector" className="sr-only">
            Filter by status
          </label>
          <select
            id="status-filter-selector"
            className="filter-selector"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            aria-label="Filter flights by status"
          >
            <option value="all">All Status</option>
            <option value="scheduled">Scheduled</option>
            <option value="departed">Departed</option>
            <option value="in_progress">In Progress</option>
            <option value="arrived">Arrived</option>
            <option value="delayed">Delayed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      <div className="flight-list-groups">
        {Object.entries(groupedFlights)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([groupName, groupFlights]) => (
            <div key={groupName} className="flight-group">
              <header
                className="flight-group-header"
                onClick={() => toggleGroup(groupName)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    toggleGroup(groupName)
                  }
                }}
                style={{ borderLeftColor: getGroupColor(groupName) }}
                role="button"
                tabIndex={0}
                aria-label={`${expandedGroups.has(groupName) ? 'Collapse' : 'Expand'} ${groupName} group`}
                aria-expanded={expandedGroups.has(groupName)}
              >
                <div className="group-header-left">
                  <span className="group-toggle" aria-hidden="true">
                    {expandedGroups.has(groupName) ? '▼' : '▶'}
                  </span>
                  <h3 className="group-name">{groupName}</h3>
                  <span className="group-count" aria-label={`${groupFlights.length} flights`}>
                    ({groupFlights.length})
                  </span>
                </div>
              </header>
              {expandedGroups.has(groupName) && (
                <div className="flight-group-items">
                  {groupFlights.map((flight) => (
                    <FlightListItem
                      key={flight.id}
                      flight={flight}
                      onClick={onFlightClick}
                    />
                  ))}
                </div>
              )}
            </div>
          ))}
      </div>
    </div>
  )
}
