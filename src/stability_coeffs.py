from stability_params import wing, h_stab, v_stab, params

# Tail Volume Coefficients
Vh_long = params['Sh']/params['S'] * params['lh']/params['MAC']
Vh_lat = params['Sh']/params['S'] * params['bh']/params['b']
Vv_lat = params['Sv']/params['S'] * params['z_MAC']/params['b']
Vv_long = params['Sv']/params['S'] * params['lv']/params['b']
# Longitudinal Stability Coefficients
CL0 = wing['CL0wf'] - h_stab['CLah'] * params['Sh']/params['S'] * (h_stab['e0'] - h_stab['CL0h']/h_stab['CLah'])
CLa = wing['CLawf'] - h_stab['CLah'] * params['Sh']/params['S']
Cm0 = wing['Cmacwf'] - wing['CL0wf'] * params['SM_wing'] - (h_stab['CL0h'] - h_stab['CLah']*h_stab['e0']) * Vh_long
Cma = - wing['CLawf'] * params['SM_wing'] - h_stab['CLah'] * (1 - h_stab['deda']) * Vh_long * params['lh']/params['MAC']
CD0 = wing['CD0wf'] + params['Sh']/params['S']*h_stab['CD0h'] + params['Sv']/params['S']*v_stab['CD0v']
CDa = wing['CDawf'] + params['Sh']/params['S']*h_stab['CDah'] + params['Sv']/params['S']*v_stab['CDav']
# Lat/d Stability Coefficients
num_fins = params['twin'] if 2 else 1
Cl0 = 0
ClB = wing['ClBwf'] + Vh_lat*h_stab['ClBh'] + num_fins*Vv_lat*(1-v_stab['dsdB'])*v_stab['CLav']
Cn0 = 0
CnB = num_fins*Vv_long*(1-v_stab['dsdB'])*v_stab['CLav']
CY0 = 0
CYB = -num_fins*params['Sv']/params['S']*(1-v_stab['dsdB'])*v_stab['CLav']