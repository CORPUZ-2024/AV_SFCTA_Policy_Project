# AV SFCTA Policy Project

## Project Goal
This project establishes an empirical, policy-aligned analytical pipeline to evaluate the network-level impacts of Autonomous Vehicles (AVs) on San Francisco's transportation grid. It extends existing SFCTA modeling tools (SF-CHAMP and Dynamic Traffic Assignment) to measure true modal shift, transit cannibalization, "deadheading" VMT, and emergency responder operational risks.

## Scope
The evaluation focuses on date-bounded snapshot analyses using parametric temporal windowing. It encompasses:
- **Data Ingestion**: Direct integration with DataSF SODA, NHTSA REST APIs, and 511.org GTFS-RT feeds for a specific time window.
- **Analytical Engine**: Advanced microeconomic models including Upper-Level Nested Logit Logsum linkage, non-linear Highway Capacity Manual incident drop curves, and Sequential Probability Ratio Test (SPRT) safety engines.
- **Visual Dashboards**: Two primary frontends:
  - An Operational GIS & Live Bayesian Risk Dashboard built with React, Mapbox GL JS, and Deck.gl.
  - An Executive Policy Trade-Off Engine built with Streamlit and Plotly for high-level scenario modeling.

## Approach
The architecture is structured into the following components:
1. **Backend ETL & Analytics (`backend/`)**: Python scripts handling data ingestion, ETL cleaning, QA validation gates, and the core causal proxy and econometric logic. It utilizes PostgreSQL/PostGIS for robust spatial analysis.
2. **Operational Dashboard (`frontend-dashboard/`)**: A Vite-based React application providing live spatial monitoring of incident clusters and transit delays.
3. **Executive Engine (`executive-engine/`)**: A Streamlit application offering a clean interface for policy makers to simulate deadheading taxes and Pick-up/Drop-off (PUDO) mandates.

## Implementation Directions

### 1. Backend Pipeline
Ensure you have `python` installed.
```bash
cd backend
pip install -r requirements.txt
python ingestion.py --start-date 2026-06-01 --end-date 2026-07-31
python proxy_pipeline.py
python analytics_engine.py
python qa_gates.py
```

### 2. Operational GIS Dashboard (React)
Ensure you have `Node.js` installed.
```bash
cd frontend-dashboard
npm install
npm run dev
```

### 3. Executive Policy Trade-Off Engine (Streamlit)
```bash
cd executive-engine
pip install -r requirements.txt
streamlit run app.py
```

### 4. Database Setup
A `docker-compose.yml` file is provided to quickly spin up a local PostGIS database for data staging.
```bash
docker-compose up -d
```
