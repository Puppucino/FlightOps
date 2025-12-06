import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import FlightOpsDashboard from './pages/FlightOpsDashboard'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<FlightOpsDashboard />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App

