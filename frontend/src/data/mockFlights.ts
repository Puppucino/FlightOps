import { Flight } from "../types"

export const mockFlights: Flight[] = [
  {
    id: "1",
    flightNumber: "AK123",
    origin: "KUL",
    destination: "SIN",
    scheduledDeparture: "08:00",
    scheduledArrival: "09:30",
    delayPrediction: {
      delay_probability: 0.75,
      estimated_delay_minutes: 45,
      confidence: 0.88
    },
    weather: {
      temperature: 28,
      humidity: 85,
      wind_speed: 25,
      visibility: 8,
      conditions: "Rain"
    },
    inboundAircraft: {
      flightNumber: "AK456",
      status: "delayed",
      delayMinutes: 30
    },
    airportTraffic: {
      airport_code: "KUL",
      current_traffic: 45,
      capacity: 60
    }
  },
  {
    id: "2",
    flightNumber: "AK456",
    origin: "SIN",
    destination: "BKK",
    scheduledDeparture: "10:30",
    scheduledArrival: "12:00",
    delayPrediction: {
      delay_probability: 0.45,
      estimated_delay_minutes: 20,
      confidence: 0.82
    },
    weather: {
      temperature: 32,
      humidity: 70,
      wind_speed: 15,
      visibility: 12,
      conditions: "Clear"
    },
    inboundAircraft: {
      flightNumber: "AK789",
      status: "on-time",
      delayMinutes: 0
    },
    airportTraffic: {
      airport_code: "SIN",
      current_traffic: 32,
      capacity: 50
    }
  },
  {
    id: "3",
    flightNumber: "AK789",
    origin: "BKK",
    destination: "CGK",
    scheduledDeparture: "14:15",
    scheduledArrival: "16:45",
    delayPrediction: {
      delay_probability: 0.25,
      estimated_delay_minutes: 8,
      confidence: 0.90
    },
    weather: {
      temperature: 35,
      humidity: 60,
      wind_speed: 10,
      visibility: 15,
      conditions: "Sunny"
    },
    inboundAircraft: {
      flightNumber: "AK101",
      status: "on-time",
      delayMinutes: 0
    },
    airportTraffic: {
      airport_code: "BKK",
      current_traffic: 28,
      capacity: 55
    }
  },
  {
    id: "4",
    flightNumber: "AK101",
    origin: "CGK",
    destination: "MNL",
    scheduledDeparture: "16:45",
    scheduledArrival: "20:30",
    delayPrediction: {
      delay_probability: 0.85,
      estimated_delay_minutes: 55,
      confidence: 0.91
    },
    weather: {
      temperature: 30,
      humidity: 90,
      wind_speed: 30,
      visibility: 5,
      conditions: "Heavy Rain"
    },
    inboundAircraft: {
      flightNumber: "AK202",
      status: "delayed",
      delayMinutes: 45
    },
    airportTraffic: {
      airport_code: "CGK",
      current_traffic: 58,
      capacity: 60
    }
  },
  {
    id: "5",
    flightNumber: "AK202",
    origin: "MNL",
    destination: "HKG",
    scheduledDeparture: "09:20",
    scheduledArrival: "11:15",
    delayPrediction: {
      delay_probability: 0.35,
      estimated_delay_minutes: 15,
      confidence: 0.79
    },
    weather: {
      temperature: 29,
      humidity: 75,
      wind_speed: 18,
      visibility: 10,
      conditions: "Cloudy"
    },
    inboundAircraft: {
      flightNumber: "AK303",
      status: "on-time",
      delayMinutes: 0
    },
    airportTraffic: {
      airport_code: "MNL",
      current_traffic: 35,
      capacity: 50
    }
  },
  {
    id: "6",
    flightNumber: "AK303",
    origin: "HKG",
    destination: "TPE",
    scheduledDeparture: "11:50",
    scheduledArrival: "13:20",
    delayPrediction: {
      delay_probability: 0.55,
      estimated_delay_minutes: 25,
      confidence: 0.84
    },
    weather: {
      temperature: 26,
      humidity: 80,
      wind_speed: 22,
      visibility: 9,
      conditions: "Light Rain"
    },
    inboundAircraft: {
      flightNumber: "AK404",
      status: "delayed",
      delayMinutes: 20
    },
    airportTraffic: {
      airport_code: "HKG",
      current_traffic: 48,
      capacity: 55
    }
  }
]

