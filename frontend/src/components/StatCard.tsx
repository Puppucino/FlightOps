interface StatCardProps {
  label: string
  value: string | number
  color?: string
  icon?: string
  gradient?: string
}

export const StatCard = ({ 
  label, 
  value, 
  color = "text-gray-900 dark:text-white",
  icon,
  gradient
}: StatCardProps) => {
  return (
    <div className="group relative bg-white/70 dark:bg-gray-900/70 backdrop-blur-sm rounded-xl border border-gray-200/50 dark:border-gray-800/50 p-5 hover:shadow-lg hover:shadow-gray-200/50 dark:hover:shadow-gray-900/50 hover:border-gray-300 dark:hover:border-gray-700 transition-all duration-300 hover:-translate-y-1">
      {/* Gradient Background Effect */}
      {gradient && (
        <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-5 dark:group-hover:opacity-10 rounded-xl transition-opacity duration-300`} />
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
        </div>
      </div>
      
      {/* Decorative accent */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-gray-200 to-transparent dark:via-gray-700 group-hover:via-gray-300 dark:group-hover:via-gray-600 rounded-b-xl transition-colors" />
    </div>
  )
}
