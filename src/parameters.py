params = {
    # Required
    "s_FL": 600, # ft
    "s_TOFL": 100, # ft
    "rho_alt": 0.00235, # lbf/ft^3
    "rho_sea": 0.002377, # lbf/ft^3
    "g": 32.2, # ft/s^2
    "b_max": 6, # ft
    "V_max": 146.667, # ft/s
    "Endurance": 5.0/60.0, # hours
    "R_turn": 50, # ft
    # Derived from structural g-loading constraints
    "V_turn": 146.667, # ft/s
    # Designed
    "e": 0.8, # unitless
    "AR": 5, # unitless
    "CLmaxL": 1.5, # unitless
    "CLmaxTO": 1.5, # unitless
    "CLmaxCruise": 1.5, # unitless
    "CD0": 0.02, # unitless
    "WTO_estimate": 10 # lbs
}