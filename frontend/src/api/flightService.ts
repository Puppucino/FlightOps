/**
 * Flight API Service
 * Functions for fetching flight data for dashboards
 */
import { apiClient } from './client'
import { Flight } from '../types'

/**
 * Fetch flights for the main Dashboard
 */
export const getDashboardFlights = async (): Promise<Flight[]> => {
  try {
    const response = await apiClient.get('/api/v1/flights/dashboard')
    return response.data
  } catch (error) {
    console.error('Failed to fetch dashboard flights:', error)
    throw error
  }
}

/**
 * Flight operations data for FlightOpsDashboard
 */
export interface FlightOperation {
  id: string
  status: string
  delay: number
  gate: string
  eta: string
  risk: number
  weather: string
  traffic: string
  origin?: string
  destination?: string
  flight_number?: string
  scheduled_departure?: string
}

/**
 * Fetch flight operations data
 */
export const getFlightOperations = async (): Promise<FlightOperation[]> => {
  try {
    const response = await apiClient.get('/api/v1/flights/operations')
    return response.data
  } catch (error) {
    console.error('Failed to fetch flight operations:', error)
    throw error
  }
}

/**
 * Weather data interface
 */
export interface WeatherData {
  airport_code: string
  airport_name: string
  icao_code: string | null
  temperature: number | null
  humidity: number | null
  wind_speed: number | null
  wind_direction: number | null
  visibility: number | null
  conditions: string
  pressure: number | null
  last_updated: string | null
  error: string | null
}

/**
 * Fetch weather data for airports
 */
export const getWeatherData = async (airportCode?: string): Promise<{ count: number; weather_data: WeatherData[] }> => {
  try {
    const params = airportCode ? { airport_code: airportCode } : {}
    const response = await apiClient.get('/api/v1/flights/weather', { params })
    return response.data
  } catch (error) {
    console.error('Failed to fetch weather data:', error)
    throw error
  }
}

/**
 * Traffic data interface
 */
export interface TrafficData {
  airport_code: string
  airport_name: string
  icao_code: string | null
  departures_next_hour: number
  arrivals_next_hour: number
  total_departures: number
  total_arrivals: number
  total_movements: number
  capacity: number
  utilization_percent: number
  traffic_level: 'Low' | 'Moderate' | 'High'
  time_window_hours: number
}

/**
 * Fetch traffic data for airports
 */
export const getTrafficData = async (airportCode?: string, hoursAhead: number = 24): Promise<{ count: number; traffic_data: TrafficData[] }> => {
  try {
    const params: any = { hours_ahead: hoursAhead }
    if (airportCode) {
      params.airport_code = airportCode
    }
    const response = await apiClient.get('/api/v1/flights/traffic', { params })
    return response.data
  } catch (error) {
    console.error('Failed to fetch traffic data:', error)
    throw error
  }
}
