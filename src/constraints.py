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
max_wing_loading = 5.0
max_tw_ratio = 1.0
wing_loading = np.linspace(0,max_wing_loading,1000)

# Enter Design Point Here
TW_ratio_val = None # Enter the thrust to weight ratio of the design point given by A&P
wing_loading_val = params['WTO_estimate']/(params['b']**2  / params['AR'])

# Calculate constraints
takeoff = takeoff_constraint(wing_loading)
velocity = velocity_constraint(wing_loading)
size = size_constraint(WTO_estimate)
turn_radius = min_turn_radius_constraint()
landing = landing_constraint()
if min([size]) < min([turn_radius,landing]):
    wing_loading_subset = np.linspace(size,min([turn_radius,landing]),1000)
else:
    wing_loading_subset = np.linspace(0,min([turn_radius,landing]),1000)
    print("Size constraint violated. Design point not feasible.")
takeoff_subset = takeoff_constraint(wing_loading_subset)
velocity_subset = velocity_constraint(wing_loading_subset)
min_takeoff_velocity = np.maximum(takeoff_subset,velocity_subset)


# Create a sample plot
plt.plot(wing_loading,takeoff, label='Takeoff (min)')
plt.plot(wing_loading,velocity, label='Velocity (min)')
if min([size]) > min([turn_radius,landing]):
    plt.axvline(x=size, color='r', linestyle='--', label='Size VIOLATED (min)')
else:
    plt.axvline(x=size, color='r', linestyle='--', label='Size (min)')
plt.axvline(x=turn_radius, color='b', linestyle='--', label='Turn Radius (max)')
plt.axvline(x=landing, color='g', linestyle='--', label='Landing (max)')
# Shade the feasible region
plt.fill_between(wing_loading_subset, min_takeoff_velocity, max_tw_ratio, where=(min_takeoff_velocity <= max_tw_ratio), color='gray', alpha=0.5)
# Plot the design point
if (TW_ratio_val and wing_loading_val):
    plt.scatter(wing_loading_val, TW_ratio_val, color='r', label='Design Point')
elif (wing_loading_val):
    plt.axvline(x=wing_loading_val, color='y', linestyle='-', label='Design Point')
plt.ylim((0,max_tw_ratio))
plt.xlim((0,max_wing_loading))
plt.legend(loc='upper right')
plt.xlabel('Wing Loading (lbs/ft^2)')
plt.ylabel('Thrust to Weight Ratio')
plt.title('Constraints Diagram')

# Show the plot
plt.show()

