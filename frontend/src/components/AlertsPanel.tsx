import React, { useState, useEffect } from 'react'
import './AlertsPanel.css'

interface Alert {
  type: string
  severity: 'high' | 'medium' | 'low'
  flight_id: string
  flight_number: string
  title: string
  message: string
  timestamp: string
  action_required: boolean
}

interface AlertsPanelProps {
  onAlertClick?: (flightId: string) => void
}

const AlertsPanel: React.FC<AlertsPanelProps> = ({ onAlertClick }) => {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(true)

  useEffect(() => {
    fetchAlerts()
    // Refresh alerts every 5 minutes
    const interval = setInterval(fetchAlerts, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/v1/ai/alerts?days_ahead=7')
      if (response.ok) {
        const data = await response.json()
        setAlerts(data.alerts || [])
      }
    } catch (error) {
      console.error('Error fetching alerts:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return '🔴'
      case 'medium':
        return '🟡'
      case 'low':
        return '🟢'
      default:
        return '⚪'
    }
  }

  const getSeverityClass = (severity: string) => {
    return `alert-severity-${severity}`
  }

  const highPriorityAlerts = alerts.filter(a => a.severity === 'high')
  const mediumPriorityAlerts = alerts.filter(a => a.severity === 'medium')
  const lowPriorityAlerts = alerts.filter(a => a.severity === 'low')

  if (!expanded) {
    return (
      <div className="alerts-panel-collapsed" onClick={() => setExpanded(true)}>
        <div className="alerts-badge">
          {alerts.length > 0 && (
            <span className="alerts-count">{alerts.length}</span>
          )}
          <span className="alerts-icon">🔔</span>
        </div>
      </div>
    )
  }

  return (
    <div className="alerts-panel">
      <div className="alerts-header">
        <div className="alerts-title">
          <span className="alerts-icon">🔔</span>
          <h3>Alerts</h3>
          {alerts.length > 0 && (
            <span className="alerts-count-badge">{alerts.length}</span>
          )}
        </div>
        <button className="alerts-collapse-btn" onClick={() => setExpanded(false)}>−</button>
      </div>

      <div className="alerts-content">
        {loading ? (
          <div className="alerts-loading">Loading alerts...</div>
        ) : alerts.length === 0 ? (
          <div className="alerts-empty">
            <p>✅ No alerts at this time</p>
            <p className="alerts-empty-sub">All flights are operating normally</p>
          </div>
        ) : (
          <>
            {highPriorityAlerts.length > 0 && (
              <div className="alerts-section">
                <h4 className="alerts-section-title high">High Priority ({highPriorityAlerts.length})</h4>
                {highPriorityAlerts.map((alert, index) => (
                  <div
                    key={index}
                    className={`alert-item ${getSeverityClass(alert.severity)}`}
                    onClick={() => onAlertClick?.(alert.flight_id)}
                  >
                    <div className="alert-header">
                      <span className="alert-severity-icon">{getSeverityIcon(alert.severity)}</span>
                      <span className="alert-title">{alert.title}</span>
                    </div>
                    <div className="alert-message">{alert.message}</div>
                    <div className="alert-footer">
                      <span className="alert-flight">{alert.flight_number}</span>
                      <span className="alert-time">
                        {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {mediumPriorityAlerts.length > 0 && (
              <div className="alerts-section">
                <h4 className="alerts-section-title medium">Medium Priority ({mediumPriorityAlerts.length})</h4>
                {mediumPriorityAlerts.map((alert, index) => (
                  <div
                    key={index}
                    className={`alert-item ${getSeverityClass(alert.severity)}`}
                    onClick={() => onAlertClick?.(alert.flight_id)}
                  >
                    <div className="alert-header">
                      <span className="alert-severity-icon">{getSeverityIcon(alert.severity)}</span>
                      <span className="alert-title">{alert.title}</span>
                    </div>
                    <div className="alert-message">{alert.message}</div>
                    <div className="alert-footer">
                      <span className="alert-flight">{alert.flight_number}</span>
                      <span className="alert-time">
                        {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {lowPriorityAlerts.length > 0 && (
              <div className="alerts-section">
                <h4 className="alerts-section-title low">Low Priority ({lowPriorityAlerts.length})</h4>
                {lowPriorityAlerts.map((alert, index) => (
                  <div
                    key={index}
                    className={`alert-item ${getSeverityClass(alert.severity)}`}
                    onClick={() => onAlertClick?.(alert.flight_id)}
                  >
                    <div className="alert-header">
                      <span className="alert-severity-icon">{getSeverityIcon(alert.severity)}</span>
                      <span className="alert-title">{alert.title}</span>
                    </div>
                    <div className="alert-message">{alert.message}</div>
                    <div className="alert-footer">
                      <span className="alert-flight">{alert.flight_number}</span>
                      <span className="alert-time">
                        {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default AlertsPanel
