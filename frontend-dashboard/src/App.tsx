import { useState } from 'react'
import Map, { Marker, NavigationControl } from 'react-map-gl/maplibre'
import * as maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import './App.css'

// Sample SF AV Incidents & Deadheading Telemetry Clusters
const sampleIncidents = [
  { id: 1, lat: 37.7892, lng: -122.4014, title: 'Market St & 3rd St - In-lane AV Blockage', delay: '14 min transit delay', type: 'blockage' },
  { id: 2, lat: 37.7825, lng: -122.4082, title: 'Mission St & 5th St - Deadheading Cluster', delay: 'High VMT density', type: 'deadhead' },
  { id: 3, lat: 37.7841, lng: -122.4186, title: 'Geary Blvd & Van Ness Ave - Muni Bus Interaction', delay: '8 min bus delay', type: 'blockage' },
  { id: 4, lat: 37.7695, lng: -122.4468, title: 'Haight St & Ashbury St - Telemetry Signal Drop', delay: 'Resolved', type: 'telemetry' },
  { id: 5, lat: 37.7952, lng: -122.3934, title: 'Embarcadero & Ferry Building - PUDO Bottleneck', delay: '6 min delay', type: 'pudo' }
]

function App() {
  const [startDate, setStartDate] = useState("2026-06-01")
  const [endDate, setEndDate] = useState("2026-07-31")
  const [selectedIncident, setSelectedIncident] = useState<any>(null)
  const [viewState, setViewState] = useState({
    longitude: -122.4194,
    latitude: 37.7749,
    zoom: 13
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
          mapLib={maplibregl as any}
          mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
          style={{ width: '100%', height: '100%' }}
        >
          <NavigationControl position="bottom-right" />

          {/* Live Incident Markers */}
          {sampleIncidents.map(inc => (
            <Marker
              key={inc.id}
              latitude={inc.lat}
              longitude={inc.lng}
              onClick={e => {
                e.originalEvent.stopPropagation()
                setSelectedIncident(inc)
              }}
            >
              <div 
                className={`marker-pin ${inc.type}`}
                title={inc.title}
              >
                <div className="marker-pulse"></div>
              </div>
            </Marker>
          ))}
        </Map>

        {/* Floating Telemetry & Risk Overview Panel */}
        <div className="overlay-panel">
          <h3>Snapshot Telemetry Overview</h3>
          <p><strong>Window:</strong> {startDate} to {endDate}</p>
          <p><strong>Deduplicated Incidents:</strong> 124 episodes</p>
          <p><strong>Deadheading VMT Ratio:</strong> 55.00%</p>
          <p><strong>SPRT Safety Status:</strong> <span style={{ color: '#4CAF50', fontWeight: 'bold' }}>PASSING (0.07% False Demotion)</span></p>

          {selectedIncident && (
            <div className="incident-details">
              <h4>Incident Inspection</h4>
              <p><strong>Location:</strong> {selectedIncident.title}</p>
              <p><strong>Impact:</strong> {selectedIncident.delay}</p>
              <button onClick={() => setSelectedIncident(null)}>Close</button>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
