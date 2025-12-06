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
    <article className="flight-card" role="article" aria-labelledby={`flight-${flight.id}-number`}>
      <div className="flight-card-content">
        {/* Icon */}
        <div className="flight-card-icon">
          <div className="flight-icon-badge" aria-hidden="true">✈️</div>
        </div>

        {/* Main Content */}
        <div className="flight-card-main">
          {/* Flight Number and Route */}
          <header className="flight-card-header">
            <div className="flight-card-title-section">
              <h3 className="flight-number" id={`flight-${flight.id}-number`}>{flight.flightNumber}</h3>
              <p className="flight-route">
                <span>{flight.origin}</span>
                <span className="route-arrow" aria-hidden="true">→</span>
                <span>{flight.destination}</span>
              </p>
            </div>
            {/* Priority Flag */}
            <div 
              className={`flight-priority-badge priority-${riskLevel}`} 
              title={`${(delayProb * 100).toFixed(0)}% delay risk`}
              aria-label={`Delay risk: ${(delayProb * 100).toFixed(0)}%`}
              role="status"
            >
              <span aria-hidden="true">{getPriorityIcon()}</span>
            </div>
          </header>

          {/* Tags */}
          <div className="flight-tags" role="list" aria-label="Flight status tags">
            <span className="tag tag-weather" role="listitem">
              {flight.weather.conditions.toLowerCase()}
            </span>
            <span className={`tag tag-risk tag-risk-${riskLevel}`} role="listitem">
              {(delayProb * 100).toFixed(0)}% risk
            </span>
            {flight.inboundAircraft?.status === 'delayed' && (
              <span className="tag tag-delayed" role="listitem">
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
            <div className="flight-confidence" aria-label={`AI prediction confidence: ${(flight.delayPrediction.confidence * 100).toFixed(0)}%`}>
              <span className="confidence-label" aria-hidden="true">AI</span>
              <span className="confidence-badge" aria-label={`${(flight.delayPrediction.confidence * 100).toFixed(0)}% confidence`}>
                {(flight.delayPrediction.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </article>
  )
}
