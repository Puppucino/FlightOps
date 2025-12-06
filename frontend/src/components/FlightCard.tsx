import { Flight } from "../types"
import './FlightCard.css'

interface FlightCardProps {
  flight: Flight
}

export const FlightCard = ({ flight }: FlightCardProps) => {
  const delayProb = flight.delayPrediction.delay_probability
  const delayMinutes = flight.delayPrediction.estimated_delay_minutes
  
  const getRiskLevel = () => {
    if (delayProb >= 0.6) return "high"
    if (delayProb >= 0.3) return "medium"
    return "low"
  }

  const getPriorityIcon = () => {
    if (delayProb >= 0.6) return "🔴"
    if (delayProb >= 0.3) return "🟡"
    return "🔵"
  }

  const riskLevel = getRiskLevel()

  return (
    <div className="flight-card">
      <div className="flight-card-content">
        {/* Icon */}
        <div className="flight-card-icon">
          <div className="flight-icon-badge">✈️</div>
        </div>

        {/* Main Content */}
        <div className="flight-card-main">
          {/* Flight Number and Route */}
          <div className="flight-card-header">
            <div className="flight-card-title-section">
              <h3 className="flight-number">{flight.flightNumber}</h3>
              <p className="flight-route">
                <span>{flight.origin}</span>
                <span className="route-arrow">→</span>
                <span>{flight.destination}</span>
              </p>
            </div>
            {/* Priority Flag */}
            <div className={`flight-priority-badge priority-${riskLevel}`} title={`${(delayProb * 100).toFixed(0)}% delay risk`}>
              {getPriorityIcon()}
            </div>
          </div>

          {/* Tags */}
          <div className="flight-tags">
            <span className="tag tag-weather">
              {flight.weather.conditions.toLowerCase()}
            </span>
            <span className={`tag tag-risk tag-risk-${riskLevel}`}>
              {(delayProb * 100).toFixed(0)}% risk
            </span>
            {flight.inboundAircraft?.status === 'delayed' && (
              <span className="tag tag-delayed">
                inbound delayed
              </span>
            )}
          </div>

          {/* Bottom Row: Info */}
          <div className="flight-card-footer">
            <div className="flight-info-left">
              {/* Departure Time */}
              <div className="flight-info-item">
                <svg className="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{flight.scheduledDeparture}</span>
              </div>
              
              {/* Estimated Delay */}
              {delayMinutes > 0 && (
                <div className="flight-info-item delay-badge">
                  <span>+{delayMinutes}m</span>
                </div>
              )}
            </div>

            {/* Confidence Badge */}
            <div className="flight-confidence">
              <span className="confidence-label">AI</span>
              <span className="confidence-badge">
                {(flight.delayPrediction.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
