params = {
    # Required
    "s_FL": 800, # ft # Lenient
    "s_TOFL": 800, # ft # Lenient
    "rho_alt": 0.00235, # lbf/ft^3
    "rho_sea": 0.002377, # lbf/ft^3
    "g": 32.2, # ft/s^2
    "b_max": 6, # ft
    "V_max": 146.667, # ft/s 
    "Endurance": 5.0/60.0, # hours
    "R_turn": 100, # ft # Lenient
    # Derived from structural g-loading constraints
    "V_turn": 146.667, # ft/s # Lenient    
    # Designed
    "b": 6, # ft
    "e": 0.997, # unitless
    "AR": 6.750, # unitless
    "CLmaxL": 1.248, # unitless
    "CLmaxTO": 1.248, # unitless
    "CLmaxCruise": 0.648, # unitless
    "CD0": 0.012, # unitless
    "WTO_estimate": 10 # lbs
}