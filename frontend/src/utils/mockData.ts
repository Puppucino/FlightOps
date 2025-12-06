/**
 * Mock data utility for development and testing
 * This can be used when the backend API is not available
 */
import { CargoAnalyticsData, FlightDetails } from '../types'

export const generateMockCargoAnalytics = (flightId?: string): CargoAnalyticsData => {
  const flight: FlightDetails = {
    id: flightId || 'flight-001',
    flight_number: 'AA1234',
    airline_name: 'American Airlines',
    aircraft_registration: 'N123AB',
    aircraft_type: 'Boeing 777-300ER',
    origin_airport: 'John F. Kennedy International Airport',
    origin_airport_code: 'JFK',
    destination_airport: 'Los Angeles International Airport',
    destination_airport_code: 'LAX',
    scheduled_departure: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
    scheduled_arrival: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(),
    flight_status: 'scheduled',
    distance_km: 3984,
    flight_type: 'cargo',
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
  return [
    {
      id: 'flight-001',
      flight_number: 'AA1234',
      airline_name: 'American Airlines',
      aircraft_registration: 'N123AB',
      aircraft_type: 'Boeing 777-300ER',
      origin_airport: 'John F. Kennedy International Airport',
      origin_airport_code: 'JFK',
      destination_airport: 'Los Angeles International Airport',
      destination_airport_code: 'LAX',
      scheduled_departure: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
      scheduled_arrival: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(),
      flight_status: 'scheduled',
      distance_km: 3984,
      flight_type: 'cargo',
    },
    {
      id: 'flight-002',
      flight_number: 'UA5678',
      airline_name: 'United Airlines',
      aircraft_registration: 'N456CD',
      aircraft_type: 'Boeing 747-8F',
      origin_airport: 'Chicago O\'Hare International Airport',
      origin_airport_code: 'ORD',
      destination_airport: 'Tokyo Haneda Airport',
      destination_airport_code: 'HND',
      scheduled_departure: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(),
      scheduled_arrival: new Date(Date.now() + 14 * 60 * 60 * 1000).toISOString(),
      flight_status: 'scheduled',
      distance_km: 10350,
      flight_type: 'cargo',
    },
    {
      id: 'flight-003',
      flight_number: 'DL9012',
      airline_name: 'Delta Air Lines',
      aircraft_registration: 'N789EF',
      aircraft_type: 'Airbus A330-200F',
      origin_airport: 'Hartsfield-Jackson Atlanta International Airport',
      origin_airport_code: 'ATL',
      destination_airport: 'London Heathrow Airport',
      destination_airport_code: 'LHR',
      scheduled_departure: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(),
      scheduled_arrival: new Date(Date.now() + 14 * 60 * 60 * 1000).toISOString(),
      flight_status: 'in_progress',
      distance_km: 6780,
      flight_type: 'mixed',
    },
  ]
}
