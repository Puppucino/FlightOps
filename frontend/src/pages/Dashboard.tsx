import { useState, useMemo } from "react"
import { FlightCard } from "../components/FlightCard"
import { StatCard } from "../components/StatCard"
import { Layout } from "../components/Layout"
import { mockFlights } from "../data/mockFlights"
import { Flight } from "../types"
import './Dashboard.css'

type RiskFilter = "all" | "high" | "medium" | "low"
type SortOption = "delay" | "flight" | "route"
type GroupBy = "status" | "route" | "none"

export const Dashboard = () => {
  const [searchQuery, setSearchQuery] = useState("")
  const [riskFilter] = useState<RiskFilter>("all")
  const [sortBy] = useState<SortOption>("delay")
  const [groupBy] = useState<GroupBy>("status")

  const flights = mockFlights

  const stats = {
    total: flights.length,
    highRisk: flights.filter(f => f.delayPrediction.delay_probability >= 0.6).length,
    mediumRisk: flights.filter(f => f.delayPrediction.delay_probability >= 0.3 && f.delayPrediction.delay_probability < 0.6).length,
    lowRisk: flights.filter(f => f.delayPrediction.delay_probability < 0.3).length,
    avgDelay: Math.round(flights.reduce((sum, f) => sum + f.delayPrediction.estimated_delay_minutes, 0) / flights.length)
  }

  const filteredAndSortedFlights = useMemo(() => {
    let filtered = flights.filter(flight => {
      // Search filter
      const matchesSearch = 
        flight.flightNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
        flight.origin.toLowerCase().includes(searchQuery.toLowerCase()) ||
        flight.destination.toLowerCase().includes(searchQuery.toLowerCase())
      
      // Risk filter
      const delayProb = flight.delayPrediction.delay_probability
      const matchesRisk = 
        riskFilter === "all" ||
        (riskFilter === "high" && delayProb >= 0.6) ||
        (riskFilter === "medium" && delayProb >= 0.3 && delayProb < 0.6) ||
        (riskFilter === "low" && delayProb < 0.3)
      
      return matchesSearch && matchesRisk
    })

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "delay":
          return b.delayPrediction.delay_probability - a.delayPrediction.delay_probability
        case "flight":
          return a.flightNumber.localeCompare(b.flightNumber)
        case "route":
          return a.origin.localeCompare(b.origin)
        default:
          return 0
      }
    })

    return filtered
  }, [searchQuery, riskFilter, sortBy])

  // Group flights by risk status
  const groupedFlights = useMemo(() => {
    if (groupBy !== "status") {
      return { "All Flights": filteredAndSortedFlights }
    }

    const groups: Record<string, Flight[]> = {
      "HIGH RISK": [],
      "MEDIUM RISK": [],
      "LOW RISK": []
    }

    filteredAndSortedFlights.forEach(flight => {
      const delayProb = flight.delayPrediction.delay_probability
      if (delayProb >= 0.6) {
        groups["HIGH RISK"].push(flight)
      } else if (delayProb >= 0.3) {
        groups["MEDIUM RISK"].push(flight)
      } else {
        groups["LOW RISK"].push(flight)
      }
    })

    // Remove empty groups
    Object.keys(groups).forEach(key => {
      if (groups[key].length === 0) {
        delete groups[key]
      }
    })

    return groups
  }, [filteredAndSortedFlights, groupBy])

  const getGroupColor = (groupName: string) => {
    if (groupName === "HIGH RISK") return "red"
    if (groupName === "MEDIUM RISK") return "orange"
    if (groupName === "LOW RISK") return "green"
    return "gray"
  }

  return (
    <Layout searchQuery={searchQuery} onSearchChange={setSearchQuery}>
      <main className="dashboard-container" role="main">
        {/* Breadcrumbs */}
        <header className="dashboard-header">
          <nav className="dashboard-breadcrumb" aria-label="Breadcrumb navigation">
            <span>Dashboard</span>
            <span className="dashboard-breadcrumb-separator" aria-hidden="true">/</span>
            <span className="dashboard-breadcrumb-item">Flight Monitoring</span>
          </nav>
        </header>

        {/* Stats Cards */}
        <section className="dashboard-stats-grid" aria-label="Flight statistics">
          <StatCard 
            label="Total Flights" 
            value={stats.total}
            icon="✈️"
            gradient="from-blue-500 to-cyan-500"
          />
          <StatCard 
            label="High Risk" 
            value={stats.highRisk}
            color="red"
            icon="⚠️"
            gradient="from-red-500 to-rose-500"
          />
          <StatCard 
            label="Medium Risk" 
            value={stats.mediumRisk}
            color="orange"
            icon="⚡"
            gradient="from-orange-500 to-amber-500"
          />
          <StatCard 
            label="Low Risk" 
            value={stats.lowRisk}
            color="green"
            icon="✅"
            gradient="from-green-500 to-emerald-500"
          />
          <StatCard 
            label="Avg Delay" 
            value={`${stats.avgDelay}m`}
            icon="⏱️"
            gradient="from-purple-500 to-indigo-500"
          />
        </section>

        {/* Grouped Flight Lists */}
        <section className="dashboard-groups" aria-label="Flight groups">
          {Object.entries(groupedFlights).map(([groupName, groupFlights]) => (
            <article key={groupName} className="dashboard-group">
              {/* Group Header */}
              <header className={`dashboard-group-header ${getGroupColor(groupName)}-risk`}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <button aria-label={`Toggle ${groupName} group`} type="button">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  <h3>{groupName}</h3>
                  <span aria-label={`${groupFlights.length} flights in ${groupName}`}>{groupFlights.length}</span>
                </div>
              </header>

              {/* Flight Cards Grid */}
              <div className="dashboard-group-content">
                <div className="dashboard-flights-grid">
                  {groupFlights.map((flight) => (
                    <div key={flight.id}>
                      <FlightCard flight={flight} />
                    </div>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </section>

        {/* Empty State */}
        {filteredAndSortedFlights.length === 0 && (
          <div className="dashboard-empty-state" role="status" aria-live="polite">
            <div className="dashboard-empty-icon" aria-hidden="true">
              <svg className="w-8 h-8" style={{ color: 'var(--color-text-tertiary)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="dashboard-empty-title">No flights found</h3>
            <p className="dashboard-empty-text">
              Try adjusting your search or filter criteria
            </p>
          </div>
        )}
      </main>
    </Layout>
  )
}
