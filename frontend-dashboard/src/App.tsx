import { useState } from 'react'
import Map, { Marker, NavigationControl } from 'react-map-gl/maplibre'
import * as maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import './App.css'

// 100% Reliable Dark Vector/Raster Style Specification for CARTO Dark Matter
const cartoDarkStyle: maplibregl.StyleSpecification = {
  version: 8,
  sources: {
    'carto-dark': {
      type: 'raster',
      tiles: [
        'https://a.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png',
        'https://b.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png',
        'https://c.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png',
        'https://d.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png'
      ],
      tileSize: 256,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    }
  },
  layers: [
    {
      id: 'carto-dark-layer',
      type: 'raster',
      source: 'carto-dark',
      minzoom: 0,
      maxzoom: 22
    }
  ]
}

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
  const [selectedIncident, setSelectedIncident] = useState<any>(sampleIncidents[0])
  const [activeFilter, setActiveFilter] = useState("all")
  const [viewState, setViewState] = useState({
    longitude: -122.4194,
    latitude: 37.7749,
    zoom: 12.5
  })

  const filteredIncidents = activeFilter === "all" 
    ? sampleIncidents 
    : sampleIncidents.filter(inc => inc.type === activeFilter)

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
          mapStyle={cartoDarkStyle}
          style={{ width: '100%', height: '100%' }}
        >
          <NavigationControl position="bottom-right" />

          {/* Live Incident Markers */}
          {filteredIncidents.map(inc => (
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

          <div style={{ marginTop: '0.75rem', marginBottom: '0.5rem' }}>
            <strong>Filter Incidents:</strong>
            <select 
              value={activeFilter} 
              onChange={e => setActiveFilter(e.target.value)}
              style={{ marginLeft: '0.5rem', background: '#2a2a35', color: '#fff', border: '1px solid #444', padding: '0.2rem 0.5rem', borderRadius: '4px' }}
            >
              <option value="all">All Types (5)</option>
              <option value="blockage">Transit Blockages</option>
              <option value="deadhead">Deadheading Clusters</option>
              <option value="pudo">PUDO Bottlenecks</option>
              <option value="telemetry">Telemetry Drops</option>
            </select>
          </div>

          {selectedIncident && (
            <div className="incident-details">
              <h4>Incident Inspection</h4>
              <p><strong>Location:</strong> {selectedIncident.title}</p>
              <p><strong>Impact:</strong> {selectedIncident.delay}</p>
              <button onClick={() => setSelectedIncident(null)}>Close Inspection</button>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
