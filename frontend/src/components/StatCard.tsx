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
  color = "text-gray-900 dark:text-white",
  icon,
  gradient,
  trend,
  trendValue
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
    <div className={`group relative bg-white/70 dark:bg-gray-900/70 backdrop-blur-sm rounded-xl border-l-4 ${getBorderColor()} border border-gray-200/50 dark:border-gray-800/50 p-5 hover:shadow-lg hover:shadow-gray-200/50 dark:hover:shadow-gray-900/50 hover:border-gray-300 dark:hover:border-gray-700 transition-all duration-300 hover:-translate-y-1`}>
      {/* Gradient Background Effect */}
      {gradient && (
        <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-5 dark:opacity-10 rounded-xl transition-opacity duration-300 group-hover:opacity-10 dark:group-hover:opacity-15`} />
      )}
      
      <div className="relative flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {icon && <span className="text-xl">{icon}</span>}
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              {label}
            </p>
          </div>
          <p className={`text-3xl font-bold ${color} leading-none`}>
            {value}
          </p>
          {trendValue && (
            <p className={`text-xs font-medium mt-1 ${
              trend === "up" ? "text-green-600 dark:text-green-400" :
              trend === "down" ? "text-red-600 dark:text-red-400" :
              "text-gray-500 dark:text-gray-400"
            }`}>
              {trendValue}
            </p>
          )}
        </div>
      </div>
      
      {/* Colored accent bar */}
      <div className={`absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent ${getAccentColor()} to-transparent rounded-b-xl transition-colors`} />
    </div>
  )
}
