import './StatCard.css'

interface StatCardProps {
  label: string
  value: string | number
  color?: string
  icon?: string
  gradient?: string
  trend?: string
  trendValue?: string
}

export const StatCard = ({ 
  label, 
  value, 
  color,
  icon,
  gradient,
  trend,
  trendValue
}: StatCardProps) => {
  // Determine border color class from gradient if provided
  const getBorderColorClass = () => {
    if (!gradient) return "stat-card-border-default"
    if (gradient.includes("blue")) return "stat-card-border-blue"
    if (gradient.includes("green")) return "stat-card-border-green"
    if (gradient.includes("yellow")) return "stat-card-border-yellow"
    if (gradient.includes("purple")) return "stat-card-border-purple"
    if (gradient.includes("red") || gradient.includes("rose")) return "stat-card-border-red"
    if (gradient.includes("orange") || gradient.includes("amber")) return "stat-card-border-orange"
    return "stat-card-border-default"
  }

  // Determine accent color class from gradient
  const getAccentColorClass = () => {
    if (!gradient) return "stat-card-accent-default"
    if (gradient.includes("blue")) return "stat-card-accent-blue"
    if (gradient.includes("green")) return "stat-card-accent-green"
    if (gradient.includes("yellow")) return "stat-card-accent-yellow"
    if (gradient.includes("purple")) return "stat-card-accent-purple"
    if (gradient.includes("red") || gradient.includes("rose")) return "stat-card-accent-red"
    if (gradient.includes("orange") || gradient.includes("amber")) return "stat-card-accent-orange"
    return "stat-card-accent-default"
  }

  // Determine value color class
  const getValueColorClass = () => {
    if (color) {
      if (color.includes("red")) return "stat-card-value-red"
      if (color.includes("orange")) return "stat-card-value-orange"
      if (color.includes("green")) return "stat-card-value-green"
      if (color.includes("blue")) return "stat-card-value-blue"
      if (color.includes("purple")) return "stat-card-value-purple"
      if (color.includes("yellow")) return "stat-card-value-yellow"
    }
    return "stat-card-value-default"
  }

  // Determine trend color class
  const getTrendColorClass = () => {
    if (trend === "up") return "stat-card-trend-up"
    if (trend === "down") return "stat-card-trend-down"
    return "stat-card-trend-neutral"
  }

  return (
    <article 
      className={`stat-card ${getBorderColorClass()}`} 
      role="article" 
      aria-label={`${label}: ${value}`}
    >
      {/* Gradient Background Effect */}
      {gradient && (
        <div className={`stat-card-gradient ${gradient.replace(/\s+/g, '-')}`} />
      )}
      
      <div className="stat-card-content">
        <div className="stat-card-header">
          {icon && <span className="stat-card-icon" aria-hidden="true">{icon}</span>}
          <p className="stat-card-label">
            {label}
          </p>
        </div>
        <p className={`stat-card-value ${getValueColorClass()}`} aria-label={`${label} value is ${value}`}>
          {value}
        </p>
        {trendValue && (
          <p className={`stat-card-trend ${getTrendColorClass()}`}>
            {trendValue}
          </p>
        )}
      </div>
      
      {/* Colored accent bar */}
      <div className={`stat-card-accent ${getAccentColorClass()}`} />
    </article>
  )
}
