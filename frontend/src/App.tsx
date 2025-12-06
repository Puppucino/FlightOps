import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import { Layout } from './components/Layout'
import CargoAnalytics from './pages/CargoAnalytics'
import CargoAnalyticsDashboard from './pages/CargoAnalyticsDashboard'
import { Dashboard } from './pages/Dashboard'
import FlightOpsDashboard from './pages/FlightOpsDashboard'
import './App.css'

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/flight-ops" element={<FlightOpsDashboard />} />
          <Route path="/cargo-analytics" element={
            <Layout>
              <CargoAnalyticsDashboard />
            </Layout>
          } />
          <Route path="/cargo-analytics/:flightId" element={
            <Layout showBackButton>
              <CargoAnalytics />
            </Layout>
          } />
          <Route path="/cargo-analytics/flight/:flightNumber" element={
            <Layout showBackButton>
              <CargoAnalytics />
            </Layout>
          } />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App
