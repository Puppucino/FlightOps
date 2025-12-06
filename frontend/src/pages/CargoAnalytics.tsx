import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card } from '../components/Card'
import { ProgressBar } from '../components/ProgressBar'
import { StatCard } from '../components/StatCard'
import { getCargoAnalytics, getCargoAnalyticsByFlightNumber, getCargoFlights, getCargoAnalyticsWithPrediction } from '../api/cargoService'
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
  const [daysBeforeFlight, setDaysBeforeFlight] = useState<number>(0)
  const [predictionData, setPredictionData] = useState<any>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Fetch available flights
        const flights = await getCargoFlights()
        setAvailableFlights(flights)

        // Fetch analytics data with prediction support
        let data: CargoAnalyticsData
        if (flightId) {
          data = await getCargoAnalyticsWithPrediction(flightId, daysBeforeFlight)
        } else if (flightNumber) {
          data = await getCargoAnalyticsByFlightNumber(flightNumber)
        } else if (flights.length > 0) {
          // Default to first flight if no ID provided
          data = await getCargoAnalyticsWithPrediction(flights[0].id, daysBeforeFlight)
        } else {
          throw new Error('No flights available')
        }

        setAnalyticsData(data)
        
        // Extract prediction data if available - always set it if prediction exists
        if (data.prediction && typeof data.prediction === 'object') {
          setPredictionData(data.prediction)
        } else if (data.storage_availability) {
          // If no prediction object but we have storage_availability, create a minimal predictionData
          setPredictionData({
            available_weight_kg: (data.storage_availability.available_capacity_tonnes || 0) * 1000,
            available_volume_m3: 0,
            constraining_factor: 'weight',
            overbooking_risk: 'low'
          })
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load cargo analytics')
        console.error('Error fetching cargo analytics:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [flightId, flightNumber, daysBeforeFlight])


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
      <main className="cargo-analytics-container" role="main">
        <div className="error-message" role="alert">
          <h2>Error</h2>
          <p>{error || 'No data available'}</p>
          <button 
            onClick={() => window.location.reload()}
            aria-label="Retry loading cargo analytics"
            type="button"
          >
            Retry
          </button>
        </div>
      </main>
    )
  }

  const { flight, storage_availability, loading_progress, prediction } = analyticsData
  
  // Safe fallback for loading_progress if missing
  const safeLoadingProgress = loading_progress || {
    flight_id: flight?.id || '',
    flight_number: flight?.flight_number || '',
    total_cargo_tonnes: storage_availability?.total_capacity_tonnes || 0,
    loaded_cargo_tonnes: storage_availability?.current_cargo_tonnes || 0,
    loading_percentage: storage_availability?.utilization_percentage || 0,
    status: 'not_started' as const
  }
  
  // Safe fallback for prediction if missing
  const safePrediction = prediction || {
    predicted_cargo_volume: 0,
    confidence: 0
  }

  // Prepare chart data - Using CSS variables via getComputedStyle for dynamic colors
  const getChartColors = () => {
    const root = document.documentElement
    const blue = getComputedStyle(root).getPropertyValue('--color-status-blue').trim() || '#3B82F6'
    const green = getComputedStyle(root).getPropertyValue('--color-status-green').trim() || '#10B981'
    return { blue, green }
  }
  
  const chartColors = getChartColors()
  const storageData = [
    { name: 'Used', value: storage_availability.current_cargo_tonnes, color: chartColors.blue },
    { name: 'Available', value: storage_availability.available_capacity_tonnes, color: chartColors.green },
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
    <main className="cargo-analytics-container" role="main">
      <header className="cargo-analytics-header">
        <button 
          className="back-to-list-btn" 
          onClick={() => navigate('/cargo-analytics')}
          aria-label="Go back to cargo analytics list"
          type="button"
        >
          ← Back to List
        </button>
        {availableFlights.length > 0 && (
          <label htmlFor="flight-selector" className="sr-only">
            Select flight
          </label>
        )}
        {availableFlights.length > 0 && (
          <select
            id="flight-selector"
            className="flight-selector"
            value={analyticsData?.flight.id || ''}
            onChange={(e) => navigate(`/cargo-analytics/${e.target.value}`)}
            aria-label="Select flight to view analytics"
          >
            {availableFlights.map((f) => (
              <option key={f.id} value={f.id}>
                {f.flight_number} - {f.origin_airport_code} → {f.destination_airport_code}
              </option>
            ))}
          </select>
        )}
        <div className="prediction-controls">
          <label htmlFor="days-before-flight" className="days-label">
            Predict Capacity:
          </label>
          <select
            id="days-before-flight"
            className="days-selector"
            value={daysBeforeFlight}
            onChange={(e) => setDaysBeforeFlight(Number(e.target.value))}
            aria-label="Select days before flight for prediction"
          >
            <option value={0}>Day of Flight</option>
            <option value={1}>1 Day Before</option>
            <option value={3}>3 Days Before</option>
            <option value={7}>7 Days Before</option>
            <option value={14}>14 Days Before</option>
            <option value={30}>30 Days Before</option>
          </select>
        </div>
      </header>

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
          value={`${storage_availability.utilization_percentage.toFixed(2)}%`}
          icon="📦"
          color="blue"
          gradient="from-blue-500 to-blue-600"
        />
        <StatCard
          label="Available Capacity"
          value={`${storage_availability.available_capacity_tonnes.toFixed(2)} tonnes`}
          icon="📊"
          color="green"
          gradient="from-green-500 to-green-600"
        />
        <StatCard
          label="Loading Progress"
          value={`${safeLoadingProgress.loading_percentage.toFixed(2)}%`}
          icon="⚡"
          color="yellow"
          gradient="from-yellow-500 to-yellow-600"
        />
        <StatCard
          label="Predicted Demand"
          value={`${safePrediction.predicted_cargo_volume.toFixed(2)} tonnes`}
          icon="🔮"
          color="purple"
          gradient="from-purple-500 to-purple-600"
          trend="up"
          trendValue={`${(safePrediction.confidence * 100).toFixed(0)}% confidence`}
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
                      backgroundColor: 'var(--color-bg-primary)',
                      border: '1px solid var(--color-border)',
                      borderRadius: '8px',
                      color: 'var(--color-text-primary)',
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
              <span className={`status-badge status-${getStatusColor(safeLoadingProgress.status)}`}>
                {safeLoadingProgress.status.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <ProgressBar
              value={safeLoadingProgress.loading_percentage}
              label="Loading Progress"
              color={getStatusColor(safeLoadingProgress.status) as any}
              size="large"
            />
            <div className="loading-details">
              <div className="detail-row">
                <span>Loaded:</span>
                <span className="value">
                  {safeLoadingProgress.loaded_cargo_tonnes.toFixed(2)} / {safeLoadingProgress.total_cargo_tonnes.toFixed(2)} tonnes
                </span>
              </div>
              <div className="detail-row">
                <span>Remaining:</span>
                <span className="value">
                  {(safeLoadingProgress.total_cargo_tonnes - safeLoadingProgress.loaded_cargo_tonnes).toFixed(2)} tonnes
                </span>
              </div>
              {loading_progress.estimated_completion_time && (
                <div className="detail-row">
                  <span>Est. Completion:</span>
                  <span className="value">{formatDate(safeLoadingProgress.estimated_completion_time)}</span>
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
                <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.8} />
                <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis dataKey="time" stroke="var(--color-text-secondary)" />
            <YAxis stroke="var(--color-text-secondary)" domain={[0, 100]} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--color-bg-primary)',
                border: '1px solid var(--color-border)',
                borderRadius: '8px',
                color: 'var(--color-text-primary)',
              }}
              formatter={(value: number) => [`${value.toFixed(1)}%`, 'Utilization']}
            />
            <Area
              type="monotone"
              dataKey="utilization"
              stroke="var(--color-primary)"
              fillOpacity={1}
              fill="url(#colorUtilization)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Card>

      {/* ML Prediction Section */}
      {predictionData && (
        <div className="analytics-grid">
          <Card title={`Capacity Prediction (${daysBeforeFlight} Days Before Flight)`} icon="🤖" className="prediction-card">
            <div className="prediction-info">
              <div className="prediction-grid">
                <div className="prediction-metric">
                  <span className="metric-label">Available Weight</span>
                  <span className="metric-value-large">
                    {predictionData.available_weight_kg ? (predictionData.available_weight_kg / 1000).toFixed(2) : 'N/A'} tonnes
                  </span>
                  {predictionData.confidence_interval_95_lower_weight && (
                    <span className="confidence-range">
                      {((predictionData.confidence_interval_95_lower_weight) / 1000).toFixed(2)} - {((predictionData.confidence_interval_95_upper_weight) / 1000).toFixed(2)} tonnes
                    </span>
                  )}
                </div>
                <div className="prediction-metric">
                  <span className="metric-label">Available Volume</span>
                  <span className="metric-value-large">
                    {predictionData.available_volume_m3 ? predictionData.available_volume_m3.toFixed(2) : 'N/A'} m³
                  </span>
                  {predictionData.confidence_interval_95_lower_volume && (
                    <span className="confidence-range">
                      {predictionData.confidence_interval_95_lower_volume.toFixed(2)} - {predictionData.confidence_interval_95_upper_volume.toFixed(2)} m³
                    </span>
                  )}
                </div>
                <div className="prediction-metric">
                  <span className="metric-label">Constraining Factor</span>
                  <span className={`metric-value status status-${predictionData.constraining_factor === 'weight' ? 'warning' : 'primary'}`}>
                    {predictionData.constraining_factor?.toUpperCase() || 'N/A'}
                  </span>
                </div>
                <div className="prediction-metric">
                  <span className="metric-label">Overbooking Risk</span>
                  <span className={`metric-value status status-${
                    predictionData.overbooking_risk === 'high' ? 'danger' :
                    predictionData.overbooking_risk === 'medium' ? 'warning' : 'success'
                  }`}>
                    {predictionData.overbooking_risk?.toUpperCase() || 'LOW'}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          <Card title="Baggage Prediction" icon="🧳" className="baggage-card">
            <div className="baggage-info">
              {/* Show baggage prediction if available, otherwise use direct fields */}
              {(predictionData.baggage_prediction || predictionData.predicted_baggage_weight_kg) ? (
                <>
                  <div className="baggage-metrics">
                    <div className="metric">
                      <span className="metric-label">Predicted Baggage Weight</span>
                      <span className="metric-value">
                        {predictionData.baggage_prediction?.predicted_baggage_weight_kg || predictionData.predicted_baggage_weight_kg ? 
                          ((predictionData.baggage_prediction?.predicted_baggage_weight_kg || predictionData.predicted_baggage_weight_kg) / 1000).toFixed(2) : 'N/A'} tonnes
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Predicted Baggage Volume</span>
                      <span className="metric-value">
                        {predictionData.baggage_prediction?.predicted_baggage_volume_m3 || predictionData.predicted_baggage_volume_m3 ? 
                          (predictionData.baggage_prediction?.predicted_baggage_volume_m3 || predictionData.predicted_baggage_volume_m3).toFixed(2) : 'N/A'} m³
                      </span>
                    </div>
                    {(predictionData.baggage_prediction?.confidence_interval_95_lower_weight || predictionData.confidence_interval_95_lower_weight) && (
                      <div className="metric">
                        <span className="metric-label">Confidence Interval (95%)</span>
                        <span className="metric-value-small">
                          Weight: {((predictionData.baggage_prediction?.confidence_interval_95_lower_weight || predictionData.confidence_interval_95_lower_weight) / 1000).toFixed(2)} - 
                          {((predictionData.baggage_prediction?.confidence_interval_95_upper_weight || predictionData.confidence_interval_95_upper_weight) / 1000).toFixed(2)} tonnes
                        </span>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div className="baggage-metrics">
                  <div className="metric">
                    <span className="metric-label">No Baggage Prediction Available</span>
                    <span className="metric-value">N/A</span>
                  </div>
                </div>
              )}
              {predictionData.aircraft_max_cargo_weight_kg && (
                <div className="aircraft-capacity">
                  <span className="capacity-label">Aircraft Max Capacity:</span>
                  <span className="capacity-value">
                    {(predictionData.aircraft_max_cargo_weight_kg / 1000).toFixed(2)} tonnes / {predictionData.aircraft_max_cargo_volume_m3?.toFixed(2) || 'N/A'} m³
                  </span>
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* Legacy Prediction Section (if no ML prediction) */}
      {!predictionData && (
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
      )}
    </main>
  )
}

export default CargoAnalytics
