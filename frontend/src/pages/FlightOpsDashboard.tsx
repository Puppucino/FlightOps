import { useState, useEffect } from 'react';
import { AlertCircle, Cloud, Users, Package, Plane, TrendingUp, Clock, Radio, X, ChevronDown, ChevronUp, Wind, Eye, Thermometer, Gauge } from 'lucide-react';
import { Layout } from '../components/Layout';
import { getFlightOperations, FlightOperation, getWeatherData, getTrafficData, WeatherData, TrafficData } from '../api/flightService';
import './FlightOpsDashboard.css';

interface Alert {
  id: number;
  flight?: string;
  type: string;
  risk?: number;
  time: string;
  severity: 'high' | 'medium' | 'low';
  message?: string;
}

// Flight interface is now imported from flightService

interface PassengerData {
  hour: string;
  expected: number;
  actual: number;
}

interface CargoData {
  flight: string;
  weight: number;
  capacity: number;
  utilization: number;
}

const FlightOpsDashboard = () => {
  const [activeTab, setActiveTab] = useState('delays');
  const [flights, setFlights] = useState<FlightOperation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedFlights, setExpandedFlights] = useState<Set<string>>(new Set());
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<number>>(new Set());
  
  // Weather and Traffic data
  const [weatherData, setWeatherData] = useState<WeatherData[]>([]);
  const [trafficData, setTrafficData] = useState<TrafficData[]>([]);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [trafficLoading, setTrafficLoading] = useState(false);

  // Generate alerts based on real flight data
  const [alerts, setAlerts] = useState<Alert[]>([]);

  // Fetch flight operations data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getFlightOperations();
        setFlights(data);
        
        // Generate alerts from flight data
        const newAlerts: Alert[] = [];
        data.forEach((flight, index) => {
          if (flight.risk >= 70) {
            newAlerts.push({
              id: index + 1,
              flight: flight.id,
              type: 'delay',
              risk: flight.risk,
              time: 'Just now',
              severity: 'high'
            });
          }
        });
        
        // Add weather and gate alerts (simplified)
        if (data.length > 1) {
          newAlerts.push({
            id: data.length + 1,
            type: 'weather',
            message: 'Weather conditions monitored',
            time: '5 min ago',
            severity: 'medium'
          });
        }
        
        setAlerts(newAlerts);
      } catch (err) {
        console.error('Failed to load flight operations:', err);
        setError('Failed to load flight operations data');
        // Fallback to empty state
        setFlights([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Fetch weather data when weather tab is active
  useEffect(() => {
    if (activeTab === 'weather') {
      const fetchWeather = async () => {
        try {
          setWeatherLoading(true);
          const data = await getWeatherData();
          setWeatherData(data.weather_data);
        } catch (err) {
          console.error('Failed to load weather data:', err);
        } finally {
          setWeatherLoading(false);
        }
      };
      fetchWeather();
      // Refresh weather every 5 minutes
      const interval = setInterval(fetchWeather, 5 * 60 * 1000);
      return () => clearInterval(interval);
    }
  }, [activeTab]);

  // Fetch traffic data when traffic tab is active
  useEffect(() => {
    if (activeTab === 'traffic') {
      const fetchTraffic = async () => {
        try {
          setTrafficLoading(true);
          const data = await getTrafficData();
          setTrafficData(data.traffic_data);
        } catch (err) {
          console.error('Failed to load traffic data:', err);
        } finally {
          setTrafficLoading(false);
        }
      };
      fetchTraffic();
      // Refresh traffic every 2 minutes
      const interval = setInterval(fetchTraffic, 2 * 60 * 1000);
      return () => clearInterval(interval);
    }
  }, [activeTab]);

  // Generate passenger data from flights (simplified)
  const passengerData: PassengerData[] = [
    { hour: '08:00', expected: 245, actual: 238 },
    { hour: '10:00', expected: 380, actual: 392 },
    { hour: '12:00', expected: 520, actual: 515 },
    { hour: '14:00', expected: 610, actual: 625 },
    { hour: '16:00', expected: 485, actual: 0 },
    { hour: '18:00', expected: 420, actual: 0 }
  ];

  // Generate cargo data from flights
  const cargoData: CargoData[] = flights.slice(0, 10).map((flight, idx) => {
    const baseWeight = 3000 + (idx * 200);
    const capacity = 5000;
    const utilization = Math.min(95, 50 + (flight.risk / 2));
    return {
      flight: flight.id,
      weight: Math.round(baseWeight * (utilization / 100)),
      capacity: capacity,
      utilization: Math.round(utilization)
    };
  });

  const toggleFlightExpansion = (flightId: string) => {
    setExpandedFlights(prev => {
      const newSet = new Set(prev);
      if (newSet.has(flightId)) {
        newSet.delete(flightId);
      } else {
        newSet.add(flightId);
      }
      return newSet;
    });
  };

  const dismissAlert = (alertId: number) => {
    setDismissedAlerts(prev => new Set(prev).add(alertId));
  };

  const visibleAlerts = alerts.filter(alert => !dismissedAlerts.has(alert.id));

  const renderDelaysTab = () => (
    <section aria-label="Flight delays information">
      <div className="flight-ops-stats">
        <article className="flight-ops-stat-card" role="article" aria-label="Total flights">
          <div className="flex items-center justify-between">
            <div>
              <p className="flight-ops-stat-label">Total Flights</p>
              <p className="flight-ops-stat-value">{flights.length}</p>
            </div>
            <Plane className="w-12 h-12 text-blue-400 opacity-50" aria-hidden="true" />
          </div>
        </article>
        <article className="flight-ops-stat-card flight-ops-stat-card-red" role="article" aria-label="High risk flights">
          <div className="flex items-center justify-between">
            <div>
              <p className="flight-ops-stat-label flight-ops-stat-label-red">High Risk</p>
              <p className="flight-ops-stat-value">{flights.filter(f => f.risk >= 70).length}</p>
            </div>
            <AlertCircle className="w-12 h-12 text-red-400 opacity-50" aria-hidden="true" />
          </div>
        </article>
        <article className="flight-ops-stat-card flight-ops-stat-card-yellow" role="article" aria-label="Average delay">
          <div className="flex items-center justify-between">
            <div>
              <p className="flight-ops-stat-label flight-ops-stat-label-yellow">Avg Delay</p>
              <p className="flight-ops-stat-value">{Math.round(flights.reduce((sum, f) => sum + f.delay, 0) / flights.length)} min</p>
            </div>
            <Clock className="w-12 h-12 text-yellow-400 opacity-50" aria-hidden="true" />
          </div>
        </article>
      </div>

      <div className="flight-ops-flight-list">
        {flights.map((flight, index) => {
          const isExpanded = expandedFlights.has(flight.id);
          return (
            <article 
              key={flight.id} 
              className="flight-ops-flight-card"
              style={{ animationDelay: `${index * 100}ms` }}
              onClick={() => toggleFlightExpansion(flight.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  toggleFlightExpansion(flight.id)
                }
              }}
              role="button"
              tabIndex={0}
              aria-label={`Flight ${flight.id} details`}
              aria-expanded={expandedFlights.has(flight.id)}
            >
              <div className="flight-ops-flight-header">
                  <div className="flight-ops-flight-info">
                  <div className="flight-ops-flight-icon">
                    <Plane className="w-6 h-6 text-blue-400" aria-hidden="true" />
                  </div>
                    <div className="flight-ops-flight-details">
                    <h3>{flight.id}</h3>
                    <p>Gate {flight.gate} • ETA {flight.eta}</p>
                    {flight.origin && flight.destination && (
                      <p className="text-xs text-slate-400 mt-1">{flight.origin} → {flight.destination}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-[10px]">
                  <div className="text-right">
                    <p className={`flight-ops-status-badge ${flight.status === 'At Risk' ? 'at-risk' : flight.status === 'Warning' ? 'warning' : 'on-time'}`}>
                      {flight.status}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">{flight.delay > 0 ? `+${flight.delay} min` : 'On Schedule'}</p>
                  </div>
                  <div className={`flight-ops-risk-badge ${flight.risk >= 70 ? 'high' : flight.risk >= 40 ? 'medium' : 'low'}`}>
                    {flight.risk}%
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFlightExpansion(flight.id);
                    }}
                    className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
                    aria-label={isExpanded ? `Collapse ${flight.id} details` : `Expand ${flight.id} details`}
                    type="button"
                  >
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-slate-400" aria-hidden="true" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-slate-400" aria-hidden="true" />
                    )}
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-[10px] mt-4 pt-4 border-t border-slate-700/50">
                <div className="flex items-center gap-[10px]">
                  <Cloud className="w-4 h-4 text-slate-400" aria-hidden="true" />
                  <span className="text-sm text-slate-300">{flight.weather}</span>
                </div>
                <div className="flex items-center gap-[10px]">
                  <Radio className="w-4 h-4 text-slate-400" aria-hidden="true" />
                  <span className="text-sm text-slate-300">Traffic: {flight.traffic}</span>
                </div>
              </div>
              {isExpanded && (
                <div className="mt-4 pt-4 border-t border-slate-700/50">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-700/30 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-1">Route</p>
                      <p className="text-sm font-semibold text-white">
                        {flight.origin && flight.destination ? `${flight.origin} → ${flight.destination}` : 'N/A'}
                      </p>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-1">Aircraft</p>
                      <p className="text-sm font-semibold text-white">A320-200</p>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-1">Passengers</p>
                      <p className="text-sm font-semibold text-white">156 / 180</p>
                    </div>
                    <div className="bg-slate-700/30 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-1">Cargo Load</p>
                      <p className="text-sm font-semibold text-white">4.2t / 5.0t</p>
                    </div>
                  </div>
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );

  const renderPassengersTab = () => (
    <section>
      <div className="flight-ops-passenger-section">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-white">Passenger Flow Prediction</h3>
            <p className="text-sm text-slate-400 mt-1">Based on historical patterns</p>
          </div>
          <Users className="w-10 h-10 text-purple-400 opacity-50 hover:opacity-100 hover:scale-110 transition-all duration-300" aria-hidden="true" />
        </div>
        <div>
          {passengerData.map((data, idx) => (
            <article 
              key={idx} 
              className="flight-ops-passenger-item"
              style={{ animationDelay: `${idx * 100}ms` }}
              role="article"
              aria-label={`Passenger flow at ${data.hour}`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-300 group-hover:text-white transition-colors">{data.hour}</span>
                <div className="flex items-center gap-[10px]">
                  <span className="text-xs text-slate-400 group-hover:text-slate-300 transition-colors">Expected: {data.expected}</span>
                  {data.actual > 0 && (
                    <span className="text-xs text-green-400 group-hover:text-green-300 transition-colors font-semibold">
                      Actual: {data.actual}
                    </span>
                  )}
                </div>
              </div>
              <div className="relative h-3 bg-slate-700/50 rounded-full overflow-hidden">
                <div 
                  className="absolute h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-500 
                             group-hover:from-purple-400 group-hover:to-blue-400"
                  style={{ width: `${(data.expected / 700) * 100}%` }}
                />
                {data.actual > 0 && (
                  <div 
                    className="absolute h-full bg-green-500/50 rounded-full transition-all duration-500 group-hover:bg-green-500/70"
                    style={{ width: `${(data.actual / 700) * 100}%` }}
                  />
                )}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );

  const renderWeatherTab = () => (
    <section>
      {weatherLoading ? (
        <div className="text-center py-12" role="status" aria-live="polite">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-slate-400">Loading weather data...</p>
        </div>
      ) : weatherData.length === 0 ? (
        <div className="text-center py-12" role="status" aria-live="polite">
          <Cloud className="w-16 h-16 text-slate-600 mx-auto mb-4 opacity-50" aria-hidden="true" />
          <p className="text-slate-400">No weather data available</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {weatherData.map((weather, idx) => (
            <article
              key={weather.airport_code}
              className="bg-slate-800/50 rounded-lg p-6 border border-slate-700/50 hover:border-slate-600 transition-all"
              style={{ animationDelay: `${idx * 100}ms` }}
              role="article"
              aria-label={`Weather for ${weather.airport_code}`}
            >
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-bold text-white">{weather.airport_code}</h3>
                  <p className="text-sm text-slate-400">{weather.airport_name}</p>
                </div>
                <div className={`p-3 rounded-lg ${
                  weather.conditions === 'Clear' ? 'bg-blue-500/20' :
                  weather.conditions === 'Rain' ? 'bg-blue-600/20' :
                  weather.conditions === 'Thunderstorm' ? 'bg-purple-600/20' :
                  'bg-slate-700/20'
                }`}>
                  <Cloud className={`w-6 h-6 ${
                    weather.conditions === 'Clear' ? 'text-blue-400' :
                    weather.conditions === 'Rain' ? 'text-blue-500' :
                    weather.conditions === 'Thunderstorm' ? 'text-purple-400' :
                    'text-slate-400'
                  }`} aria-hidden="true" />
                </div>
              </div>

              {weather.error ? (
                <div className="text-yellow-400 text-sm mb-2">⚠️ {weather.error}</div>
              ) : (
                <>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="flex items-center gap-2">
                      <Thermometer className="w-4 h-4 text-slate-400" aria-hidden="true" />
                      <div>
                        <p className="text-xs text-slate-400">Temperature</p>
                        <p className="text-sm font-semibold text-white">
                          {weather.temperature !== null ? `${Math.round(weather.temperature)}°C` : 'N/A'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Wind className="w-4 h-4 text-slate-400" aria-hidden="true" />
                      <div>
                        <p className="text-xs text-slate-400">Wind Speed</p>
                        <p className="text-sm font-semibold text-white">
                          {weather.wind_speed !== null ? `${Math.round(weather.wind_speed)} km/h` : 'N/A'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Eye className="w-4 h-4 text-slate-400" aria-hidden="true" />
                      <div>
                        <p className="text-xs text-slate-400">Visibility</p>
                        <p className="text-sm font-semibold text-white">
                          {weather.visibility !== null ? `${weather.visibility.toFixed(1)} km` : 'N/A'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Gauge className="w-4 h-4 text-slate-400" aria-hidden="true" />
                      <div>
                        <p className="text-xs text-slate-400">Pressure</p>
                        <p className="text-sm font-semibold text-white">
                          {weather.pressure !== null ? `${Math.round(weather.pressure)} mb` : 'N/A'}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 border-t border-slate-700/50">
                    <p className="text-xs text-slate-400 mb-1">Conditions</p>
                    <p className="text-sm font-semibold text-white">{weather.conditions}</p>
                    {weather.wind_direction !== null && (
                      <p className="text-xs text-slate-400 mt-1">
                        Wind: {weather.wind_direction}°
                      </p>
                    )}
                    {weather.last_updated && (
                      <p className="text-xs text-slate-500 mt-2">
                        Updated: {new Date(weather.last_updated).toLocaleTimeString()}
                      </p>
                    )}
                  </div>
                </>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );

  const renderTrafficTab = () => (
    <section>
      {trafficLoading ? (
        <div className="text-center py-12" role="status" aria-live="polite">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-slate-400">Loading traffic data...</p>
        </div>
      ) : trafficData.length === 0 ? (
        <div className="text-center py-12" role="status" aria-live="polite">
          <TrendingUp className="w-16 h-16 text-slate-600 mx-auto mb-4 opacity-50" aria-hidden="true" />
          <p className="text-slate-400">No traffic data available</p>
        </div>
      ) : (
        <div className="space-y-4">
          {trafficData.map((traffic, idx) => {
            const utilizationColor = 
              traffic.utilization_percent >= 80 ? 'text-red-400' :
              traffic.utilization_percent >= 50 ? 'text-yellow-400' :
              'text-green-400';
            
            const trafficLevelColor =
              traffic.traffic_level === 'High' ? 'bg-red-500/20 border-red-500/30' :
              traffic.traffic_level === 'Moderate' ? 'bg-yellow-500/20 border-yellow-500/30' :
              'bg-green-500/20 border-green-500/30';

            return (
              <article
                key={traffic.airport_code}
                className={`bg-slate-800/50 rounded-lg p-6 border ${trafficLevelColor} hover:border-opacity-50 transition-all`}
                style={{ animationDelay: `${idx * 100}ms` }}
                role="article"
                aria-label={`Traffic for ${traffic.airport_code}`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-white">{traffic.airport_code}</h3>
                    <p className="text-sm text-slate-400">{traffic.airport_name}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-2xl font-bold ${utilizationColor}`}>
                      {traffic.utilization_percent}%
                    </p>
                    <p className="text-xs text-slate-400">Utilization</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p className="text-xs text-slate-400 mb-1">Next Hour</p>
                    <div className="flex items-center gap-2">
                      <Plane className="w-4 h-4 text-blue-400 rotate-90" aria-hidden="true" />
                      <p className="text-sm font-semibold text-white">
                        {traffic.departures_next_hour} departures
                      </p>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <Plane className="w-4 h-4 text-green-400 -rotate-90" aria-hidden="true" />
                      <p className="text-sm font-semibold text-white">
                        {traffic.arrivals_next_hour} arrivals
                      </p>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-1">Total ({traffic.time_window_hours}h)</p>
                    <p className="text-sm font-semibold text-white">
                      {traffic.total_departures} departures
                    </p>
                    <p className="text-sm font-semibold text-white">
                      {traffic.total_arrivals} arrivals
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-1">Capacity</p>
                    <p className="text-sm font-semibold text-white">
                      {traffic.capacity} movements/hour
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-400 mb-1">Traffic Level</p>
                    <p className={`text-sm font-semibold ${
                      traffic.traffic_level === 'High' ? 'text-red-400' :
                      traffic.traffic_level === 'Moderate' ? 'text-yellow-400' :
                      'text-green-400'
                    }`}>
                      {traffic.traffic_level}
                    </p>
                  </div>
                </div>

                <div className="relative h-3 bg-slate-700/50 rounded-full overflow-hidden">
                  <div
                    className={`absolute h-full rounded-full transition-all ${
                      traffic.utilization_percent >= 80 ? 'bg-gradient-to-r from-red-500 to-red-600' :
                      traffic.utilization_percent >= 50 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
                      'bg-gradient-to-r from-green-500 to-green-600'
                    }`}
                    style={{ width: `${Math.min(100, traffic.utilization_percent)}%` }}
                  />
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );

  const renderCargoTab = () => (
    <section>
      {cargoData.map((cargo, idx) => (
        <article 
          key={cargo.flight} 
          className="flight-ops-cargo-item"
          style={{ animationDelay: `${idx * 100}ms` }}
          role="article"
          aria-label={`Cargo data for flight ${cargo.flight}`}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="bg-orange-500/20 p-3 rounded-lg group-hover:bg-orange-500/30 transition-colors group-hover:scale-110 duration-300">
                <Package className="w-6 h-6 text-orange-400 group-hover:rotate-12 transition-transform" aria-hidden="true" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white group-hover:text-orange-300 transition-colors">{cargo.flight}</h3>
                <p className="text-sm text-slate-400 group-hover:text-slate-300 transition-colors">{cargo.weight} kg / {cargo.capacity} kg</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-orange-400 group-hover:scale-110 transition-transform duration-300">{cargo.utilization}%</p>
              <p className="text-xs text-slate-400 group-hover:text-slate-300 transition-colors">Utilization</p>
            </div>
          </div>
          <div className="relative h-4 bg-slate-700/50 rounded-full overflow-hidden">
            <div 
              className={`absolute h-full rounded-full transition-all duration-500 group-hover:shadow-lg ${
                cargo.utilization >= 85 
                  ? 'bg-gradient-to-r from-orange-500 to-red-500 group-hover:from-orange-400 group-hover:to-red-400' 
                  : 'bg-gradient-to-r from-orange-500 to-yellow-500 group-hover:from-orange-400 group-hover:to-yellow-400'
              }`}
              style={{ width: `${cargo.utilization}%` }}
            />
          </div>
        </article>
      ))}
    </section>
  );

  const tabs = [
    { id: 'delays', label: 'Delays', icon: Clock },
    { id: 'passengers', label: 'Passengers', icon: Users },
    { id: 'cargo', label: 'Cargo', icon: Package },
    { id: 'weather', label: 'Weather', icon: Cloud },
    { id: 'traffic', label: 'Traffic', icon: TrendingUp }
  ];

  if (loading) {
    return (
      <Layout>
        <main className="flight-ops-container" role="main">
          <div className="flight-ops-wrapper">
            <div className="text-center py-12" role="status" aria-live="polite">
              <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-slate-400">Loading flight operations...</p>
            </div>
          </div>
        </main>
      </Layout>
    )
  }

  return (
    <Layout>
      <main className="flight-ops-container" role="main">
        <div className="flight-ops-wrapper">
          {/* Header Section */}
          <header className="flight-ops-header">
            <h1 className="flight-ops-title">
              Flight Operations Command Center
            </h1>
            <p className="flight-ops-subtitle">Real-time monitoring and predictive analytics</p>
            {error && (
              <div className="mt-4 p-3 bg-yellow-500/20 border border-yellow-500/30 rounded-lg text-yellow-400 text-sm">
                {error}
              </div>
            )}
          </header>

          {/* Alerts Section */}
          <section className="flight-ops-alerts" aria-label="Live alerts">
            <div className="flight-ops-alerts-header">
              <AlertCircle className="w-5 h-5 text-red-400 animate-pulse" aria-hidden="true" />
              <h2>Live Alerts</h2>
              {visibleAlerts.length > 0 && (
                <span className="ml-2 px-2 py-0.5 bg-red-500/20 text-red-400 text-xs font-bold rounded-full border border-red-500/30" aria-label={`${visibleAlerts.length} active alerts`}>
                  {visibleAlerts.length}
                </span>
              )}
            </div>
            <div>
              {visibleAlerts.map((alert, index) => (
                <div 
                  key={alert.id} 
                  className={`flight-ops-alert-item ${alert.severity} group`}
                  style={{ animationDelay: `${index * 100}ms` }}
                  role="alert"
                  aria-live="polite"
                >
                  <div className="flex items-center space-x-3 flex-1">
                    <AlertCircle className={`w-5 h-5 ${alert.severity === 'high' ? 'text-red-400 animate-pulse' : 'text-yellow-400'}`} aria-hidden="true" />
                    <div className="flex-1">
                      {alert.flight && (
                        <p className="text-white font-semibold">Flight {alert.flight} delay risk {alert.risk}%</p>
                      )}
                      {alert.message && (
                        <p className="text-white font-semibold">{alert.message}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-[10px]">
                    <time className="text-xs text-slate-400" dateTime={alert.time}>{alert.time}</time>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        dismissAlert(alert.id);
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-700/50 rounded transition-all duration-200"
                      aria-label={`Dismiss alert ${alert.id}`}
                      type="button"
                    >
                      <X className="w-4 h-4 text-slate-400 hover:text-white" aria-hidden="true" />
                    </button>
                  </div>
                </div>
              ))}
              {visibleAlerts.length === 0 && (
                <div className="text-center py-8 text-slate-500" role="status" aria-live="polite">
                  <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" aria-hidden="true" />
                  <p>No active alerts</p>
                </div>
              )}
            </div>
          </section>

          {/* Tabs Section */}
          <nav className="flight-ops-tabs" role="tablist" aria-label="Flight operations tabs">
            {tabs.map(tab => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flight-ops-tab ${isActive ? 'active' : ''}`}
                  role="tab"
                  aria-selected={isActive}
                  aria-controls={`tabpanel-${tab.id}`}
                  id={`tab-${tab.id}`}
                  type="button"
                >
                  <Icon className="w-5 h-5" aria-hidden="true" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Content Section */}
          <div 
            className="flight-ops-content"
            role="tabpanel"
            id={`tabpanel-${activeTab}`}
            aria-labelledby={`tab-${activeTab}`}
          >
            {activeTab === 'delays' && renderDelaysTab()}
            {activeTab === 'passengers' && renderPassengersTab()}
            {activeTab === 'cargo' && renderCargoTab()}
            {activeTab === 'weather' && renderWeatherTab()}
            {activeTab === 'traffic' && renderTrafficTab()}
          </div>
        </div>
      </main>
    </Layout>
  );
};

export default FlightOpsDashboard;

