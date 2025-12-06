import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card } from '../components/Card'
import { ProgressBar } from '../components/ProgressBar'
import { StatCard } from '../components/StatCard'
import { getCargoAnalytics, getCargoAnalyticsByFlightNumber, getCargoFlights } from '../api/cargoService'
import { CargoAnalyticsData, FlightDetails } from '../types'
import { format, parseISO } from 'date-fns'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import './CargoAnalytics.css'

const CargoAnalytics: React.FC = () => {
  const { flightId, flightNumber } = useParams<{ flightId?: string; flightNumber?: string }>()
  const navigate = useNavigate()
  const [analyticsData, setAnalyticsData] = useState<CargoAnalyticsData | null>(null)
  const [availableFlights, setAvailableFlights] = useState<FlightDetails[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Fetch available flights
        const flights = await getCargoFlights()
        setAvailableFlights(flights)

        // Fetch analytics data
        let data: CargoAnalyticsData
        if (flightId) {
          data = await getCargoAnalytics(flightId)
        } else if (flightNumber) {
          data = await getCargoAnalyticsByFlightNumber(flightNumber)
        } else if (flights.length > 0) {
          // Default to first flight if no ID provided
          data = await getCargoAnalytics(flights[0].id)
        } else {
          throw new Error('No flights available')
        }

        setAnalyticsData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load cargo analytics')
        console.error('Error fetching cargo analytics:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [flightId, flightNumber])


  if (loading) {
    return (
      <div className="cargo-analytics-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading cargo analytics...</p>
        </div>
      </div>
    )
  }

  if (error || !analyticsData) {
    return (
      <div className="cargo-analytics-container">
        <div className="error-message">
          <h2>Error</h2>
          <p>{error || 'No data available'}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    )
  }

  const { flight, storage_availability, loading_progress, prediction } = analyticsData

  // Prepare chart data
  const storageData = [
    { name: 'Used', value: storage_availability.current_cargo_tonnes, color: '#3b82f6' },
    { name: 'Available', value: storage_availability.available_capacity_tonnes, color: '#10b981' },
  ]

  const utilizationData = [
    { time: '00:00', utilization: 45 },
    { time: '04:00', utilization: 52 },
    { time: '08:00', utilization: 68 },
    { time: '12:00', utilization: storage_availability.utilization_percentage },
    { time: '16:00', utilization: storage_availability.utilization_percentage + 5 },
    { time: '20:00', utilization: storage_availability.utilization_percentage + 10 },
  ]

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'arrived':
        return 'success'
      case 'in_progress':
      case 'departed':
        return 'primary'
      case 'delayed':
        return 'warning'
      case 'cancelled':
        return 'danger'
      default:
        return 'primary'
    }
  }

  const formatDate = (dateString: string) => {
    try {
      return format(parseISO(dateString), 'MMM dd, yyyy HH:mm')
    } catch {
      return dateString
    }
  }

  return (
    <div className="cargo-analytics-container">
      <div className="cargo-analytics-header">
        <button className="back-to-list-btn" onClick={() => navigate('/cargo-analytics')}>
          ← Back to List
        </button>
        {availableFlights.length > 0 && (
          <select
            className="flight-selector"
            value={analyticsData?.flight.id || ''}
            onChange={(e) => navigate(`/cargo-analytics/${e.target.value}`)}
          >
            {availableFlights.map((f) => (
              <option key={f.id} value={f.id}>
                {f.flight_number} - {f.origin_airport_code} → {f.destination_airport_code}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Flight Details Section */}
      <Card title="Flight Details" icon="✈️" className="flight-details-card">
        <div className="flight-details-grid">
          <div className="flight-detail-item">
            <span className="detail-label">Flight Number</span>
            <span className="detail-value">{flight.flight_number}</span>
          </div>
          <div className="flight-detail-item">
            <span className="detail-label">Airline</span>
            <span className="detail-value">{flight.airline_name}</span>
          </div>
          <div className="flight-detail-item">
            <span className="detail-label">Aircraft</span>
            <span className="detail-value">
              {flight.aircraft_registration} ({flight.aircraft_type})
            </span>
          </div>
          <div className="flight-detail-item">
            <span className="detail-label">Route</span>
            <span className="detail-value route">
              {flight.origin_airport_code} → {flight.destination_airport_code}
            </span>
          </div>
          <div className="flight-detail-item">
            <span className="detail-label">Distance</span>
            <span className="detail-value">{flight.distance_km.toLocaleString()} km</span>
          </div>
          <div className="flight-detail-item">
            <span className="detail-label">Status</span>
            <span className={`detail-value status status-${getStatusColor(flight.flight_status)}`}>
              {flight.flight_status.toUpperCase()}
            </span>
          </div>
          <div className="flight-detail-item">
            <span className="detail-label">Scheduled Departure</span>
            <span className="detail-value">{formatDate(flight.scheduled_departure)}</span>
          </div>
          <div className="flight-detail-item">
            <span className="detail-label">Scheduled Arrival</span>
            <span className="detail-value">{formatDate(flight.scheduled_arrival)}</span>
          </div>
        </div>
      </Card>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <StatCard
          label="Storage Utilization"
          value={storage_availability.utilization_percentage}
          unit="%"
          icon="📦"
          color="blue"
        />
        <StatCard
          label="Available Capacity"
          value={storage_availability.available_capacity_tonnes}
          unit="tonnes"
          icon="📊"
          color="green"
        />
        <StatCard
          label="Loading Progress"
          value={loading_progress.loading_percentage}
          unit="%"
          icon="⚡"
          color="yellow"
        />
        <StatCard
          label="Predicted Demand"
          value={prediction.predicted_cargo_volume}
          unit="tonnes"
          icon="🔮"
          color="purple"
          trend="up"
          trendValue={`${(prediction.confidence * 100).toFixed(0)}% confidence`}
        />
      </div>

      {/* Storage Availability Section */}
      <div className="analytics-grid">
        <Card title="Storage Availability" icon="📦" className="storage-card">
          <div className="storage-info">
            <div className="storage-metrics">
              <div className="metric">
                <span className="metric-label">Total Capacity</span>
                <span className="metric-value">
                  {storage_availability.total_capacity_tonnes.toFixed(2)} tonnes
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Current Cargo</span>
                <span className="metric-value">
                  {storage_availability.current_cargo_tonnes.toFixed(2)} tonnes
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Available</span>
                <span className="metric-value available">
                  {storage_availability.available_capacity_tonnes.toFixed(2)} tonnes
                </span>
              </div>
            </div>
            <ProgressBar
              value={storage_availability.utilization_percentage}
              label="Storage Utilization"
              color={storage_availability.utilization_percentage > 80 ? 'warning' : 'primary'}
              size="large"
            />
            <div className="pie-chart-container">
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={storageData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {storageData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      color: '#111827',
                    }}
                    formatter={(value: number) => `${value.toFixed(2)} tonnes`}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </Card>

        {/* Cargo Loading Progress Section */}
        <Card title="Cargo Loading Progress" icon="⚡" className="loading-card">
          <div className="loading-info">
            <div className="loading-status">
              <span className={`status-badge status-${getStatusColor(loading_progress.status)}`}>
                {loading_progress.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <ProgressBar
              value={loading_progress.loading_percentage}
              label="Loading Progress"
              color={getStatusColor(loading_progress.status) as any}
              size="large"
            />
            <div className="loading-details">
              <div className="detail-row">
                <span>Loaded:</span>
                <span className="value">
                  {loading_progress.loaded_cargo_tonnes.toFixed(2)} / {loading_progress.total_cargo_tonnes.toFixed(2)} tonnes
                </span>
              </div>
              <div className="detail-row">
                <span>Remaining:</span>
                <span className="value">
                  {(loading_progress.total_cargo_tonnes - loading_progress.loaded_cargo_tonnes).toFixed(2)} tonnes
                </span>
              </div>
              {loading_progress.estimated_completion_time && (
                <div className="detail-row">
                  <span>Est. Completion:</span>
                  <span className="value">{formatDate(loading_progress.estimated_completion_time)}</span>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>

      {/* Utilization Trend Chart */}
      <Card title="Storage Utilization Trend" icon="📈" className="trend-card">
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={utilizationData}>
            <defs>
              <linearGradient id="colorUtilization" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="time" stroke="#6b7280" />
            <YAxis stroke="#6b7280" domain={[0, 100]} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                color: '#111827',
              }}
              formatter={(value: number) => [`${value.toFixed(1)}%`, 'Utilization']}
            />
            <Area
              type="monotone"
              dataKey="utilization"
              stroke="#3b82f6"
              fillOpacity={1}
              fill="url(#colorUtilization)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* Prediction Section */}
      <Card title="Cargo Demand Prediction" icon="🔮" className="prediction-card">
        <div className="prediction-info">
          <div className="prediction-value">
            <span className="prediction-label">Predicted Cargo Volume</span>
            <span className="prediction-number">
              {prediction.predicted_cargo_volume.toFixed(2)} tonnes
            </span>
          </div>
          <div className="confidence-indicator">
            <span className="confidence-label">Confidence Score</span>
            <ProgressBar
              value={prediction.confidence * 100}
              color="purple"
              size="medium"
            />
            <span className="confidence-value">{(prediction.confidence * 100).toFixed(1)}%</span>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default CargoAnalytics
