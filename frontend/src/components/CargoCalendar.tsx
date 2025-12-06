import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, getDay, startOfWeek, endOfWeek } from 'date-fns'
import { getCargoCalendar, CargoCalendarResponse } from '../api/cargoService'
import './CargoCalendar.css'

interface CalendarDay {
  date: Date
  flights: CargoCalendarResponse['flights']
  peakSeason?: {
    type: 'holiday' | 'school_holiday' | 'peak_season'
    multiplier: number
    is_holiday: boolean
    is_school_holiday: boolean
  }
}

const CargoCalendar: React.FC = () => {
  const navigate = useNavigate()
  const [currentDate, setCurrentDate] = useState(new Date())
  const [calendarData, setCalendarData] = useState<CargoCalendarResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchCalendar = async () => {
      try {
        setLoading(true)
        setError(null)
        const year = currentDate.getFullYear()
        const month = currentDate.getMonth() + 1
        const data = await getCargoCalendar(year, month)
        
        // Debug: Log the response
        console.log(`Calendar data for ${year}-${month}:`, {
          flightsCount: data.flights.length,
          year: data.year,
          month: data.month,
          peakSeasonsCount: data.peak_seasons.length,
          sampleFlights: data.flights.slice(0, 5).map(f => ({
            flight_number: f.flight_number,
            date: f.date,
            scheduled_departure: f.scheduled_departure,
            origin: f.origin,
            destination: f.destination
          }))
        })
        
        // If backend auto-navigated to a different month, update currentDate to match
        if (data.year !== year || data.month !== month) {
          console.log(`Calendar auto-navigated: requested ${year}-${month}, got ${data.year}-${data.month}`)
          // Update currentDate to match what backend returned to prevent loops
          const newDate = new Date(data.year, data.month - 1, 1)
          // Only update if it's actually different to avoid infinite loops
          if (newDate.getFullYear() !== currentDate.getFullYear() || 
              newDate.getMonth() !== currentDate.getMonth()) {
            setCurrentDate(newDate)
          }
        }
        
        setCalendarData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load calendar')
        console.error('Error fetching calendar:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchCalendar()
  }, [currentDate])

  const handlePreviousMonth = () => {
    setCurrentDate(subMonths(currentDate, 1))
  }

  const handleNextMonth = () => {
    setCurrentDate(addMonths(currentDate, 1))
  }

  const handleToday = () => {
    setCurrentDate(new Date())
  }

  const getUtilizationColor = (utilization: number): string => {
    if (utilization >= 80) return 'high'
    if (utilization >= 60) return 'medium'
    if (utilization >= 40) return 'low-medium'
    return 'low'
  }

  const getRiskColor = (risk: string): string => {
    switch (risk.toLowerCase()) {
      case 'high':
        return 'high-risk'
      case 'medium':
        return 'medium-risk'
      default:
        return 'low-risk'
    }
  }

  if (loading) {
    return (
      <div className="cargo-calendar-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading calendar...</p>
        </div>
      </div>
    )
  }

  if (error || !calendarData) {
    return (
      <div className="cargo-calendar-container">
        <div className="error-message" role="alert">
          <h2>Error</h2>
          <p>{error || 'No data available'}</p>
          <button onClick={() => window.location.reload()} type="button">
            Retry
          </button>
        </div>
      </div>
    )
  }

  // Build calendar days
  const monthStart = startOfMonth(currentDate)
  const monthEnd = endOfMonth(currentDate)
  const calendarStart = startOfWeek(monthStart, { weekStartsOn: 0 })
  const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 0 })
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd })

  // Create a map of date to flights and peak seasons
  const dateMap = new Map<string, CalendarDay>()
  
  days.forEach(day => {
    const dateKey = format(day, 'yyyy-MM-dd')
    // Match flights by date - handle both date string and full datetime
    const dayFlights = calendarData.flights.filter(f => {
      // f.date should be in 'yyyy-MM-dd' format from API
      // But also check scheduled_departure in case date format differs
      const flightDate = f.date || (f.scheduled_departure ? f.scheduled_departure.split('T')[0] : null)
      return flightDate === dateKey
    })
    
    // Debug: Log first few matches
    if (dayFlights.length > 0 && dayFlights.length <= 3) {
      dayFlights.slice(0, 3).forEach(f => {
        const flightDate = f.date || (f.scheduled_departure ? f.scheduled_departure.split('T')[0] : null)
        console.log(`Matched flight ${f.flight_number} to date ${dateKey}`, { flightDate, dateKey })
      })
    }
    
    // Find peak season for this day
    const peakSeason = calendarData.peak_seasons.find(p => p.date === dateKey)
    
    dateMap.set(dateKey, {
      date: day,
      flights: dayFlights,
      peakSeason: peakSeason ? {
        type: peakSeason.type,
        multiplier: peakSeason.multiplier,
        is_holiday: peakSeason.is_holiday,
        is_school_holiday: peakSeason.is_school_holiday,
      } : undefined
    })
  })

  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

  // Calculate statistics
  const highUtilizationFlights = calendarData.flights.filter(f => f.utilization_percentage >= 80).length
  const highRiskFlights = calendarData.flights.filter(f => f.overbooking_risk === 'high').length
  const totalAvailableWeight = calendarData.flights.reduce((sum, f) => sum + f.available_weight_kg, 0) / 1000 // tonnes
  const avgTrafficMultiplier = calendarData.flights.length > 0
    ? calendarData.flights.reduce((sum, f) => sum + f.traffic_estimation.traffic_multiplier, 0) / calendarData.flights.length
    : 1.0

  return (
    <div className="cargo-calendar-container">
      <div className="calendar-layout">
        {/* Left Sidebar - Insights */}
        <aside className="calendar-sidebar left">
          <div className="sidebar-section">
            <h3 className="sidebar-title">📊 Insights</h3>
            <div className="insight-card">
              <div className="insight-label">High Utilization Days</div>
              <div className="insight-value">{highUtilizationFlights}</div>
              <div className="insight-desc">Flights ≥80% capacity</div>
            </div>
            <div className="insight-card">
              <div className="insight-label">High Risk Flights</div>
              <div className="insight-value risk">{highRiskFlights}</div>
              <div className="insight-desc">Overbooking risk</div>
            </div>
            <div className="insight-card">
              <div className="insight-label">Total Available</div>
              <div className="insight-value">{totalAvailableWeight.toFixed(1)}t</div>
              <div className="insight-desc">Cargo capacity</div>
            </div>
            <div className="insight-card">
              <div className="insight-label">Traffic Multiplier</div>
              <div className="insight-value">{avgTrafficMultiplier.toFixed(2)}x</div>
              <div className="insight-desc">Avg peak season factor</div>
            </div>
          </div>

          <div className="sidebar-section">
            <h3 className="sidebar-title">🎯 Quick Filters</h3>
            <div className="filter-group">
              <button className="filter-btn active">All Flights</button>
              <button className="filter-btn">High Risk</button>
              <button className="filter-btn">Peak Season</button>
              <button className="filter-btn">Weekends</button>
            </div>
          </div>

          <div className="sidebar-section">
            <h3 className="sidebar-title">📅 Peak Seasons</h3>
            <div className="peak-season-list">
              {calendarData.peak_seasons.slice(0, 5).map((peak, idx) => (
                <div key={idx} className="peak-season-item">
                  <span className="peak-date">{peak.day}</span>
                  <span className="peak-type">{peak.type.replace('_', ' ')}</span>
                  <span className="peak-multiplier">{peak.multiplier.toFixed(1)}x</span>
                </div>
              ))}
              {calendarData.peak_seasons.length > 5 && (
                <div className="peak-season-more">
                  +{calendarData.peak_seasons.length - 5} more days
                </div>
              )}
            </div>
          </div>
        </aside>

        {/* Main Calendar Area */}
        <div className="calendar-main">
          <div className="calendar-header">
            <div className="calendar-controls">
              <button onClick={handlePreviousMonth} className="nav-button" aria-label="Previous month">
                ←
              </button>
              <h2 className="calendar-title">
                {format(currentDate, 'MMMM yyyy')}
              </h2>
              <button onClick={handleNextMonth} className="nav-button" aria-label="Next month">
                →
              </button>
              <button onClick={handleToday} className="today-button">
                Today
              </button>
            </div>
            <div className="calendar-legend">
              <div className="legend-item">
                <span className="legend-color peak-holiday"></span>
                <span>Holiday</span>
              </div>
              <div className="legend-item">
                <span className="legend-color peak-school"></span>
                <span>School Holiday</span>
              </div>
              <div className="legend-item">
                <span className="legend-color peak-season"></span>
                <span>Peak Season</span>
              </div>
              <div className="legend-item">
                <span className="legend-color utilization-high"></span>
                <span>High (≥80%)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color utilization-medium"></span>
                <span>Medium (60-79%)</span>
              </div>
            </div>
          </div>

          <div className="calendar-grid">
        <div className="calendar-weekdays">
          {weekDays.map(day => (
            <div key={day} className="weekday-header">
              {day}
            </div>
          ))}
        </div>
        <div className="calendar-days">
          {days.map(day => {
            const dayData = dateMap.get(format(day, 'yyyy-MM-dd'))
            const isCurrentMonth = isSameMonth(day, currentDate)
            const isToday = isSameDay(day, new Date())
            const flights = dayData?.flights || []
            const peakSeason = dayData?.peakSeason

            return (
              <div
                key={day.toISOString()}
                className={`calendar-day ${!isCurrentMonth ? 'other-month' : ''} ${isToday ? 'today' : ''} ${peakSeason ? `peak-${peakSeason.type}` : ''}`}
              >
                <div className="day-number">{format(day, 'd')}</div>
                {peakSeason && (
                  <div className={`peak-indicator ${peakSeason.type}`}>
                    {peakSeason.is_holiday && '🎉'}
                    {peakSeason.is_school_holiday && !peakSeason.is_holiday && '🎓'}
                    {peakSeason.type === 'peak_season' && !peakSeason.is_holiday && !peakSeason.is_school_holiday && '📈'}
                  </div>
                )}
                <div className="day-flights">
                  {flights.map(flight => {
                    const utilization = flight.utilization_percentage || 0
                    const risk = flight.overbooking_risk || 'low'
                    return (
                      <div
                        key={flight.flight_id}
                        className={`flight-item ${getUtilizationColor(utilization)} ${getRiskColor(risk)}`}
                        onClick={() => navigate(`/cargo-analytics/${flight.flight_id}`)}
                        title={`${flight.flight_number}: ${flight.origin}→${flight.destination} - ${utilization.toFixed(1)}% utilized`}
                      >
                        <div className="flight-number">{flight.flight_number}</div>
                        <div className="flight-route">{flight.origin}→{flight.destination}</div>
                        <div className="flight-utilization">{utilization.toFixed(0)}%</div>
                        {risk === 'high' && <div className="risk-badge high">⚠️</div>}
                      </div>
                    )
                  })}
                </div>
                {flights.length > 3 && (
                  <div className="more-flights">+{flights.length - 3} more</div>
                )}
              </div>
            )
          })}
          </div>
        </div>
        </div>

        {/* Right Sidebar - Statistics */}
        <aside className="calendar-sidebar right">
          <div className="sidebar-section">
            <h3 className="sidebar-title">📈 Statistics</h3>
            <div className="stat-card">
              <div className="stat-label">Total Flights</div>
              <div className="stat-value">{calendarData.flights.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Peak Season Days</div>
              <div className="stat-value">{calendarData.peak_seasons.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Avg Utilization</div>
              <div className="stat-value">
                {calendarData.flights.length > 0
                  ? (calendarData.flights.reduce((sum, f) => sum + f.utilization_percentage, 0) / calendarData.flights.length).toFixed(1)
                  : '0'}%
              </div>
            </div>
          </div>

          <div className="sidebar-section">
            <h3 className="sidebar-title">🔍 Top Routes</h3>
            <div className="route-list">
              {Array.from(
                new Map(
                  calendarData.flights.map(f => [f.route, calendarData.flights.filter(fl => fl.route === f.route).length])
                ).entries()
              )
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([route, count]) => (
                  <div key={route} className="route-item">
                    <span className="route-code">{route}</span>
                    <span className="route-count">{count} flights</span>
                  </div>
                ))}
            </div>
          </div>

          <div className="sidebar-section">
            <h3 className="sidebar-title">⚠️ Risk Alerts</h3>
            <div className="alert-list">
              {calendarData.flights
                .filter(f => f.overbooking_risk === 'high')
                .slice(0, 5)
                .map(flight => (
                  <div
                    key={flight.flight_id}
                    className="alert-item high"
                    onClick={() => navigate(`/cargo-analytics/${flight.flight_id}`)}
                  >
                    <div className="alert-flight">{flight.flight_number}</div>
                    <div className="alert-route">{flight.origin}→{flight.destination}</div>
                    <div className="alert-util">{flight.utilization_percentage.toFixed(0)}%</div>
                  </div>
                ))}
              {highRiskFlights === 0 && (
                <div className="alert-item none">No high-risk flights</div>
              )}
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}

export default CargoCalendar
