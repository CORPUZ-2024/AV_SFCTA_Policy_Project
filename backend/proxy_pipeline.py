import pandas as pd
import numpy as np
import datetime

def execute_proxy_1_deadheading(vmt_data, weights):
    """
    4.1 Proxy 1: Stratified Spatial Sampling for Deadheading VMT
    R_deadhead_z = ( VMT_Total_Observed_z - VMT_Passenger_Serviced_z ) / VMT_Total_Observed_z
    Returns weighted overall ratio.
    """
    print("Executing Proxy 1: Calculating Deadheading Ratio...")
    if vmt_data.empty:
        return 0.0
        
    vmt_data['R_deadhead_z'] = (vmt_data['vmt_total'] - vmt_data['vmt_passenger']) / vmt_data['vmt_total']
    
    # Weighted average over strata Z (e.g., CBD, Arterials, Hubs)
    vmt_data['weighted_R'] = vmt_data['R_deadhead_z'] * vmt_data['strata_weight']
    
    snapshot_ratio = vmt_data['weighted_R'].sum()
    print(f"Overall Snapshot Deadheading Ratio: {snapshot_ratio:.2%}")
    return snapshot_ratio

def execute_proxy_2_delay_control(incidents_df, gtfs_actual_df, gtfs_baseline_df):
    """
    4.2 Proxy 2: Spatio-Temporal Buffer & Counterfactual Control
    Delay_AV_Net = [ t_actual(t_incident) - t_baseline(...) ]
    """
    print("Executing Proxy 2: Calculating Net Causal Transit Delay...")
    if incidents_df.empty or gtfs_actual_df.empty:
        return pd.DataFrame()
        
    # In a full implementation, we'd do a spatial merge (within 50m) and temporal match (+/- 15m)
    # Here we mock the merged result for demonstration
    merged_delays = incidents_df.copy()
    
    # Randomly assign delays as a mock mechanism
    merged_delays['t_actual'] = np.random.uniform(15, 45, len(merged_delays))
    merged_delays['t_baseline'] = merged_delays['t_actual'] - np.random.uniform(2, 15, len(merged_delays))
    
    # The core equation: Delay_AV_Net
    merged_delays['Delay_AV_Net'] = merged_delays['t_actual'] - merged_delays['t_baseline']
    
    avg_delay = merged_delays['Delay_AV_Net'].mean()
    print(f"Calculated average net causal delay of {avg_delay:.2f} minutes per incident.")
    return merged_delays

if __name__ == "__main__":
    # Mock execution for Phase 2
    mock_vmt = pd.DataFrame({
        'strata': ['CBD', 'Arterial', 'Hub'],
        'vmt_total': [50000, 30000, 20000],
        'vmt_passenger': [25000, 18000, 2000],
        'strata_weight': [0.5, 0.3, 0.2]
    })
    
    execute_proxy_1_deadheading(mock_vmt, None)
    
    mock_incidents = pd.DataFrame({'incident_id': [1, 2, 3]})
    execute_proxy_2_delay_control(mock_incidents, pd.DataFrame(), pd.DataFrame())
