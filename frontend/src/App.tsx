import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { Header } from './components/Header'
import CargoAnalytics from './pages/CargoAnalytics'
import CargoAnalyticsDashboard from './pages/CargoAnalyticsDashboard'
import { Dashboard } from './pages/Dashboard'
import FlightOpsDashboard from './pages/FlightOpsDashboard'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/flight-ops" element={<FlightOpsDashboard />} />
        <Route path="/cargo-analytics" element={
          <div className="App">
            <Sidebar />
            <div className="main-content">
              <Header />
              <main className="main-body">
                <CargoAnalyticsDashboard />
              </main>
            </div>
          </div>
        } />
        <Route path="/cargo-analytics/:flightId" element={
          <div className="App">
            <Sidebar />
            <div className="main-content">
              <Header />
              <main className="main-body">
                <CargoAnalytics />
              </main>
            </div>
          </div>
        } />
        <Route path="/cargo-analytics/flight/:flightNumber" element={
          <div className="App">
            <Sidebar />
            <div className="main-content">
              <Header />
              <main className="main-body">
                <CargoAnalytics />
              </main>
            </div>
          </div>
        } />
      </Routes>
    </Router>
  )
}

export default App
