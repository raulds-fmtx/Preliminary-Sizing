import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from empennage_params import params, wing_flap_data, wing_data, hstab_data

# Define function to interpolate between two values in a dataframe
def interpolate_value(target, ind, dep, df):
    # Sort the dataframe by alpha to ensure correct interpolation
    df_sorted = df.sort_values(by=ind)
    
    # Extract alpha and the target column values
    ind_values = df_sorted[ind].values
    dep_values = df_sorted[dep].values
    
    # Create an interpolation function
    interp_func = interp1d(ind_values, dep_values, kind="linear", fill_value="extrapolate")
    
    # Compute the interpolated value
    interpolated_value = interp_func(target)
    
    return interpolated_value

# Define function to calculate horizontal stabilizer size for a given moment arm and trim angle of attack
def calculate_bh(lh, aoa, params):
    e0 = 2 * params['CL0wf'] / (np.pi * params['AR']) * (lh / np.sqrt(lh**2 + params['zh']**2))
    deda = 2 * params['CLawf'] / (np.pi * params['AR']) * (lh / np.sqrt(lh**2 + params['zh']**2))
    t1 = params['ARh'] * params['S'] * params['MAC'] / lh
    t2 = params['Cmacwf'] + (params['CL0wf'] * -params['SM_wing']) + (params['CLawf'] * -params['SM_wing'] * np.deg2rad(aoa))
    t3 = params['CL0h'] - (params['CLah'] * e0) + (params['CLah'] * (1 - deda) * lh / params['MAC'] * np.deg2rad(aoa))
    return np.sqrt(t1 * t2 / t3)

# Define function to calculate angle of attack for a given coefficient of lift
def aoa(lh, bh, CL, params):
    e0 = 2 * params['CL0wf'] / (np.pi * params['AR']) * (lh / np.sqrt(lh**2 + params['zh']**2))
    t1 = params['CL0wf'] + bh**2/(params['ARh']*params['S']) * (params['CL0h'] - params['CLah'] * e0)
    t2 = params['CLawf'] + bh**2/(params['ARh']*params['S']) * params['CLah']
    return np.rad2deg((CL - t1) / t2)

# Define function to calculate coefficient of drag for a given angle of attack
def CD(aoa, lh, bh, flap = False):
    e0 = 2 * params['CL0wf'] / (np.pi * params['AR']) * (lh / np.sqrt(lh**2 + params['zh']**2))
    if flap:
        CD_wing = interpolate_value(aoa, 'alpha', 'CD', wing_flap_data)
    else:
        CD_wing = interpolate_value(aoa, 'alpha', 'CD', wing_data)
    CD_hstab = interpolate_value(aoa - np.rad2deg(e0), 'alpha', 'CD', hstab_data)
    return CD_wing + bh**2 / (params['ARh'] * params['S']) * CD_hstab

# Define function to calculate lift coefficient for a given angle of attack
def CL(aoa, lh, bh, flap = False):
    e0 = 2 * params['CL0wf'] / (np.pi * params['AR']) * (lh / np.sqrt(lh**2 + params['zh']**2))
    if flap:
        CL_wing = interpolate_value(aoa, 'alpha', 'CL', wing_flap_data)
    else:
        CL_wing = interpolate_value(aoa, 'alpha', 'CL', wing_data)
    CL_hstab = interpolate_value(aoa - np.rad2deg(e0), 'alpha', 'CL', hstab_data)
    return CL_wing + bh**2 / (params['ARh'] * params['S']) * CL_hstab

# Define function to calculate static margin of the aircraft
def SM(lh,bh):
    deda = 2 * params['CLawf'] / (np.pi * params['AR']) * (lh / np.sqrt(lh**2 + params['zh']**2))
    x_cg = -params['SM_wing'] * params['MAC'] + params['x_acwf']
    x_ach = lh + x_cg
    t1 = params['x_acwf'] + params['CLah']/params['CLawf'] * bh**2/params['ARh']/params['S'] * x_ach * (1 - deda)
    t2 = 1 + params['CLah']/params['CLawf'] * bh**2/params['ARh']/params['S'] * (1 - deda)
    return t1/t2/(12*params['MAC'])

