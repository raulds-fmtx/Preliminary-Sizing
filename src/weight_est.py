import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
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
battery_power_density_model = LinearRegression().fit(x1, y)

# Estimation functions
def aircraft_weight_estimate(weight_battery,weight_motor):
    return aircraft_model.predict([[weight_battery,weight_motor]])[0]

def motor_weight_estimate(thrust):
    return motor_weight_model.predict([[thrust]])[0]

def motor_power_estimate(thrust):
    return motor_power_model.predict([[thrust]])[0]

def battery_power_density_estimate(thrust):
    return battery_power_density_model.predict([[motor_power_estimate(thrust)]])[0]

# Calculate Weights, Thrust, and Power
def weight_estimate(TW_ratio, Endurance, WTO_guess, WTO_lower, WTO_upper):
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
            return None
        
        WTO_guess = (WTO_upper+WTO_lower)/2
    
    return [WTO_guess, 
            motor_weight_estimate(T_guess),
            Endurance * motor_power_estimate(T_guess) / battery_power_density_estimate(T_guess), 
            motor_power_estimate(T_guess)]
    
# Get lists of parameters dependence on endurance and thrust-to-weight ratio   
def full_estimation(thrust_weight_range, endurance_range, WTO_guess, WTO_lower, WTO_upper, num):
    thrust_space = np.linspace(thrust_weight_range[0], thrust_weight_range[1], 1000)
    endurance_space = np.linspace(endurance_range[0], endurance_range[1], num)
    
    takeoff_weight_list = []
    motor_weight_list = []
    battery_weight_list = []
    power_list = []
    tw_ratio_list = []
    
    for e in endurance_space:
        takeoff_weight = []
        motor_weight = []
        battery_weight = []
        power = []
        tw_ratio = []
        for t in thrust_space:
            result = weight_estimate(t, e, WTO_guess, WTO_lower, WTO_upper) 
            if result is not None:
                takeoff_weight.append(result[0])
                motor_weight.append(result[1])
                battery_weight.append(result[2])
                power.append(result[3])
                tw_ratio.append(t)
        takeoff_weight_list.append(takeoff_weight)
        motor_weight_list.append(motor_weight)
        battery_weight_list.append(battery_weight)
        power_list.append(power)
        tw_ratio_list.append(tw_ratio)
        
    return takeoff_weight_list, motor_weight_list, battery_weight_list, power_list, tw_ratio_list
      
def visualize_estimation(endurance_range, takeoff_weight_list, motor_weight_list, battery_weight_list, power_list, tw_ratio_list):
    fig, axs = plt.subplots(2,2)
    fig.suptitle('Sizing Analysis')
    
    axs[0,0].set_ylabel('Takeoff Weight (lbs)')
    axs[0,1].set_ylabel('Motor Weight (lbs)')
    axs[1,0].set_ylabel('Battery Weight (lbs)')
    axs[1,1].set_ylabel('Power (W)')
    
    for i in range(0,2):
        for j in range(0,2):
            for k in range(len(endurance_range)):
                if (i,j) == (0,0):
                    axs[i,j].plot(tw_ratio_list[k], takeoff_weight_list[k], label="{:.2f} mins".format(endurance_range[k]*60))
                if (i,j) == (0,1):
                    axs[i,j].plot(tw_ratio_list[k], motor_weight_list[k], label="{:.2f} mins".format(endurance_range[k]*60))
                if (i,j) == (1,0):
                    axs[i,j].plot(tw_ratio_list[k], battery_weight_list[k], label="{:.2f} mins".format(endurance_range[k]*60))
                if (i,j) == (1,1):
                    axs[i,j].plot(tw_ratio_list[k], power_list[k], label="{:.2f} mins".format(endurance_range[k]*60))
            axs[i,j].legend()
            axs[i,j].set_xlabel('Thrust-to-Weight Ratio')
            axs[i,j].grid()
    
    plt.show()
   
# Weight Estimation sweep parameters
tw_range = [0.1,1.5]
endurance_range = [5/60.0,10/60.0]
num = 6
WTO_guess = 7 # lbs
WTO_lower = 2 # lbs
WTO_upper = 12 # lbs

# Design Point
endurance = 5
TW_ratio = 0.6 

# Run Weight Estimation
takeoff_weight_list, motor_weight_list, battery_weight_list, power_list, tw_ratio_list = full_estimation(tw_range, endurance_range, WTO_guess, WTO_lower, WTO_upper, num)
visualize_estimation(
    np.linspace(endurance_range[0],endurance_range[1],num), 
    takeoff_weight_list,
    motor_weight_list, 
    battery_weight_list, 
    power_list, 
    tw_ratio_list
)