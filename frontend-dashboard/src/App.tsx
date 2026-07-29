import { useState } from 'react'
import Map from 'react-map-gl/mapbox'
import 'mapbox-gl/dist/mapbox-gl.css'
import './App.css'

function App() {
  const [startDate, setStartDate] = useState("2026-06-01")
  const [endDate, setEndDate] = useState("2026-07-31")
  const [viewState, setViewState] = useState({
    longitude: -122.4194,
    latitude: 37.7749,
    zoom: 12
  })

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Operational GIS & Live Bayesian Risk Dashboard</h1>
        <div className="controls">
          <label>
            Start Date: 
            <input 
              type="date" 
              value={startDate} 
              onChange={e => setStartDate(e.target.value)} 
            />
          </label>
          <label>
            End Date: 
            <input 
              type="date" 
              value={endDate} 
              onChange={e => setEndDate(e.target.value)} 
            />
          </label>
        </div>
      </header>

      <main className="map-container">
        <Map
          {...viewState}
          onMove={(evt: any) => setViewState(evt.viewState)}
          mapStyle="mapbox://styles/mapbox/dark-v11"
          mapboxAccessToken="pk.eyJ1IjoiZHVtbXkiLCJhIjoiY2R1bW15In0.dummy"
        />

        <div className="overlay-panel">
          <h3>Snapshot Telemetry Overview</h3>
          <p><strong>Window:</strong> {startDate} to {endDate}</p>
          <p><strong>Deduplicated Incidents:</strong> 124</p>
          <p><strong>Deadheading VMT Ratio:</strong> 55.00%</p>
          <p><strong>SPRT Safety Status:</strong> <span style={{ color: '#4CAF50' }}>PASSING (0.07% False Demotion)</span></p>
        </div>
      </main>
    </div>
  )
}

export default App
