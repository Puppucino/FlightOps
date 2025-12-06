/**
 * Mock data utility for development and testing
 * This can be used when the backend API is not available
 */
import { CargoAnalyticsData, FlightDetails } from '../types'
import { CargoCalendarResponse } from '../api/cargoService'

export const generateMockCargoAnalytics = (flightId?: string): CargoAnalyticsData => {
  // Parse flight ID to extract date information if it's in the format flight-YYYYMMDD-index
  let flightDate = new Date(Date.now() + 2 * 60 * 60 * 1000)
  let flightNumber = 'AA1234'
  let origin = 'JFK'
  let destination = 'LAX'
  let distance = 3984
  
  if (flightId && flightId.startsWith('flight-')) {
    // Try to extract date from flight ID format: flight-YYYYMMDD-index
    const match = flightId.match(/flight-(\d{4})(\d{2})(\d{2})-(\d+)/)
    if (match) {
      const [, year, month, day] = match
      flightDate = new Date(parseInt(year), parseInt(month) - 1, parseInt(day), 8, 0)
      flightNumber = `AA${1000 + parseInt(match[4])}`
      
      // Use route based on index
      const routes = [
        { origin: 'JFK', dest: 'LAX', distance: 3984 },
        { origin: 'ORD', dest: 'HND', distance: 10350 },
        { origin: 'ATL', dest: 'LHR', distance: 6780 },
        { origin: 'LAX', dest: 'NRT', distance: 8800 },
        { origin: 'DFW', dest: 'CDG', distance: 8100 },
      ]
      const routeIndex = parseInt(match[4]) % routes.length
      const route = routes[routeIndex]
      origin = route.origin
      destination = route.dest
      distance = route.distance
    }
  }
  
  const flight: FlightDetails = {
    id: flightId || 'flight-001',
    flight_number: flightNumber,
    airline_name: 'American Airlines',
    aircraft_registration: 'N123AB',
    aircraft_type: 'Boeing 777-300ER',
    origin_airport: `${origin} Airport`,
    origin_airport_code: origin,
    destination_airport: `${destination} Airport`,
    destination_airport_code: destination,
    scheduled_departure: flightDate.toISOString(),
    scheduled_arrival: new Date(flightDate.getTime() + distance / 800 * 60 * 60 * 1000).toISOString(),
    flight_status: 'scheduled',
    distance_km: distance,
    flight_type: 'mixed',
  }

  const totalCapacity = 102.5
  const currentCargo = 68.3
  const availableCapacity = totalCapacity - currentCargo
  const utilization = (currentCargo / totalCapacity) * 100

  return {
    flight,
    storage_availability: {
      aircraft_id: 'aircraft-001',
      aircraft_registration: 'N123AB',
      total_capacity_tonnes: totalCapacity,
      current_cargo_tonnes: currentCargo,
      available_capacity_tonnes: availableCapacity,
      utilization_percentage: utilization,
      predicted_demand_tonnes: 75.2,
      confidence_score: 0.87,
    },
    loading_progress: {
      flight_id: flight.id,
      flight_number: flight.flight_number,
      total_cargo_tonnes: 75.0,
      loaded_cargo_tonnes: 45.5,
      loading_percentage: (45.5 / 75.0) * 100,
      estimated_completion_time: new Date(Date.now() + 1.5 * 60 * 60 * 1000).toISOString(),
      status: 'in_progress',
    },
    prediction: {
      predicted_cargo_volume: 75.2,
      confidence: 0.87,
    },
  }
}

