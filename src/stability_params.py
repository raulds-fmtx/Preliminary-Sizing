import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# Function to remove whitespace from DataFrame
def remove_whitespace(df):
    df.columns = df.columns.str.strip()  # Strip whitespace from column names
    for col in df.select_dtypes(['object']).columns:
        df[col] = df[col].str.strip()  # Strip whitespace from string data
    return df

# Import CSV data
wing_data = pd.read_csv('data/polars/Wing.csv')
hstab_data = pd.read_csv('data/polars/Hstab.csv')
vstab_data = pd.read_csv('data/polars/Vstab.csv')
wing_side_data = pd.read_csv('data/polars/Wing-Side-Slip.csv')
hstab_side_data = pd.read_csv('data/polars/Hstab-Side-Slip.csv')

# General Params UPDATE THESE
params = {
    # Trim Angle of Attack
    'aoa_trim': 3.0, # deg
    # Wing Geometry
    'AR': 6.750, 
    'S': 5.333, # ft^2
    'b': 6.0, # ft
    'MAC': 11.555/12.0, # ft
    'e': 0.997,
    'SM_wing': -0.25,
    'lambda_c/4': 12.529, # rads
    # H-Stab Geometry
    'ARh': 4.571,
    'Sh': 0.8750820389, # ft^2
    'bh': 2, # ft
    'lh': 1.5, # ft
    'zh': 1.5, # ft
    # V-Stab Geometry
    'ARv': 4.571,
    'Sv': 0.750, # ft^2
    'bv': 1.5, # ft
    'lv': 1.5, # ft
    'y_MAC': 1.0, # ft
    'z_MAC': 8.0/12.0, # ft
    'twin': True,
}

# Get the CL0 coefficients
CL0wf = wing_data.loc[wing_data['alpha'] == 0, 'CL'].values[0]
CL0h = hstab_data.loc[hstab_data['alpha'] == 0, 'CL'].values[0]
CL0v = vstab_data.loc[vstab_data['alpha'] == 0, 'CL'].values[0]
# Get the CLa coefficients
CLawf = LinearRegression().fit(wing_data['alpha'].values.reshape(-1, 1), wing_data['CL'].values).coef_[0] * (360/(2*np.pi))
CLah = LinearRegression().fit(hstab_data['alpha'].values.reshape(-1, 1), hstab_data['CL'].values).coef_[0] * (360/(2*np.pi))
CLav = LinearRegression().fit(vstab_data['alpha'].values.reshape(-1, 1), vstab_data['CL'].values).coef_[0] * (360/(2*np.pi))
# Get the CD coefficients
wing_poly = PolynomialFeatures(degree=2)
a_wing_poly = wing_poly.fit_transform(wing_data['alpha'].values.reshape(-1, 1))
wing_poly.fit(a_wing_poly, wing_data['CD'].values)
wing_model = LinearRegression().fit(a_wing_poly, wing_data['CD'].values)
a, b, c = wing_model.coef_
CDawf = 2 * a * params['aoa_trim'] + b
CD0wf = a * params['aoa_trim']**2 + b * params['aoa_trim'] + c - CDawf * params['aoa_trim']
hstab_poly = PolynomialFeatures(degree=2)
a_hstab_poly = hstab_poly.fit_transform(hstab_data['alpha'].values.reshape(-1, 1))
hstab_poly.fit(a_hstab_poly, hstab_data['CD'].values)
hstab_model = LinearRegression().fit(a_hstab_poly, hstab_data['CD'].values)
a, b, c = hstab_model.coef_
CDah = 2 * a * params['aoa_trim'] + b
CD0h = a * params['aoa_trim']**2 + b * params['aoa_trim'] + c - CDah * params['aoa_trim']
vstab_poly = PolynomialFeatures(degree=2)
a_vstab_poly = vstab_poly.fit_transform(vstab_data['alpha'].values.reshape(-1, 1))
vstab_poly.fit(a_vstab_poly, vstab_data['CD'].values)
vstab_model = LinearRegression().fit(a_vstab_poly, vstab_data['CD'].values)
a, b, c = vstab_model.coef_
CDav = 2 * a * params['aoa_trim'] + b
CD0v = a * params['aoa_trim']**2 + b * params['aoa_trim'] + c - CDav * params['aoa_trim']
# Get the ClB coefficients
ClBwf = LinearRegression().fit(wing_side_data['Beta'].values.reshape(-1, 1), wing_side_data['Cl'].values).coef_[0] * (360/(2*np.pi))
ClBh = LinearRegression().fit(hstab_side_data['Beta'].values.reshape(-1, 1), hstab_side_data['Cl'].values).coef_[0] * (360/(2*np.pi))


wing = {
    'CL0wf': CL0wf,
    'CLawf': CLawf,
    'Cmacwf': -0.12306, # FIND MANUALLY
    'CD0wf': CD0wf,
    'CDawf': CDawf,
    'ClBwf': ClBwf,
}

h_stab = {
    'CL0h': CL0h,
    'CLah': CLah,
    'CD0h': CD0h,
    'CDah': CDah,
    'ClBh': ClBh,
    'e0': 2*CL0wf/(np.pi*params['AR']) * params['lh']/np.sqrt(params['lh']**2 + params['zh']**2),
    'deda': 2*CLawf/(np.pi*params['AR']) * params['lh']/np.sqrt(params['lh']**2 + params['zh']**2),
}

v_stab = {
    'CL0v': CL0v,
    'CLav': CLav,
    'CD0v': CD0v,
    'CDav': CDav,
    'dsdB': 4.22652*params['Sv']/params['S']/(1+np.cos(params['lambda_c/4'])) + 0.012431*params['AR'],
}