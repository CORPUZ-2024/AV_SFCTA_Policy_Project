import math

def calculate_nested_logit_utilities(fare_av, fare_h, ivtt_av, ivtt_h, ovtt, comfort_discount):
    """
    A. Lower-Level For-Hire Nest Systematic Utility Equations
    V_TNC_AV = b_0_AV + b_fare * Fare_AV + b_ivtt_AV * IVTT + b_ovtt * OVTT + b_comfort * Comfort_Discount
    V_TNC_H  = b_0_H  + b_fare * Fare_H  + b_ivtt_H  * IVTT + b_ovtt * OVTT
    """
    # Dummy coefficients
    b_0_AV = 1.0
    b_0_H = 0.5
    b_fare = -0.1
    b_ivtt_AV = -0.05
    b_ivtt_H = -0.08
    b_ovtt = -0.15
    b_comfort = 0.5
    
    v_tnc_av = b_0_AV + (b_fare * fare_av) + (b_ivtt_AV * ivtt_av) + (b_ovtt * ovtt) + (b_comfort * comfort_discount)
    v_tnc_h = b_0_H + (b_fare * fare_h) + (b_ivtt_H * ivtt_h) + (b_ovtt * ovtt)
    
    return v_tnc_av, v_tnc_h

def calculate_inclusive_value(v_tnc_av, v_tnc_h, mu_fh=0.5):
    """
    B. Inclusive Value (Logsum) of For-Hire Nest
    I_FH = ln[ exp(V_TNC_AV / mu_FH) + exp(V_TNC_H / mu_FH) ]
    """
    i_fh = math.log(math.exp(v_tnc_av / mu_fh) + math.exp(v_tnc_h / mu_fh))
    return i_fh

def bayesian_sprt_update(alpha_0, beta_0, k_snapshot, vmt_snapshot):
    """
    5.2 Sequential Probability Ratio Test (SPRT) & Bayesian Reversion Engine
    Posterior Update Distribution Equation:
    theta | Snapshot ~ Gamma(alpha_0 + K_snapshot, beta_0 + VMT_snapshot)
    """
    alpha_post = alpha_0 + k_snapshot
    beta_post = beta_0 + vmt_snapshot
    return alpha_post, beta_post

def non_linear_hcm_capacity_drop(c_base, n_blocked, n_total, f_rubberneck):
    """
    3.3 Non-Linear HCM Incident Capacity Drop
    C_effective = C_base * [ 1 - ( 1.1 * (N_blocked / N_total)^0.8 + F_rubberneck ) ]
    """
    c_effective = c_base * (1 - (1.1 * ((n_blocked / n_total)**0.8) + f_rubberneck))
    return max(0, c_effective)

def calculate_income_segmented_vot(b_ivtt_k, b_fare_k):
    """
    §7.2 Income-Segmented VOT:
    VOT_k = b_ivtt_k / b_fare_k # $/hour, computed per income segment k
    Requires binning PopulationSim's continuous household income into k tiers.
    """
    if b_fare_k == 0:
        return 0.0
    vot_k = (b_ivtt_k / b_fare_k) * 60.0  # Convert $/minute to $/hour
    return vot_k

def calculate_upper_level_tour_mode_utility(i_fh, mu_fh, income_tier="medium", b_income_dict=None):
    """
    §3.1 / §7.1 Upper-Level Tour-Mode Choice Tree (Transit vs. Drive vs. Walk vs. For-Hire):
    V_FH_Composite = mu_FH * I_FH + b_income_segment * Income_Group
    """
    if b_income_dict is None:
        b_income_dict = {"low": -0.5, "medium": 0.0, "high": 0.8}
    b_income = b_income_dict.get(income_tier, 0.0)
    v_fh_composite = (mu_fh * i_fh) + b_income
    return v_fh_composite

def run_dta_sfchamp_feedback_loop(c_base, n_blocked, n_total, f_rubberneck, max_iterations=10):
    """
    3.3 Iterative DTA Feedback Loop
    Demand-Supply Feedback Equilibration Convergence Equation:
    RMSE_skim = sqrt[ (1 / N_links) * SUM_{i=1}^{N_links} ( Skim_Time_DTA_{i, m} - Skim_Time_SFCHAMP_{i, m-1} )^2 ]
    """
    print("Initializing DTA <-> SF-CHAMP Equilibration Loop...")
    
    # Calculate effective capacity due to AV blockages
    c_effective = non_linear_hcm_capacity_drop(c_base, n_blocked, n_total, f_rubberneck)
    print(f"Non-Linear HCM Effective Capacity: {c_effective:.2f} veh/hr/lane")
    
    # Mocking skim convergence
    rmse_skim = 1.0
    iteration = 1
    
    while rmse_skim > 0.01 and iteration <= max_iterations:
        # Simulate skim updating
        rmse_skim *= 0.5  # Artificial convergence
        print(f"Iteration {iteration}: RMSE_skim = {rmse_skim:.4f}")
        
        if rmse_skim < 0.01:
            print(f"Equilibrium reached at iteration {iteration} (RMSE < 0.01).")
            break
        iteration += 1
        
    return rmse_skim

if __name__ == "__main__":
    print("=== Executing v7 SF-CHAMP & DTA Snapshot Simulation ===")
    v_tnc_av, v_tnc_h = calculate_nested_logit_utilities(
        fare_av=15.0, fare_h=20.0, ivtt_av=30.0, ivtt_h=35.0, ovtt=5.0, comfort_discount=1.0
    )
    
    mu_fh = 0.5
    i_fh = calculate_inclusive_value(v_tnc_av, v_tnc_h, mu_fh=mu_fh)
    print(f"For-Hire Nest Inclusive Value (Logsum): {i_fh:.4f}")
    
    # Income-segmented equity VOT testing (§7.2)
    vot_low  = calculate_income_segmented_vot(b_ivtt_k=-0.04, b_fare_k=-0.15)
    vot_high = calculate_income_segmented_vot(b_ivtt_k=-0.08, b_fare_k=-0.05)
    print(f"Income-Segmented VOT -> Low Income: ${vot_low:.2f}/hr | High Income: ${vot_high:.2f}/hr")
    
    # Upper-level composite utility with PopulationSim Income_Group (§7.1)
    for tier in ["low", "medium", "high"]:
        v_composite = calculate_upper_level_tour_mode_utility(i_fh, mu_fh, income_tier=tier)
        print(f"V_FH_Composite (Income_Group='{tier}'): {v_composite:.4f}")
    
    # Run DTA Loop
    run_dta_sfchamp_feedback_loop(c_base=1800, n_blocked=1, n_total=3, f_rubberneck=0.15)