export const generateMockFlights = (): FlightDetails[] => {
  const today = new Date()
  const flights: FlightDetails[] = []
  
  // Generate flights for the next 90 days (matching calendar view)
  const routes = [
    { origin: 'JFK', originName: 'John F. Kennedy International Airport', dest: 'LAX', destName: 'Los Angeles International Airport', distance: 3984 },
    { origin: 'ORD', originName: 'Chicago O\'Hare International Airport', dest: 'HND', destName: 'Tokyo Haneda Airport', distance: 10350 },
    { origin: 'ATL', originName: 'Hartsfield-Jackson Atlanta International Airport', dest: 'LHR', destName: 'London Heathrow Airport', distance: 6780 },
    { origin: 'LAX', originName: 'Los Angeles International Airport', dest: 'NRT', destName: 'Tokyo Narita Airport', distance: 8800 },
    { origin: 'DFW', originName: 'Dallas/Fort Worth International Airport', dest: 'CDG', destName: 'Charles de Gaulle Airport', distance: 8100 },
    { origin: 'MIA', originName: 'Miami International Airport', dest: 'GRU', destName: 'São Paulo-Guarulhos International Airport', distance: 6800 },
    { origin: 'SEA', originName: 'Seattle-Tacoma International Airport', dest: 'ICN', destName: 'Incheon International Airport', distance: 8500 },
    { origin: 'SFO', originName: 'San Francisco International Airport', dest: 'SYD', destName: 'Sydney Kingsford Smith Airport', distance: 12000 },
  ]
  
  const aircraftTypes = [
    { type: 'Boeing 777-300ER', reg: 'N123AB' },
    { type: 'Boeing 747-8F', reg: 'N456CD' },
    { type: 'Airbus A330-200F', reg: 'N789EF' },
    { type: 'Boeing 737-800', reg: 'N012GH' },
    { type: 'Airbus A350-900', reg: 'N345IJ' },
  ]
  
  let flightCounter = 1000
  
  // Generate flights for next 90 days
  for (let dayOffset = 0; dayOffset < 90; dayOffset++) {
    const flightDate = new Date(today)
    flightDate.setDate(today.getDate() + dayOffset)
    flightDate.setHours(8, 0, 0, 0)
    
    const isWeekend = flightDate.getDay() === 0 || flightDate.getDay() === 6
    const flightsPerDay = isWeekend ? 4 : 3
    
    for (let i = 0; i < flightsPerDay; i++) {
      const route = routes[i % routes.length]
      const aircraft = aircraftTypes[i % aircraftTypes.length]
      const flightNumber = `AA${flightCounter}`
      
      // Calculate arrival time (estimate 800 km/h average)
      const hours = route.distance / 800
      const arrivalDate = new Date(flightDate)
      arrivalDate.setHours(flightDate.getHours() + Math.floor(hours))
      arrivalDate.setMinutes(flightDate.getMinutes() + Math.floor((hours % 1) * 60))
      
      // Generate consistent flight ID (same format as calendar)
      // Use format: flight-YYYYMMDD-index to match calendar view
      const year = flightDate.getFullYear()
      const month = String(flightDate.getMonth() + 1).padStart(2, '0')
      const day = String(flightDate.getDate()).padStart(2, '0')
      const flightId = `flight-${year}${month}${day}-${i}`
      
      flights.push({
        id: flightId,
        flight_number: flightNumber,
      airline_name: 'American Airlines',
        aircraft_registration: aircraft.reg,
        aircraft_type: aircraft.type,
        origin_airport: route.originName,
        origin_airport_code: route.origin,
        destination_airport: route.destName,
        destination_airport_code: route.dest,
        scheduled_departure: flightDate.toISOString(),
        scheduled_arrival: arrivalDate.toISOString(),
        flight_status: dayOffset === 0 && i === 0 ? 'in_progress' : 'scheduled',
        distance_km: route.distance,
        flight_type: 'mixed',
      })
      
      flightCounter++
    }
  }
  
  return flights
}

/**
 * Generate comprehensive mock calendar data with flights and peak seasons
 */