# Define function to calculate T/W ratio for a given coefficient of drag
def TW_req(CD0, params):
    t1 = params['rho_alt'] * CD0 * params['Vmax']**2
    t2 = 2 * params['W/S']
    t3 = params['rho_alt'] * np.pi * params['e'] * params['AR'] * params['Vmax']**2
    return t1/t2 + t2/t3

def verify(lh, bh, aoa_trim, params):
    # Verify bh is on bh_range
    if bh < params['bh_range'][0] or bh > params['bh_range'][1]:
        return False, {'aoa_L/TO': None, 'TW_req': None}
    # Calculate values
    CLCruise = CL(aoa_trim, lh, bh)
    aoa_L_TO = aoa(lh, bh, params['CLmaxL/TO'], params)
    aoa_CL_0 = aoa(lh, bh, 0, params)
    TW = TW_req(CD(aoa_CL_0, lh, bh), params)
    # Perform verification
    ver_cruise = CLCruise > params['CLCruise']
    ver_aoa = aoa_L_TO > params['aoa_L/TO_range'][0] and aoa_L_TO < params['aoa_L/TO_range'][1]
    ver_TW = TW < params['T/W']
    # return True if all conditions are met, False otherwise
    return ver_cruise and ver_aoa and ver_TW, {'aoa_L/TO': aoa_L_TO, 'TW_req': TW}

# Calculate horizontal stabilizer size for each moment arm and angle of attack
lh_arr = np.linspace(params['lh_range'][0],params['lh_range'][1],1001)
aoa_arr = np.linspace(params['aoa_trim_range'][0],params['aoa_trim_range'][1],11)
bh_arr = np.zeros((len(lh_arr),len(aoa_arr)))

# List to store verified data
verified_data = []

# Verify each horizontal stabilizer size
for i in range(len(lh_arr)):
    for j in range(len(aoa_arr)):
        bh = calculate_bh(lh_arr[i], aoa_arr[j], params)
        bh_arr[i,j] = np.real(bh)
        
        verified, data = verify(lh_arr[i], bh, aoa_arr[j], params)
        if verified:
            sm = SM(lh_arr[i],bh)
            x_ac = (sm * 12 * params['MAC']) + (params['x_acwf'] - params['SM_wing'] * params['MAC'])
            x_cg = x_ac - sm * 12 * params['MAC']
            x_ach = lh_arr[i] * 12 + x_cg
            
            verified_data.append({
                'lh (ft)': lh_arr[i],
                'bh (ft)': bh,
                'aoa_trim (deg)': aoa_arr[j],
                'aoa_TO/L (deg)': data['aoa_L/TO'],
                'T/W_req': data['TW_req'],
                'SM': sm,
                'X_AC (in)': x_ac,
                'X_CG (in)': x_cg,
                'X_ACH (in)': x_ach,
                'X_ACWF (in)': params['x_acwf']
            })
            
# Plot bh vs lh values in verified_data as a scatter plot
for i in range(len(aoa_arr)):
    plt.plot(lh_arr, bh_arr[:,i], label=f'aoa = {aoa_arr[i]}')
plt.legend()
plt.xlabel('lh')
plt.ylabel('bh')
plt.ylim(params['bh_range'])
plt.xlim(params['lh_range'])
plt.title('bh vs lh')
plt.grid(True)
plt.show()

# Convert verified data to DataFrame and save to CSV
verified_df = pd.DataFrame(verified_data)
verified_df.to_csv('./data/solutions/hstab.csv', index=False)

# Print the rows with the smallest values for each criterion
print("Solution with smallest lh value:")
print(verified_df.loc[verified_df['lh (ft)'].idxmin()])

print("\nSolution with smallest bh value:")
print(verified_df.loc[verified_df['bh (ft)'].idxmin()])

print("\nSolution with smallest aoa_trim value:")
print(verified_df.loc[verified_df['aoa_trim (deg)'].idxmin()])

print("\nSolution with smallest aoa_TO/L value:")
print(verified_df.loc[verified_df['aoa_TO/L (deg)'].idxmin()])

print("\nSolution with smallest T/W_req value:")
print(verified_df.loc[verified_df['T/W_req'].idxmin()])