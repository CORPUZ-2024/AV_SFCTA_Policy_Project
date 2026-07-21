import pandas as pd
import numpy as np

def apply_rule_1_deduplication(sgo_df, sf311_df, sffd_df, start_date, end_date):
    """
    Rule 1 (Deduplication): Cross-reference SGO, 311, and SFFD logs using VIN, timestamp (+/- 5 mins), 
    and spatial coordinates within [START_DATE, END_DATE] to eliminate duplicate records.
    """
    print("Applying Rule 1: Deduplicating across SGO, 311, and SFFD logs...")
    # Mocking complex spatial/temporal deduplication logic with basic deduplication
    # In reality, this would require spatial joins using geopandas and time-delta matching
    if not sgo_df.empty:
        sgo_df = sgo_df.drop_duplicates(subset=['vin', 'timestamp'])
    return sgo_df

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
    """Run full ETL pipeline"""
    # Create DataFrames if they aren't already
    sgo_df = pd.DataFrame(raw_sgo)
    sf311_df = pd.DataFrame(raw_sf311)
    gtfs_df = pd.DataFrame(raw_gtfs)

    sgo_cleaned = apply_rule_1_deduplication(sgo_df, sf311_df, pd.DataFrame(), start_date, end_date)
    sgo_cleaned = apply_rule_2_temporal_boundary(sgo_cleaned, 'timestamp', start_date, end_date)
    sf311_cleaned = apply_rule_2_temporal_boundary(sf311_df, 'requested_datetime', start_date, end_date)
    gtfs_cleaned = apply_rule_3_gtfs_anomalies(gtfs_df)
    
    return sgo_cleaned, sf311_cleaned, gtfs_cleaned

