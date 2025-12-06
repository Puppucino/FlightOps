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
  const [riskFilter, setRiskFilter] = useState<RiskFilter>("all")
  const [sortBy, setSortBy] = useState<SortOption>("delay")
  const [groupBy, setGroupBy] = useState<GroupBy>("status")
  const [showFilters, setShowFilters] = useState(false)

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
      <div className="dashboard-container">
        {/* Breadcrumbs and View Tabs */}
        <div className="dashboard-header">
          <div className="dashboard-breadcrumb">
            <span>Dashboard</span>
            <span className="dashboard-breadcrumb-separator">/</span>
            <span className="dashboard-breadcrumb-item">Flight Monitoring</span>
          </div>
          
          {/* View Tabs */}
          <div className="dashboard-view-tabs">
            <button className="dashboard-view-tab active">List</button>
            <button className="dashboard-view-tab">Board</button>
            <button className="dashboard-view-tab">Timeline</button>
            <button className="dashboard-view-tab">Analytics</button>
          </div>

          {/* Action Bar */}
          <div className="dashboard-action-bar">
            <button className="dashboard-action-btn">
              <span>Group: Status</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <button className="dashboard-action-btn">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              <span>Filter</span>
            </button>
            <button className="dashboard-action-btn primary">
              <span>+</span>
              <span>Add Flight</span>
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="dashboard-stats-grid">
              <StatCard 
                label="Total Flights" 
                value={stats.total}
                icon="✈️"
                gradient="from-blue-500 to-cyan-500"
              />
              <StatCard 
                label="High Risk" 
                value={stats.highRisk}
                color="text-red-600 dark:text-red-400"
                icon="⚠️"
                gradient="from-red-500 to-rose-500"
              />
              <StatCard 
                label="Medium Risk" 
                value={stats.mediumRisk}
                color="text-orange-600 dark:text-orange-400"
                icon="⚡"
                gradient="from-orange-500 to-amber-500"
              />
              <StatCard 
                label="Low Risk" 
                value={stats.lowRisk}
                color="text-green-600 dark:text-green-400"
                icon="✅"
                gradient="from-green-500 to-emerald-500"
              />
              <StatCard 
                label="Avg Delay" 
                value={`${stats.avgDelay}m`}
                icon="⏱️"
                gradient="from-purple-500 to-indigo-500"
              />
            </div>

        {/* Grouped Flight Lists */}
        <div className="dashboard-groups">
          {Object.entries(groupedFlights).map(([groupName, groupFlights]) => (
            <div key={groupName} className="dashboard-group">
              {/* Group Header */}
              <div className={`dashboard-group-header ${getGroupColor(groupName).replace('bg-', '').replace('-500', '').toLowerCase()}-risk`}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <button style={{ background: 'rgba(255, 255, 255, 0.2)', padding: '4px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 700, textTransform: 'uppercase' }}>
                    {groupName}
                  </h3>
                  <span style={{ background: 'rgba(255, 255, 255, 0.2)', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 500 }}>
                    {groupFlights.length}
                  </span>
                </div>
              </div>

              {/* Flight Cards Grid */}
              <div className="dashboard-group-content">
                <div className="dashboard-flights-grid">
                  {groupFlights.map((flight, index) => (
                    <div key={flight.id}>
                      <FlightCard flight={flight} />
                    </div>
                  ))}
                </div>
                
                {/* Add Flight Button */}
                <button className="dashboard-add-flight-btn">
                  <span>+</span>
                  <span>Add Flight</span>
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredAndSortedFlights.length === 0 && (
          <div className="dashboard-empty-state">
            <div className="dashboard-empty-icon">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="dashboard-empty-title">No flights found</h3>
            <p className="dashboard-empty-text">
              Try adjusting your search or filter criteria
            </p>
          </div>
        )}
      </div>
    </Layout>
  )
}
