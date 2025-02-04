import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from parameters import params

# Load CSV data
lipo_data = pd.read_csv('./data/lipo_weight_data.csv')
edf_data = pd.read_csv('./data/edf_weight_data.csv')
aircraft_data = pd.read_csv('./data/aircraft_weight_data.csv')

# Aircraft weight regression model
x1 = aircraft_data['Battery Weight (lbs)']
x2 = aircraft_data['Motor Weight (lbs)']
y = aircraft_data['Takeoff Weight (lbs)']
X = np.column_stack((x1,x2))
aircraft_model = LinearRegression().fit(X, y)
# Motor weight regression model
x1 = edf_data['Thrust (lbs)'].values.reshape(-1, 1)
y = edf_data['Weight (lbs)']
X = np.column_stack((x1))
motor_weight_model = LinearRegression().fit(x1, y)
# Motor power regression model
x1 = edf_data['Thrust (lbs)'].values.reshape(-1, 1)
y = edf_data['Power (W)']
X = np.column_stack((x1))
motor_power_model = LinearRegression().fit(x1, y)
# Battery weight regression model
x1 = lipo_data['Energy (Wh)'].values.reshape(-1, 1)
y = lipo_data['Energy Density (Wh/lb)']
X = np.column_stack((x1))
motor_power_density_model = LinearRegression().fit(x1, y)

# Estimation functions
def aircraft_weight_estimate(weight_battery,weight_motor):
    return aircraft_model.predict([[weight_battery,weight_motor]])[0]

def motor_weight_estimate(thrust):
    return motor_weight_model.predict([[thrust]])[0]

def motor_power_estimate(thrust):
    return motor_power_model.predict([[thrust]])[0]

def battery_power_density_estimate(thrust):
    return motor_power_density_model.predict([[motor_power_estimate(thrust)]])[0]

# Calculate Weights, Thrust, and Power
def weight_estimate(TW_ratio, Endurance, WTO_guess, WTO_lower, WTO_upper, show=True):
    lower_init = WTO_lower
    upper_init = WTO_upper
    
    while(True):
        T_guess = TW_ratio * WTO_guess
        Wmotor = motor_weight_estimate(T_guess)
        Wbattery = Endurance * motor_power_estimate(T_guess) / battery_power_density_estimate(T_guess)
        WTO_calc = aircraft_weight_estimate(Wbattery,Wmotor)
        
        if np.abs((WTO_guess-WTO_calc)/WTO_calc) < 0.0001 or WTO_guess < 0:
            break
        elif WTO_guess < WTO_calc:
            WTO_lower = WTO_guess
        elif WTO_guess > WTO_calc:
            WTO_upper = WTO_guess
        
        if np.abs(WTO_upper - lower_init) < 0.0001 or np.abs(WTO_lower - upper_init) < 0.0001:
            return False
        
        WTO_guess = (WTO_upper+WTO_lower)/2
    
    if show:
        print("Thrust-to-Weight Ratio:", TW_ratio)
        print("Takeoff Weight:", WTO_guess, "lbs")
        print("Thrust Req.:", TW_ratio * WTO_guess, "lbs")
        print("Motor Weight:", motor_weight_estimate(T_guess), "lbs")
        print("System Power:", motor_power_estimate(T_guess), "W")
        print("Battery Weight:", Endurance * motor_power_estimate(T_guess) / battery_power_density_estimate(T_guess), "lbs")
        print("Battery Energy:", Endurance * motor_power_estimate(T_guess), "Wh")
    
    return True
        
def tw_ratio_range(tw_lower, tw_upper, num, Endurance, WTO_guess, WTO_lower, WTO_upper):
    test_range = np.linspace(tw_lower, tw_upper, num)
    valid_range = []
    for i in test_range:
        if weight_estimate(i,Endurance,WTO_guess,WTO_lower,WTO_upper,False):
            valid_range.append(i)
    print("T/W range:", [min(valid_range),max(valid_range)])

# Paramaters
Endurance = params["Endurance"] # hours
TW_ratio = 0.6

# Initial Guess for WTO
WTO_guess = 10 # lbs
WTO_lower = 2 # lbs
WTO_upper = 20 # lbs
 
# Range for T/W
tw_lower = 0.1
tw_upper = 1.5
num = 10000

tw_ratio_range(tw_lower,tw_upper,15,Endurance,WTO_guess,WTO_lower,WTO_upper)
weight_estimate(TW_ratio,Endurance,WTO_guess,WTO_lower,WTO_upper)