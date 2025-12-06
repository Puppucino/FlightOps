import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { Header } from './components/Header'
import CargoAnalytics from './pages/CargoAnalytics'
import CargoAnalyticsDashboard from './pages/CargoAnalyticsDashboard'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Sidebar />
        <div className="main-content">
          <Header />
          <main className="main-body">
            <Routes>
              <Route path="/" element={<CargoAnalyticsDashboard />} />
              <Route path="/cargo-analytics" element={<CargoAnalyticsDashboard />} />
              <Route path="/cargo-analytics/:flightId" element={<CargoAnalytics />} />
              <Route path="/cargo-analytics/flight/:flightNumber" element={<CargoAnalytics />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App

