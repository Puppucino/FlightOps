import { useState, useMemo } from "react"
import { FlightCard } from "../components/FlightCard"
import { StatCard } from "../components/StatCard"
import { Sidebar } from "../components/Sidebar"
import { Header } from "../components/Header"
import { mockFlights } from "../data/mockFlights"
import { Flight } from "../types"

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
    if (groupName === "HIGH RISK") return "bg-red-500"
    if (groupName === "MEDIUM RISK") return "bg-orange-500"
    if (groupName === "LOW RISK") return "bg-green-500"
    return "bg-gray-500"
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950 overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col ml-64">
        {/* Header */}
        <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto mt-16">
          <div className="p-6">
            {/* Breadcrumbs and View Tabs */}
            <div className="mb-6">
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-4">
                <span>Dashboard</span>
                <span>/</span>
                <span className="text-gray-700 dark:text-gray-300 font-medium">Flight Monitoring</span>
              </div>
              
              {/* View Tabs */}
              <div className="flex items-center gap-2 mb-4">
                <button className="px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  List
                </button>
                <button className="px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  Board
                </button>
                <button className="px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  Timeline
                </button>
                <button className="px-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                  Analytics
                </button>
              </div>

              {/* Action Bar */}
              <div className="flex items-center gap-3 flex-wrap">
                <button className="px-3 py-1.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors flex items-center gap-2">
                  <span>Group: Status</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                <button className="px-3 py-1.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                  <span>Filter</span>
                </button>
                <button className="px-4 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
                  <span>+</span>
                  <span>Add Flight</span>
                </button>
              </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-4 mb-6">
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
            <div className="space-y-6">
              {Object.entries(groupedFlights).map(([groupName, groupFlights]) => (
                <div key={groupName} className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 overflow-hidden">
                  {/* Group Header */}
                  <div className={`${getGroupColor(groupName)} px-4 py-3 flex items-center justify-between`}>
                    <div className="flex items-center gap-3">
                      <button className="text-white hover:bg-white/20 rounded p-1 transition-colors">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      <h3 className="text-white font-bold text-sm uppercase tracking-wide">
                        {groupName}
                      </h3>
                      <span className="text-white/80 text-xs font-medium bg-white/20 px-2 py-0.5 rounded">
                        {groupFlights.length}
                      </span>
                    </div>
                  </div>

                  {/* Flight Cards Grid */}
                  <div className="p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {groupFlights.map((flight, index) => (
                        <div
                          key={flight.id}
                          className="animate-in fade-in slide-in-from-bottom-4"
                          style={{ animationDelay: `${index * 50}ms` }}
                        >
                          <FlightCard flight={flight} />
                        </div>
                      ))}
                    </div>
                    
                    {/* Add Flight Button */}
                    <button className="mt-4 w-full py-3 border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-lg text-gray-500 dark:text-gray-400 hover:border-purple-500 hover:text-purple-500 transition-colors flex items-center justify-center gap-2">
                      <span>+</span>
                      <span>Add Flight</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Empty State */}
            {filteredAndSortedFlights.length === 0 && (
              <div className="text-center py-16 bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-800 mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No flights found</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Try adjusting your search or filter criteria
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