export const generateMockCargoCalendar = (
  year?: number,
  month?: number
): CargoCalendarResponse => {
  const today = new Date()
  const targetYear = year || today.getFullYear()
  const targetMonth = month || today.getMonth() + 1
  
  // Generate peak seasons for the month
  const peakSeasons: CargoCalendarResponse['peak_seasons'] = []
  
  // Major holidays
  if (targetMonth === 1) {
    peakSeasons.push({
      date: `${targetYear}-01-01`,
      day: 1,
      multiplier: 1.5,
      type: 'holiday',
      is_holiday: true,
      is_school_holiday: false,
    })
  }
  if (targetMonth === 12) {
    peakSeasons.push({
      date: `${targetYear}-12-25`,
      day: 25,
      multiplier: 1.5,
      type: 'holiday',
      is_holiday: true,
      is_school_holiday: false,
    })
    peakSeasons.push({
      date: `${targetYear}-12-31`,
      day: 31,
      multiplier: 1.5,
      type: 'holiday',
      is_holiday: true,
      is_school_holiday: false,
    })
    // Winter break (Dec 15 - Jan 5)
    for (let day = 15; day <= 31; day++) {
      peakSeasons.push({
        date: `${targetYear}-12-${String(day).padStart(2, '0')}`,
        day,
        multiplier: 1.3,
        type: 'school_holiday',
        is_holiday: day === 25 || day === 31,
        is_school_holiday: true,
      })
    }
  }
  
  // Summer break (June-August)
  if (targetMonth >= 6 && targetMonth <= 8) {
    const daysInMonth = new Date(targetYear, targetMonth, 0).getDate()
    for (let day = 1; day <= daysInMonth; day++) {
      peakSeasons.push({
        date: `${targetYear}-${String(targetMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`,
        day,
        multiplier: 1.3,
        type: 'school_holiday',
        is_holiday: false,
        is_school_holiday: true,
      })
    }
  }
  
  // Spring break (March 15-31)
  if (targetMonth === 3) {
    for (let day = 15; day <= 31; day++) {
      peakSeasons.push({
        date: `${targetYear}-03-${String(day).padStart(2, '0')}`,
        day,
        multiplier: 1.3,
        type: 'school_holiday',
        is_holiday: false,
        is_school_holiday: true,
      })
    }
  }
  
  // Generate flights for the month
  const flights: CargoCalendarResponse['flights'] = []
  const daysInMonth = new Date(targetYear, targetMonth, 0).getDate()
  
  // Flight routes
  const routes = [
    { origin: 'JFK', destination: 'LAX', basePax: 180 },
    { origin: 'ORD', destination: 'HND', basePax: 220 },
    { origin: 'ATL', destination: 'LHR', basePax: 250 },
    { origin: 'LAX', destination: 'NRT', basePax: 200 },
    { origin: 'DFW', destination: 'CDG', basePax: 240 },
    { origin: 'MIA', destination: 'GRU', basePax: 190 },
    { origin: 'SEA', destination: 'ICN', basePax: 210 },
    { origin: 'SFO', destination: 'SYD', basePax: 230 },
  ]
  
  const aircraftTypes = [
    'Boeing 777-300ER',
    'Boeing 747-8F',
    'Airbus A330-200F',
    'Boeing 737-800',
    'Airbus A350-900',
  ]
  
  // Generate 3-5 flights per day, more on weekends and peak seasons
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${targetYear}-${String(targetMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    const date = new Date(targetYear, targetMonth - 1, day)
    const isWeekend = date.getDay() === 0 || date.getDay() === 6
    const isPeakSeason = peakSeasons.some(p => p.date === dateStr)
    
    const flightsPerDay = isPeakSeason ? 5 : isWeekend ? 4 : 3
    
    for (let i = 0; i < flightsPerDay; i++) {
      const route = routes[Math.floor(Math.random() * routes.length)]
      const aircraftType = aircraftTypes[Math.floor(Math.random() * aircraftTypes.length)]
      const flightNumber = `${String.fromCharCode(65 + Math.floor(Math.random() * 26))}${String.fromCharCode(65 + Math.floor(Math.random() * 26))}${Math.floor(1000 + Math.random() * 9000)}`
      
      // Calculate traffic multiplier
      const peakSeason = peakSeasons.find(p => p.date === dateStr)
      const trafficMultiplier = peakSeason?.multiplier || (isWeekend ? 1.15 : 1.0)
      const estimatedPax = Math.floor(route.basePax * trafficMultiplier)
      
      // Calculate utilization based on traffic
      const baseUtilization = 45 + Math.random() * 30 // 45-75% base
      const peakAdjustment = isPeakSeason ? 15 : isWeekend ? 5 : 0
      const utilization = Math.min(95, baseUtilization + peakAdjustment)
      
      // Determine overbooking risk
      let overbookingRisk: 'low' | 'medium' | 'high' = 'low'
      if (utilization >= 85) {
        overbookingRisk = 'high'
      } else if (utilization >= 70) {
        overbookingRisk = 'medium'
      }
      
      // Calculate available capacity (inverse of utilization)
      const maxCapacity = 20000 // kg
      const availableWeight = maxCapacity * (1 - utilization / 100)
      const availableVolume = availableWeight * 0.15 // m³ estimate
      
      // Generate consistent flight ID matching list view format
      const flightId = `flight-${targetYear}${String(targetMonth).padStart(2, '0')}${String(day).padStart(2, '0')}-${i}`
      
      flights.push({
        flight_id: flightId,
        flight_number: flightNumber,
        date: dateStr,
        scheduled_departure: new Date(targetYear, targetMonth - 1, day, 8 + i * 3, Math.floor(Math.random() * 60)).toISOString(),
        origin: route.origin,
        destination: route.destination,
        route: `${route.origin}-${route.destination}`,
        aircraft_type: aircraftType,
        passenger_count: route.basePax,
        traffic_estimation: {
          base_passenger_count: route.basePax,
          estimated_passenger_count: estimatedPax,
          traffic_multiplier: trafficMultiplier,
          is_holiday: peakSeason?.is_holiday || false,
          is_school_holiday: peakSeason?.is_school_holiday || false,
          is_weekend: isWeekend,
          peak_season_type: peakSeason?.type || null,
          month: targetMonth,
          day_of_week: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][date.getDay()],
        },
        cargo_prediction: {
          available_weight_kg: availableWeight,
          available_volume_m3: availableVolume,
          utilization_percentage: utilization,
          overbooking_risk: overbookingRisk,
        },
        utilization_percentage: utilization,
        available_weight_kg: availableWeight,
        available_volume_m3: availableVolume,
        overbooking_risk: overbookingRisk,
      })
    }
  }
  
  return {
    year: targetYear,
    month: targetMonth,
    peak_seasons: peakSeasons,
    flights: flights,
  }
}
