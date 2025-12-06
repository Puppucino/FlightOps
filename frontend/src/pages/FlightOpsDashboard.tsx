import React, { useState } from 'react';
import { AlertCircle, Cloud, Users, Package, Plane, TrendingUp, Clock, Radio, X, ChevronDown, ChevronUp } from 'lucide-react';
import { Layout } from '../components/Layout';
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

interface Flight {
  id: string;
  status: string;
  delay: number;
  gate: string;
  eta: string;
  risk: number;
  weather: string;
  traffic: string;
}

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
  const [alerts, setAlerts] = useState<Alert[]>([
    { id: 1, flight: 'AK546', type: 'delay', risk: 78, time: '2 min ago', severity: 'high' },
    { id: 2, type: 'weather', message: 'Weather disruption predicted at 3:40 PM', time: '5 min ago', severity: 'medium' },
    { id: 3, type: 'gate', message: 'Gate clash detected between AK310 and AK312', time: '8 min ago', severity: 'high' }
  ]);
  const [expandedFlights, setExpandedFlights] = useState<Set<string>>(new Set());
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<number>>(new Set());
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);

  const [flights, setFlights] = useState<Flight[]>([
    { id: 'AK546', status: 'At Risk', delay: 45, gate: 'A12', eta: '14:30', risk: 78, weather: 'Moderate', traffic: 'High' },
    { id: 'AK310', status: 'On Time', delay: 0, gate: 'B5', eta: '15:15', risk: 12, weather: 'Clear', traffic: 'Normal' },
    { id: 'AK312', status: 'Warning', delay: 15, gate: 'B5', eta: '15:20', risk: 45, weather: 'Clear', traffic: 'Normal' },
    { id: 'AK789', status: 'On Time', delay: 0, gate: 'C8', eta: '16:00', risk: 8, weather: 'Clear', traffic: 'Low' }
  ]);

  const passengerData: PassengerData[] = [
    { hour: '08:00', expected: 245, actual: 238 },
    { hour: '10:00', expected: 380, actual: 392 },
    { hour: '12:00', expected: 520, actual: 515 },
    { hour: '14:00', expected: 610, actual: 625 },
    { hour: '16:00', expected: 485, actual: 0 },
    { hour: '18:00', expected: 420, actual: 0 }
  ];

  const cargoData: CargoData[] = [
    { flight: 'AK546', weight: 4200, capacity: 5000, utilization: 84 },
    { flight: 'AK310', weight: 3800, capacity: 5000, utilization: 76 },
    { flight: 'AK312', weight: 4500, capacity: 5000, utilization: 90 },
    { flight: 'AK789', weight: 2900, capacity: 5000, utilization: 58 }
  ];

  const getRiskColor = (risk: number) => {
    if (risk >= 70) return 'text-red-500 bg-red-500/10 border-red-500/20';
    if (risk >= 40) return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
    return 'text-green-500 bg-green-500/10 border-green-500/20';
  };

  const getStatusColor = (status: string) => {
    if (status === 'At Risk') return 'bg-red-500/20 text-red-400 border-red-500/30';
    if (status === 'Warning') return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    return 'bg-green-500/20 text-green-400 border-green-500/30';
  };

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
    <div className="space-y-4 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20 rounded-xl p-6 
                     hover:from-blue-500/20 hover:to-blue-600/10 hover:border-blue-500/40 
                     transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-blue-500/20
                     cursor-pointer group"
          onMouseEnter={() => setHoveredCard('total')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-400 text-sm font-medium group-hover:text-blue-300 transition-colors">Total Flights</p>
              <p className="text-3xl font-bold text-white mt-2 group-hover:scale-110 transition-transform duration-300">{flights.length}</p>
            </div>
            <Plane className={`w-12 h-12 text-blue-400 opacity-50 transition-all duration-300 ${hoveredCard === 'total' ? 'opacity-100 scale-110 rotate-12' : ''}`} />
          </div>
        </div>
        <div 
          className="bg-gradient-to-br from-red-500/10 to-red-600/5 border border-red-500/20 rounded-xl p-6 
                     hover:from-red-500/20 hover:to-red-600/10 hover:border-red-500/40 
                     transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-red-500/20
                     cursor-pointer group"
          onMouseEnter={() => setHoveredCard('risk')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-400 text-sm font-medium group-hover:text-red-300 transition-colors">High Risk</p>
              <p className="text-3xl font-bold text-white mt-2 group-hover:scale-110 transition-transform duration-300">{flights.filter(f => f.risk >= 70).length}</p>
            </div>
            <AlertCircle className={`w-12 h-12 text-red-400 opacity-50 transition-all duration-300 ${hoveredCard === 'risk' ? 'opacity-100 scale-110 animate-pulse' : ''}`} />
          </div>
        </div>
        <div 
          className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 border border-yellow-500/20 rounded-xl p-6 
                     hover:from-yellow-500/20 hover:to-yellow-600/10 hover:border-yellow-500/40 
                     transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-yellow-500/20
                     cursor-pointer group"
          onMouseEnter={() => setHoveredCard('delay')}
          onMouseLeave={() => setHoveredCard(null)}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-400 text-sm font-medium group-hover:text-yellow-300 transition-colors">Avg Delay</p>
              <p className="text-3xl font-bold text-white mt-2 group-hover:scale-110 transition-transform duration-300">{Math.round(flights.reduce((sum, f) => sum + f.delay, 0) / flights.length)} min</p>
            </div>
            <Clock className={`w-12 h-12 text-yellow-400 opacity-50 transition-all duration-300 ${hoveredCard === 'delay' ? 'opacity-100 scale-110' : ''}`} />
          </div>
        </div>
      </div>

      <div className="space-y-3">
        {flights.map((flight, index) => {
          const isExpanded = expandedFlights.has(flight.id);
          return (
            <div 
              key={flight.id} 
              className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-5 
                         hover:border-slate-600/50 hover:bg-slate-800/70 hover:shadow-xl hover:shadow-slate-900/50
                         transition-all duration-300 hover:scale-[1.02] cursor-pointer group
                         animate-in fade-in slide-in-from-bottom-4"
              style={{ animationDelay: `${index * 100}ms` }}
              onClick={() => toggleFlightExpansion(flight.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="bg-blue-500/20 p-3 rounded-lg group-hover:bg-blue-500/30 transition-colors">
                    <Plane className="w-6 h-6 text-blue-400 group-hover:scale-110 transition-transform" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white group-hover:text-blue-300 transition-colors">{flight.id}</h3>
                    <p className="text-sm text-slate-400 group-hover:text-slate-300 transition-colors">Gate {flight.gate} • ETA {flight.eta}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className={`text-sm font-semibold px-3 py-1 rounded-full border transition-all ${getStatusColor(flight.status)} hover:scale-105`}>
                      {flight.status}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">{flight.delay > 0 ? `+${flight.delay} min` : 'On Schedule'}</p>
                  </div>
                  <div className={`text-2xl font-bold px-4 py-2 rounded-lg border transition-all hover:scale-110 ${getRiskColor(flight.risk)}`}>
                    {flight.risk}%
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleFlightExpansion(flight.id);
                    }}
                    className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
                  >
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-slate-400" />
                    )}
                  </button>
                </div>
              </div>
              <div className={`flex items-center space-x-6 mt-4 pt-4 border-t border-slate-700/50 transition-all duration-300 ${isExpanded ? 'opacity-100' : 'opacity-100'}`}>
                <div className="flex items-center space-x-2">
                  <Cloud className="w-4 h-4 text-slate-400" />
                  <span className="text-sm text-slate-300">{flight.weather}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Radio className="w-4 h-4 text-slate-400" />
                  <span className="text-sm text-slate-300">Traffic: {flight.traffic}</span>
                </div>
              </div>
              {isExpanded && (
                <div className="mt-4 pt-4 border-t border-slate-700/50 animate-in fade-in slide-in-from-top-2">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-700/30 rounded-lg p-3">
                      <p className="text-xs text-slate-400 mb-1">Route</p>
                      <p className="text-sm font-semibold text-white">KUL → SIN</p>
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
            </div>
          );
        })}
      </div>
    </div>
  );

  const renderPassengersTab = () => (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20 rounded-xl p-6 
                      hover:from-purple-500/20 hover:to-purple-600/10 hover:border-purple-500/40 
                      transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/20">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-white">Passenger Flow Prediction</h3>
            <p className="text-sm text-slate-400 mt-1">Based on historical patterns</p>
          </div>
          <Users className="w-10 h-10 text-purple-400 opacity-50 hover:opacity-100 hover:scale-110 transition-all duration-300" />
        </div>
        <div className="space-y-4">
          {passengerData.map((data, idx) => (
            <div 
              key={idx} 
              className="bg-slate-800/30 rounded-lg p-4 hover:bg-slate-800/50 transition-all duration-300 
                         hover:scale-[1.02] hover:shadow-lg cursor-pointer group
                         animate-in fade-in slide-in-from-left-4"
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-300 group-hover:text-white transition-colors">{data.hour}</span>
                <div className="flex items-center space-x-4">
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
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderCargoTab = () => (
    <div className="space-y-4 animate-in fade-in duration-500">
      {cargoData.map((cargo, idx) => (
        <div 
          key={cargo.flight} 
          className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-6 
                     hover:border-slate-600/50 hover:bg-slate-800/70 hover:shadow-xl hover:shadow-slate-900/50
                     transition-all duration-300 hover:scale-[1.02] cursor-pointer group
                     animate-in fade-in slide-in-from-bottom-4"
          style={{ animationDelay: `${idx * 100}ms` }}
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="bg-orange-500/20 p-3 rounded-lg group-hover:bg-orange-500/30 transition-colors group-hover:scale-110 duration-300">
                <Package className="w-6 h-6 text-orange-400 group-hover:rotate-12 transition-transform" />
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
        </div>
      ))}
    </div>
  );

  const tabs = [
    { id: 'delays', label: 'Delays', icon: Clock },
    { id: 'passengers', label: 'Passengers', icon: Users },
    { id: 'cargo', label: 'Cargo', icon: Package },
    { id: 'weather', label: 'Weather', icon: Cloud },
    { id: 'traffic', label: 'Traffic', icon: TrendingUp }
  ];

  return (
    <Layout>
      <div className="flight-ops-container">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        </div>
        
        <div className="max-w-7xl mx-auto relative z-10">
        <div className="mb-8 animate-in fade-in slide-in-from-top-4 duration-700">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent 
                         hover:from-blue-300 hover:via-purple-300 hover:to-pink-300 transition-all duration-300">
            Flight Operations Command Center
          </h1>
          <p className="text-slate-400 mt-2 hover:text-slate-300 transition-colors">Real-time monitoring and predictive analytics</p>
        </div>

        <div className="mb-6 bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-xl p-4 hover:border-slate-600/50 transition-all duration-300">
          <h2 className="text-lg font-semibold text-white mb-3 flex items-center">
            <AlertCircle className="w-5 h-5 mr-2 text-red-400 animate-pulse" />
            Live Alerts
            {visibleAlerts.length > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-red-500/20 text-red-400 text-xs font-bold rounded-full border border-red-500/30">
                {visibleAlerts.length}
              </span>
            )}
          </h2>
          <div className="space-y-2">
            {visibleAlerts.map((alert, index) => (
              <div 
                key={alert.id} 
                className={`flex items-center justify-between p-3 rounded-lg transition-all duration-300 hover:scale-[1.02] group animate-in fade-in slide-in-from-right-4 ${
                  alert.severity === 'high' 
                    ? 'bg-red-500/10 border border-red-500/30 hover:bg-red-500/20 hover:border-red-500/50 hover:shadow-lg hover:shadow-red-500/20' 
                    : 'bg-yellow-500/10 border border-yellow-500/30 hover:bg-yellow-500/20 hover:border-yellow-500/50 hover:shadow-lg hover:shadow-yellow-500/20'
                }`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-center space-x-3 flex-1">
                  <AlertCircle className={`w-5 h-5 ${alert.severity === 'high' ? 'text-red-400 animate-pulse' : 'text-yellow-400'} group-hover:scale-110 transition-transform`} />
                  <div className="flex-1">
                    {alert.flight && (
                      <p className="text-white font-semibold group-hover:text-red-300 transition-colors">Flight {alert.flight} delay risk {alert.risk}%</p>
                    )}
                    {alert.message && (
                      <p className="text-white font-semibold group-hover:text-yellow-300 transition-colors">{alert.message}</p>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-slate-400">{alert.time}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      dismissAlert(alert.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-700/50 rounded transition-all duration-200"
                    aria-label="Dismiss alert"
                  >
                    <X className="w-4 h-4 text-slate-400 hover:text-white" />
                  </button>
                </div>
              </div>
            ))}
            {visibleAlerts.length === 0 && (
              <div className="text-center py-8 text-slate-500">
                <AlertCircle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No active alerts</p>
              </div>
            )}
          </div>
        </div>

        <div className="flex space-x-2 mb-6 overflow-x-auto pb-2 scrollbar-hide">
          {tabs.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-300 whitespace-nowrap relative overflow-hidden group ${
                  isActive
                    ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/50 hover:shadow-xl hover:shadow-blue-500/60 scale-105 ml-[10px]'
                    : 'bg-slate-800/50 text-slate-400 hover:bg-slate-700/50 hover:text-slate-300 hover:scale-105'
                }`}
              >
                <span className={`bg-gradient-to-r from-blue-600/20 to-purple-600/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${isActive ? 'opacity-100' : ''}`} />
                <Icon className={`w-5 h-5 relative z-10 transition-transform duration-300 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`} />
                <span className="relative z-10">{tab.label}</span>
                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-400 to-purple-400 animate-pulse" />
                )}
              </button>
            );
          })}
        </div>

        <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-700/30 rounded-2xl p-6 hover:border-slate-600/30 transition-all duration-300">
          <div className="animate-in fade-in duration-500">
            {activeTab === 'delays' && renderDelaysTab()}
            {activeTab === 'passengers' && renderPassengersTab()}
            {activeTab === 'cargo' && renderCargoTab()}
            {activeTab === 'weather' && (
              <div className="text-center py-12 animate-in fade-in zoom-in duration-500">
                <Cloud className="w-16 h-16 text-slate-600 mx-auto mb-4 animate-pulse" />
                <p className="text-slate-400">Weather module coming soon</p>
              </div>
            )}
            {activeTab === 'traffic' && (
              <div className="text-center py-12 animate-in fade-in zoom-in duration-500">
                <TrendingUp className="w-16 h-16 text-slate-600 mx-auto mb-4 animate-pulse" />
                <p className="text-slate-400">Traffic analytics coming soon</p>
              </div>
            )}
          </div>
        </div>
      </div>
      </div>
    </Layout>
  );
};

export default FlightOpsDashboard;

