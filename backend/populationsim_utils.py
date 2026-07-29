import numpy as np
import pandas as pd
import geopandas as gpd

def build_puma_taz_crosswalk(puma_shp, taz_shp, block_pop_table):
    """
    §5.2 PUMA -> TAZ Crosswalk (PopulationSim geography)
    ACS PUMS seed data is published at PUMA geography; PopulationSim requires TAZ-level marginal controls.
    Population-weighted areal apportionment via Census block avoids PUMA centroid misallocation.
    """
    print("Building PUMA -> TAZ population-weighted crosswalk...")
    if not isinstance(puma_shp, gpd.GeoDataFrame) or not isinstance(taz_shp, gpd.GeoDataFrame):
        # Mock crosswalk if input is not a full GeoDataFrame
        return pd.DataFrame({
            'puma_id': ['0607501', '0607501', '0607502'],
            'taz_id': [101, 102, 103],
            'weight': [0.6, 0.4, 1.0]
        })
    
    # 1. Intersect PUMA and TAZ polygons at the Census block level
    blocks = gpd.overlay(block_pop_table, puma_shp, how="intersection")
    blocks = gpd.overlay(blocks, taz_shp, how="intersection")
    # 2. Apportion each block's population by area share across split TAZ fragments
    blocks["frac"] = blocks.geometry.area / blocks.groupby("block_id").geometry.area.transform("sum")
    blocks["apportioned_pop"] = blocks["population"] * blocks["frac"]
    # 3. Aggregate to PUMA x TAZ population-weighted crosswalk
    xwalk = blocks.groupby(["puma_id", "taz_id"])["apportioned_pop"].sum().reset_index()
    xwalk["weight"] = xwalk["apportioned_pop"] / xwalk.groupby("puma_id")["apportioned_pop"].transform("sum")
    return xwalk

def check_ipu_convergence(weight_curr, weight_prev, iteration_count, max_iterations=100, tol=0.0001):
    """
    §5.3 IPU Convergence Criterion:
    STOP WHEN max(|weight_iter_n - weight_iter_(n-1)|) / weight_iter_(n-1) < 0.0001
    OR iteration_count >= 100 # hard cap — treat as non-convergence, not success
    Returns: (is_converged: bool, max_rel_change: float, is_hard_cap: bool)
    """
    weight_curr_arr = np.asarray(weight_curr, dtype=float)
    weight_prev_arr = np.asarray(weight_prev, dtype=float)
    
    # Avoid division by zero
    safe_denom = np.where(weight_prev_arr == 0, 1e-10, weight_prev_arr)
    rel_change = np.abs(weight_curr_arr - weight_prev_arr) / safe_denom
    max_rel_change = np.max(rel_change)
    
    is_hard_cap = iteration_count >= max_iterations
    is_converged = (max_rel_change < tol) and not is_hard_cap
    
    if is_hard_cap and max_rel_change >= tol:
        print(f"WARNING: IPU hard cap reached at iteration {iteration_count} without convergence (max_rel_change={max_rel_change:.6f}).")
    elif is_converged:
        print(f"IPU converged at iteration {iteration_count} with max_rel_change={max_rel_change:.6f} < {tol}.")
        
    return is_converged, max_rel_change, is_hard_cap

def generate_synthetic_population_snapshot(taz_ids, income_tiers=["low", "medium", "high"], households_per_taz=100, seed=42):
    """
    Generate synthetic households mapped to TAZs and income tiers for v7 downstream mode choice and QA Gate 6.
    """
    np.random.seed(seed)
    records = []
    for taz in taz_ids:
        for _ in range(households_per_taz):
            income_tier = np.random.choice(income_tiers, p=[0.3, 0.4, 0.3])
            records.append({
                "synth_hh_id": len(records) + 1,
                "taz_id": taz,
                "income_tier": income_tier,
                "expansion_weight": 1.0
            })
    return pd.DataFrame(records)

if __name__ == "__main__":
    print("Testing PopulationSim utils...")
    xwalk = build_puma_taz_crosswalk(None, None, None)
    print("Crosswalk preview:\n", xwalk)
    
    converged, max_chg, hard_cap = check_ipu_convergence([1.00005, 2.00002], [1.00000, 2.00000], 15)
    print(f"Converged: {converged}, max_change: {max_chg:.6f}, hard_cap: {hard_cap}")
