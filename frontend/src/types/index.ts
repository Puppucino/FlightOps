/**
 * TypeScript type definitions for the application
 */

export interface FlightDelayPrediction {
  delay_probability: number
  estimated_delay_minutes: number
  confidence: number
}

export interface CargoPrediction {
  predicted_cargo_volume: number
  confidence: number
}

export interface PassengerTrafficPrediction {
  predicted_passengers: number
  confidence: number
}

export interface WeatherData {
  temperature: number
  humidity: number
  wind_speed: number
  visibility: number
  conditions: string
}

export interface FlightRoute {
  origin: string
  destination: string
  distance: number
  duration: number
}

export interface AirportTraffic {
  airport_code: string
  current_traffic: number
  capacity: number
}

export interface AircraftData {
  aircraft_type: string
  capacity: number
  cargo_capacity: number
}

// Cargo Analytics Types
export interface FlightDetails {
  id: string
  flight_number: string
  airline_name: string
  aircraft_registration: string
  aircraft_type: string
  origin_airport: string
  origin_airport_code: string
  destination_airport: string
  destination_airport_code: string
  scheduled_departure: string
  scheduled_arrival: string
  actual_departure?: string
  actual_arrival?: string
  flight_status: 'scheduled' | 'departed' | 'arrived' | 'cancelled' | 'delayed'
  distance_km: number
  flight_type: 'passenger' | 'cargo' | 'mixed'
}

export interface StorageAvailability {
  aircraft_id: string
  aircraft_registration: string
  total_capacity_tonnes: number
  current_cargo_tonnes: number
  available_capacity_tonnes: number
  utilization_percentage: number
  predicted_demand_tonnes: number
  confidence_score: number
}

export interface CargoLoadingProgress {
  flight_id: string
  flight_number: string
  total_cargo_tonnes: number
  loaded_cargo_tonnes: number
  loading_percentage: number
  estimated_completion_time?: string
  status: 'not_started' | 'in_progress' | 'completed' | 'delayed'
}

export interface CargoAnalyticsData {
  flight: FlightDetails
  storage_availability: StorageAvailability
  loading_progress: CargoLoadingProgress
  prediction: CargoPrediction
}

// Flight Delay Prediction Types
export interface Flight {
  id: string
  flightNumber: string
  origin: string
  destination: string
  scheduledDeparture: string
  scheduledArrival: string
  delayPrediction: FlightDelayPrediction
  weather: WeatherData
  inboundAircraft: {
    flightNumber: string
    status: 'on-time' | 'delayed' | 'arrived'
    delayMinutes: number
  } | null
  airportTraffic: AirportTraffic
}
