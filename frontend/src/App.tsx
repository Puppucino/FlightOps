import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Flight Delay Prediction Dashboard</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<div>Dashboard - Coming Soon</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

