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
  color = "text-gray-900",
  icon
}: StatCardProps) => {
  // Determine border color from gradient if provided
  const getBorderColor = () => {
    if (!gradient) return "border-gray-200/50 dark:border-gray-800/50"
    if (gradient.includes("blue")) return "border-blue-200/50 dark:border-blue-800/50"
    if (gradient.includes("green")) return "border-green-200/50 dark:border-green-800/50"
    if (gradient.includes("yellow")) return "border-yellow-200/50 dark:border-yellow-800/50"
    if (gradient.includes("purple")) return "border-purple-200/50 dark:border-purple-800/50"
    return "border-gray-200/50 dark:border-gray-800/50"
  }

  // Determine accent bar color from gradient
  const getAccentColor = () => {
    if (!gradient) return "via-gray-200 dark:via-gray-700"
    if (gradient.includes("blue")) return "via-blue-400 dark:via-blue-600"
    if (gradient.includes("green")) return "via-green-400 dark:via-green-600"
    if (gradient.includes("yellow")) return "via-yellow-400 dark:via-yellow-600"
    if (gradient.includes("purple")) return "via-purple-400 dark:via-purple-600"
    return "via-gray-200 dark:via-gray-700"
  }

  return (
    <div className="stat-card">
      <div className="stat-card-content">
        <div className="stat-card-header">
          {icon && <span className="stat-card-icon">{icon}</span>}
          <p className="stat-card-label">{label}</p>
        </div>
        <p className={`stat-card-value ${color}`}>
          {value}
        </p>
      </div>
    </div>
  )
}
