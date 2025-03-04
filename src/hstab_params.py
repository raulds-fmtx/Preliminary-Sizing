import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Function to remove whitespace from DataFrame
def remove_whitespace(df):
    df.columns = df.columns.str.strip()  # Strip whitespace from column names
    for col in df.select_dtypes(['object']).columns:
        df[col] = df[col].str.strip()  # Strip whitespace from string data
    return df

# Import CSV data
wing_flap_data = pd.read_csv('data/polars/Wing-Flap.csv')
wing_data = pd.read_csv('data/polars/Wing.csv')
hstab_data = pd.read_csv('data/polars/Hstab.csv')

# Get the coefficients
CL0wf = wing_data.loc[wing_data['alpha'] == 0, 'CL'].values[0]
CL0wf_flaps = wing_flap_data.loc[wing_flap_data['alpha'] == 0, 'CL'].values[0]
CL0h = hstab_data.loc[hstab_data['alpha'] == 0, 'CL'].values[0]
CLawf = LinearRegression().fit(wing_data['alpha'].values.reshape(-1, 1), wing_data['CL'].values).coef_[0] * (360/(2*np.pi))
CLawf_flaps = LinearRegression().fit(wing_flap_data['alpha'].values.reshape(-1, 1), wing_flap_data['CL'].values).coef_[0] * (360/(2*np.pi))
CLah = LinearRegression().fit(hstab_data['alpha'].values.reshape(-1, 1), hstab_data['CL'].values).coef_[0] * (360/(2*np.pi))

params = {
    # Constraints
    'T/W': 0.75, # unitless
    'W/S': 1.875, # lbf/ft^2
    "CLmaxL/TO": 1.248, # unitless
    "CLCruise": 0.648, # unitless
    "rho_alt": 0.00235, # lbf/ft^3
    'Vmax': 146.667, # ft/s
    # Wing Geometry
    'S': 5.333, # ft^2
    'MAC': 11.555/12.0, # ft
    'e': 0.997,
    'AR': 6.750, 
    'SM_wing': -0.25,
    'x_acwf': 6.985,
    # H-Stab Geometry
    'ARh': 4.571,
    # H-stab Sizing Params
    'aoa_trim_range': (0.0, 5.0), # deg
    'aoa_L/TO_range': (0.0, 10.0), # deg
    'lh_range': (1.0, 4.0), # ft
    'bh_range': (1.0, 4.0), # ft
    'zh': 1.5, # ft
    # Flight Surface Coefficients
    'CL0wf': CL0wf,
    'CL0wf_flaps': CL0wf_flaps,
    'CL0h': CL0h,
    'CLawf': CLawf,
    'CLawf_flaps': CLawf_flaps,
    'CLah': CLah,
    'Cmacwf': -0.12306, # FIND MANUALLY
}