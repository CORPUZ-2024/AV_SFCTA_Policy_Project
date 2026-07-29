# AV SFCTA Policy Project (Version 7.0)

## Project Goal
This project implements an empirical, policy-aligned analytical pipeline to evaluate the network-level impacts of Autonomous Vehicles (AVs) on San Francisco's transportation grid. It extends existing SFCTA modeling tools (SF-CHAMP and Dynamic Traffic Assignment) to measure true modal shift, transit cannibalization, "deadheading" VMT, income-segmented equity dynamics, and emergency responder operational risks.

## Scope & Version 7.0 Enhancements
The exploration focuses on date-bounded snapshot analyses using parametric temporal windowing (`START_DATE` to `END_DATE`). Version 7.0 introduces key engineering upgrades:
- **PopulationSim (ActivitySim) Integration**: Synthesizes TAZ-level household demographics from Census ACS PUMS seed microdata using Iterative Proportional Updating (IPU) and Census block-level population-weighted areal apportionment.
- **Rule 4 Spatial/CRS Harmonization**: Mandatory transformation of all ingested API data to `EPSG:26910` (NAD83 UTM Zone 10N) prior to metric spatial joins (Rule 1 deduplication and Rule 3 GTFS jump filtering).
- **6-Gate QA Gateway Suite**: Rigorous validation matrix return tuples across all 6 QA Gates, including new **QA Gate 6 (Demographic Marginal Validation)** enforcing `MAPE <= 1.0%` for cells with `>= 30` households.
- **Income-Segmented Econometric Engine**: Upper-Level Nested Logit choice tree incorporating PopulationSim `Income_Group` categorical variables and disaggregated Value of Travel Time Savings (`VOT_k = b_ivtt_k / b_fare_k`).
- **Interactive Executive Streamlit Engine**: Dynamic corridor deadheading cost modeling, disaggregated population equity mode shift matrices, styled dark-mode tables with aligned container heights, and grouped bar chart visualizations.
- **MapLibre GL Operational Dashboard**: High-performance dark vector/raster GIS monitoring with animated incident pins, pulse effects, and live filter controls.

## Architecture & Components
1. **Backend Pipeline (`backend/`)**:
   - `ingestion.py`: Parametric temporal API ingestion stack.
   - `cleaning.py`: 4-Rule ETL pipeline (Rule 4 CRS Harmonization -> Rule 1 Composite Key Deduplication -> Rule 2 Boundary Enforcement -> Rule 3 GTFS Anomaly Cleaning).
   - `populationsim_utils.py`: Population-weighted PUMA-to-TAZ crosswalk builder and IPU convergence checker (`tol < 0.0001` or 100-iter cap).
   - `qa_gates.py`: Full 6-Gate QA Gateway Suite returning `(passed, statistic)` tuples.
   - `proxy_pipeline.py`: Causal Proxy 1 (Deadheading VMT ratio) and Proxy 2 (Net Causal Transit Delay).
   - `analytics_engine.py`: Nested Logit logsum linkage, Income-Segmented VOT, non-linear HCM capacity drops, and DTA feedback loop.
2. **Operational Dashboard (`frontend-dashboard/`)**: A React + MapLibre GL application providing live spatial monitoring of incident clusters, transit delays, and interactive filter controls.
3. **Executive Engine (`executive-engine/`)**: A Streamlit application offering interactive policy controls to simulate deadheading taxes ($/mi) and Pick-up/Drop-off (PUDO) mandates with real-time corridor cost tables and disaggregated population mode choice matrices.

## Implementation Directions & Demonstration Videos

### 1. Backend Pipeline Execution
Ensure Python 3.9+ is installed.
```bash
cd backend
pip install -r requirements.txt

# Run Data Ingestion Stack
python ingestion.py --start-date 2026-06-01 --end-date 2026-07-31

# Run PopulationSim & IPU Utilities
python populationsim_utils.py

# Run Causal Proxy Engine
python proxy_pipeline.py

# Run Econometric & DTA Simulation Engine
python analytics_engine.py

# Execute Full 6-Gate QA Gateway Suite
python qa_gates.py
```

### 2. Operational GIS Dashboard (React + MapLibre)
```bash
cd frontend-dashboard
npm install
npm run dev
```

#### 🎥 Operational GIS Dashboard Demonstration
<video src="assets/demo_videos/MapLibre_GL_Operational_Dashboard.mp4" controls="controls" muted="muted" style="max-width: 100%; height: auto;">
  Your browser does not support the video tag.
</video>

### 3. Executive Policy Trade-Off Engine (Streamlit)
```bash
py -m pip install -r executive-engine/requirements.txt
py -m streamlit run executive-engine/app.py
```

#### 🎥 Executive Policy Engine Demonstration
<video src="assets/demo_videos/Policy_Engine_Dashboard.mp4" controls="controls" muted="muted" style="max-width: 100%; height: auto;">
  Your browser does not support the video tag.
</video>

### 4. Database Setup
A `docker-compose.yml` file is provided to spin up a local PostGIS database for spatial data staging.
```bash
docker-compose up -d
```
