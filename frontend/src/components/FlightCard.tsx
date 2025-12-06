import { Flight } from "../types"

interface FlightCardProps {
  flight: Flight
}

export const FlightCard = ({ flight }: FlightCardProps) => {
  const delayProb = flight.delayPrediction.delay_probability
  const delayMinutes = flight.delayPrediction.estimated_delay_minutes
  
  const getRiskColor = () => {
    if (delayProb < 0.3) return "text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400"
    if (delayProb < 0.6) return "text-orange-600 bg-orange-50 dark:bg-orange-900/20 dark:text-orange-400"
    return "text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400"
  }

  const getPriorityIcon = () => {
    if (delayProb >= 0.6) return "🔴" // Urgent/High
    if (delayProb >= 0.3) return "🟡" // High
    return "🔵" // Normal
  }

  const getPriorityColor = () => {
    if (delayProb >= 0.6) return "text-red-500"
    if (delayProb >= 0.3) return "text-yellow-500"
    return "text-blue-500"
  }

  return (
    <div className="group bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg p-4 hover:shadow-md hover:border-gray-300 dark:hover:border-gray-700 transition-all duration-200">
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className="flex-shrink-0 mt-0.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-sm">
            ✈️
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 min-w-0">
          {/* Flight Number and Route */}
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-1 truncate">
                {flight.flightNumber}
              </h3>
              <p className="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-1.5">
                <span>{flight.origin}</span>
                <span className="text-gray-400">→</span>
                <span>{flight.destination}</span>
              </p>
            </div>
            {/* Priority Flag */}
            <div className={`flex-shrink-0 ${getPriorityColor()}`} title={`${(delayProb * 100).toFixed(0)}% delay risk`}>
              {getPriorityIcon()}
            </div>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap items-center gap-1.5 mb-3">
            <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 text-xs rounded-md">
              {flight.weather.conditions.toLowerCase()}
            </span>
            <span className={`px-2 py-0.5 text-xs rounded-md font-medium ${
              delayProb >= 0.6 
                ? "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400"
                : delayProb >= 0.3
                ? "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400"
                : "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400"
            }`}>
              {(delayProb * 100).toFixed(0)}% risk
            </span>
            {flight.inboundAircraft?.status === 'delayed' && (
              <span className="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs rounded-md font-medium">
                inbound delayed
              </span>
            )}
          </div>

          {/* Bottom Row: Info */}
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center gap-4">
              {/* Departure Time */}
              <div className="flex items-center gap-1.5">
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{flight.scheduledDeparture}</span>
              </div>
              
              {/* Estimated Delay */}
              {delayMinutes > 0 && (
                <div className="flex items-center gap-1.5">
                  <span className="text-red-500 font-medium">+{delayMinutes}m</span>
                </div>
              )}
            </div>

            {/* Confidence Badge */}
            <div className="flex items-center gap-1.5">
              <span className="text-gray-400">AI</span>
              <span className="px-1.5 py-0.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded text-xs font-medium">
                {(flight.delayPrediction.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

