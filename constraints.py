import numpy as np
import matplotlib.pyplot as plt
from parameters import params
    
def takeoff_constraint(wing_loading):
    rho_alt = params['rho_alt']
    rho_sea = params['rho_sea']
    s_TOFL = params['s_TOFL']
    CLmaxTO = params['CLmaxTO']
    return (37.5/(rho_alt/rho_sea*s_TOFL*CLmaxTO)) * wing_loading

def landing_constraint():
    rho_alt = params['rho_alt']
    s_FL = params['s_FL']
    CLmaxL = params['CLmaxL']
    return s_FL*rho_alt*CLmaxL/1.014

def size_constraint(W_TO):
    AR=params['AR']
    b_max=params['b_max']
    return AR/b_max**2 * W_TO

def velocity_constraint(wing_loading):
    V_max = params['V_max']
    rho_alt = params['rho_alt']
    CD0 = params['CD0']
    e = params['e']
    AR = params['AR']
    return rho_alt*CD0*V_max**2/(2*wing_loading) + 2*wing_loading/(rho_alt*np.pi*e*AR*V_max**2)

def min_turn_radius_constraint():
    V_turn = params['V_turn']
    g = params['g']
    R_turn = params['R_turn']
    rho_alt = params['rho_alt']
    CLmaxCruise = params['CLmaxCruise']
    return (rho_alt*V_turn**2*CLmaxCruise)/(2*np.sqrt((V_turn**2/(R_turn*g))**2+1))

# Plot inputs
WTO_estimate = params['WTO_estimate']
wing_loading = np.linspace(0.5,4.5,1000)

# Enter Design Point Here
TW_ratio_val = 0.5
wing_loading_val = 8.0/5.0

# Create a sample plot
plt.plot(wing_loading,takeoff_constraint(wing_loading), label='Takeoff (min)')
plt.plot(wing_loading,velocity_constraint(wing_loading), label='Velocity (min)')
plt.axvline(x=size_constraint(WTO_estimate), color='r', linestyle='--', label='Size (min)')
plt.axvline(x=min_turn_radius_constraint(), color='b', linestyle='--', label='Turn Radius (max)')
plt.axvline(x=landing_constraint(), color='g', linestyle='--', label='Landing (max)')
if (TW_ratio_val and wing_loading_val):
    plt.scatter(wing_loading_val, TW_ratio_val, color='r', label='Design Point')
plt.ylim((0,1.0))
plt.legend()

# Show the plot
plt.show()

