/**
 * Cargo Analytics API Service
 * Functions for fetching cargo-related data
 */
import { apiClient } from './client'
import { CargoAnalyticsData, StorageAvailability, CargoLoadingProgress, FlightDetails } from '../types'
import { generateMockCargoAnalytics, generateMockFlights } from '../utils/mockData'

// Set to true to use mock data when backend is not available
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true' || false

/**
 * Fetch cargo analytics data for a specific flight
 */
export const getCargoAnalytics = async (flightId: string): Promise<CargoAnalyticsData> => {
  if (USE_MOCK_DATA) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    return generateMockCargoAnalytics(flightId)
  }
  
  try {
    const response = await apiClient.get(`/api/v1/cargo/analytics/${flightId}`)
    return response.data
  } catch (error) {
    console.warn('API call failed, using mock data:', error)
    return generateMockCargoAnalytics(flightId)
  }
}

/**
 * Fetch cargo analytics data for a flight by flight number
 */
export const getCargoAnalyticsByFlightNumber = async (flightNumber: string): Promise<CargoAnalyticsData> => {
  if (USE_MOCK_DATA) {
    await new Promise(resolve => setTimeout(resolve, 500))
    return generateMockCargoAnalytics()
  }
  
  try {
    const response = await apiClient.get(`/api/v1/cargo/analytics/flight/${flightNumber}`)
    return response.data
  } catch (error) {
    console.warn('API call failed, using mock data:', error)
    return generateMockCargoAnalytics()
  }
}

/**
 * Fetch storage availability for an aircraft
 */
export const getStorageAvailability = async (aircraftId: string): Promise<StorageAvailability> => {
  if (USE_MOCK_DATA) {
    await new Promise(resolve => setTimeout(resolve, 300))
    const mock = generateMockCargoAnalytics()
    return mock.storage_availability
  }
  
  try {
    const response = await apiClient.get(`/api/v1/cargo/storage/${aircraftId}`)
    return response.data
  } catch (error) {
    console.warn('API call failed, using mock data:', error)
    const mock = generateMockCargoAnalytics()
    return mock.storage_availability
  }
}

/**
 * Fetch cargo loading progress for a flight
 */
export const getCargoLoadingProgress = async (flightId: string): Promise<CargoLoadingProgress> => {
  if (USE_MOCK_DATA) {
    await new Promise(resolve => setTimeout(resolve, 300))
    const mock = generateMockCargoAnalytics(flightId)
    return mock.loading_progress
  }
  
  try {
    const response = await apiClient.get(`/api/v1/cargo/loading/${flightId}`)
    return response.data
  } catch (error) {
    console.warn('API call failed, using mock data:', error)
    const mock = generateMockCargoAnalytics(flightId)
    return mock.loading_progress
  }
}

/**
 * Fetch flight details
 */
export const getFlightDetails = async (flightId: string): Promise<FlightDetails> => {
  if (USE_MOCK_DATA) {
    await new Promise(resolve => setTimeout(resolve, 300))
    const mock = generateMockCargoAnalytics(flightId)
    return mock.flight
  }
  
  try {
    const response = await apiClient.get(`/api/v1/flights/${flightId}`)
    return response.data
  } catch (error) {
    console.warn('API call failed, using mock data:', error)
    const mock = generateMockCargoAnalytics(flightId)
    return mock.flight
  }
}

/**
 * Fetch all flights with cargo data
 */
export const getCargoFlights = async (): Promise<FlightDetails[]> => {
  if (USE_MOCK_DATA) {
    await new Promise(resolve => setTimeout(resolve, 500))
    return generateMockFlights()
  }
  
  try {
    const response = await apiClient.get('/api/v1/flights/cargo')
    return response.data
  } catch (error) {
    console.warn('API call failed, using mock data:', error)
    return generateMockFlights()
  }
}

/**
 * Predict cargo capacity for a flight
 */
export interface CargoCapacityPredictionRequest {
  aircraft_type: string
  passenger_count: number
  origin: string
  destination: string
  flight_date: string
  fuel_weight_kg?: number
  days_before_flight?: number
}

export interface CargoCapacityPredictionResponse {
  available_weight_kg: number
  available_volume_m3: number
  confidence_interval_95_lower_weight: number
  confidence_interval_95_upper_weight: number
  confidence_interval_95_lower_volume: number
  confidence_interval_95_upper_volume: number
  utilization_percentage: number
  weight_utilization_pct: number
  volume_utilization_pct: number
  constraining_factor: string
  predicted_cargo_demand_kg: number
  overbooking_risk: string
  baggage_prediction: {
    predicted_baggage_weight_kg: number
    predicted_baggage_volume_m3: number
    confidence_interval_95_lower_weight: number
    confidence_interval_95_upper_weight: number
    days_before_flight: number
  }
  aircraft_max_cargo_weight_kg: number
  aircraft_max_cargo_volume_m3: number
  predicted_baggage_weight_kg: number
  predicted_baggage_volume_m3: number
  fuel_weight_kg: number
  days_before_flight: number
}

export const predictCargoCapacity = async (
  request: CargoCapacityPredictionRequest
): Promise<CargoCapacityPredictionResponse> => {
  if (USE_MOCK_DATA) {
    await new Promise(resolve => setTimeout(resolve, 500))
    // Return mock prediction
    const mockWeight = 8000
    const mockVolume = 150
    return {
      available_weight_kg: mockWeight,
      available_volume_m3: mockVolume,
      confidence_interval_95_lower_weight: mockWeight * 0.85,
      confidence_interval_95_upper_weight: mockWeight * 1.15,
      confidence_interval_95_lower_volume: mockVolume * 0.85,
      confidence_interval_95_upper_volume: mockVolume * 1.15,
      utilization_percentage: 65.0,
      weight_utilization_pct: 65.0,
      volume_utilization_pct: 60.0,
      constraining_factor: 'weight',
      predicted_cargo_demand_kg: 7500,
      overbooking_risk: 'low',
      baggage_prediction: {
        predicted_baggage_weight_kg: 2500,
        predicted_baggage_volume_m3: 37.5,
        confidence_interval_95_lower_weight: 2300,
        confidence_interval_95_upper_weight: 2700,
        days_before_flight: request.days_before_flight || 0
      },
      aircraft_max_cargo_weight_kg: 20500,
      aircraft_max_cargo_volume_m3: 190,
      predicted_baggage_weight_kg: 2500,
      predicted_baggage_volume_m3: 37.5,
      fuel_weight_kg: 10000,
      days_before_flight: request.days_before_flight || 0
    }
  }
  
  try {
    const response = await apiClient.post('/api/v1/cargo/predict-capacity', request)
    return response.data
  } catch (error) {
    console.error('Failed to predict cargo capacity:', error)
    throw error
  }
}

/**
 * Get cargo analytics with prediction support
 */
export const getCargoAnalyticsWithPrediction = async (
  flightId: string,
  daysBeforeFlight: number = 0
): Promise<CargoAnalyticsData> => {
  try {
    const response = await apiClient.get(
      `/api/v1/cargo/analytics/${flightId}?days_before_flight=${daysBeforeFlight}`
    )
    return response.data
  } catch (error) {
    console.warn('API call failed, using mock data:', error)
    return getCargoAnalytics(flightId)
  }
}
