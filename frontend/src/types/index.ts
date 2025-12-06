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

