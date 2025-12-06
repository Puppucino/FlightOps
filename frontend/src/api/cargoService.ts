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
