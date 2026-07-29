import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

def apply_rule_4_crs_harmonization(gdf, target_crs="EPSG:26910"):
    """
    Rule 4 (Spatial/CRS Harmonization):
    All ingested API data arrives in mixed or absent coordinate reference systems.
    Convert to NAD83 UTM Zone 10N (EPSG:26910) before any metric spatial join in Rules 1 and 3.
    """
    print(f"Applying Rule 4: CRS Harmonization to target CRS {target_crs}...")
    if not isinstance(gdf, gpd.GeoDataFrame) or gdf.empty:
        return gdf
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")  # assume WGS84 for unlabeled API output
    return gdf.to_crs(target_crs)  # NAD83 UTM Zone 10N — metric distances required

def _union_find_episodes(dupes_df):
    """
    Helper for Rule 1: Connected components across duplicate pairs -> Episode_ID
    """
    parent = {}
    def find(x):
        if parent.setdefault(x, x) != x:
            parent[x] = find(parent[x])
        return parent[x]
    def union(x, y):
        root_x, root_y = find(x), find(y)
        if root_x != root_y:
            parent[root_x] = root_y

    for idx, row in dupes_df.iterrows():
        union(idx, row.get('index_b', idx))
    return {k: find(k) for k in parent}

def apply_rule_1_deduplication(sgo_gdf, time_tol_min=5, spatial_tol_m=50):
    """
    Rule 1 (Deduplication): Cross-reference SGO, 311, and SFFD logs using VIN, timestamp (+/- 5 mins), 
    and spatial coordinates (50m buffer) to collapse overlapping reports into deterministic Episode_ID.
    """
    print(f"Applying Rule 1: Deduplicating logs with ±{time_tol_min} min and {spatial_tol_m} m composite key...")
    if sgo_gdf.empty:
        return sgo_gdf
    
    # Ensure timestamp is datetime
    if 'timestamp' in sgo_gdf.columns:
        sgo_gdf['timestamp'] = pd.to_datetime(sgo_gdf['timestamp'])
        sgo_gdf = sgo_gdf.sort_values("timestamp")
    
    if isinstance(sgo_gdf, gpd.GeoDataFrame) and 'geometry' in sgo_gdf.columns and 'vin' in sgo_gdf.columns and len(sgo_gdf) > 1:
        # Per v7 Implementation Spec §4.1
        sgo_gdf["geometry_buf"] = sgo_gdf.geometry.buffer(spatial_tol_m)
        candidates = gpd.sjoin(sgo_gdf.set_geometry("geometry_buf"), sgo_gdf,
                               predicate="intersects", lsuffix="a", rsuffix="b")
        same_vin = candidates["vin_a"] == candidates["vin_b"]
        near_time = (candidates["timestamp_a"] - candidates["timestamp_b"]).abs() <= pd.Timedelta(minutes=time_tol_min)
        dupes = candidates[same_vin & near_time]
        episode_map = _union_find_episodes(dupes)
        sgo_gdf["episode_id"] = sgo_gdf.index.map(lambda x: episode_map.get(x, f"ep_{x}"))
        sgo_gdf = sgo_gdf.set_geometry("geometry")
        return sgo_gdf.sort_values("timestamp").drop_duplicates("episode_id", keep="first")
    elif 'vin' in sgo_gdf.columns and 'timestamp' in sgo_gdf.columns:
        # Fallback deduplication if not a full GeoDataFrame with geometries
        sgo_gdf["episode_id"] = sgo_gdf.index.map(lambda x: f"ep_{x}")
        return sgo_gdf.drop_duplicates(subset=['vin', 'timestamp'])
    return sgo_gdf

def apply_rule_2_temporal_boundary(df, timestamp_col, start_date, end_date):
    """
    Rule 2 (Spatial & Temporal Boundary Enforcement): Discard records with timestamps < START_DATE 
    or > END_DATE, or occurring outside SF County boundaries.
    """
    print(f"Applying Rule 2: Enforcing temporal boundaries [{start_date}, {end_date}]...")
    if df.empty or timestamp_col not in df.columns:
        return df
    
    # Ensure datetime format
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date + " 23:59:59")
    
    filtered_df = df[(df[timestamp_col] >= start_dt) & (df[timestamp_col] <= end_dt)]
    print(f"Filtered {len(df) - len(filtered_df)} records outside temporal bounds.")
    return filtered_df

def apply_rule_3_gtfs_anomalies(gtfs_df):
    """
    Rule 3 (GTFS Anomaly Cleaning): Filter out bus GPS telemetry jump anomalies (speeds > 65 mph or distance jumps > 500m/sec).
    """
    print("Applying Rule 3: Cleaning GTFS anomalies...")
    if gtfs_df.empty or 'speed_mph' not in gtfs_df.columns:
        return gtfs_df
    
    original_len = len(gtfs_df)
    gtfs_df = gtfs_df[gtfs_df['speed_mph'] <= 65.0]
    
    if 'distance_jump_m_per_sec' in gtfs_df.columns:
        gtfs_df = gtfs_df[gtfs_df['distance_jump_m_per_sec'] <= 500.0]
        
    print(f"Removed {original_len - len(gtfs_df)} GTFS anomalous records.")
    return gtfs_df

def run_etl_pipeline(raw_sgo, raw_sf311, raw_gtfs, start_date, end_date):
    """
    Run full ETL pipeline enforcing v7 ordering:
    Rule 4 (CRS Harmonization) -> Rule 1 (Deduplication) -> Rule 2 (Boundary) -> Rule 3 (GTFS Anomalies)
    """
    sgo_df = pd.DataFrame(raw_sgo)
    sf311_df = pd.DataFrame(raw_sf311)
    gtfs_df = pd.DataFrame(raw_gtfs)

    # Step 1: Rule 4 CRS Harmonization (before Rules 1 and 3)
    sgo_gdf = apply_rule_4_crs_harmonization(sgo_df)
    sf311_gdf = apply_rule_4_crs_harmonization(sf311_df)

    # Step 2: Rule 1 Deduplication (uses metric UTM Zone 10N buffer)
    sgo_cleaned = apply_rule_1_deduplication(sgo_gdf, time_tol_min=5, spatial_tol_m=50)

    # Step 3: Rule 2 Temporal & Spatial Boundary Enforcement
    sgo_cleaned = apply_rule_2_temporal_boundary(sgo_cleaned, 'timestamp', start_date, end_date)
    sf311_cleaned = apply_rule_2_temporal_boundary(sf311_gdf, 'requested_datetime', start_date, end_date)

    # Step 4: Rule 3 GTFS Anomaly Cleaning
    gtfs_cleaned = apply_rule_3_gtfs_anomalies(gtfs_df)
    
    return sgo_cleaned, sf311_cleaned, gtfs_cleaned


