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
  color = "text-gray-900",
  icon
}: StatCardProps) => {
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
