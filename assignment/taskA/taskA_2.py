import pandas as pd
import gurobipy as gp
from gurobipy import GRB, quicksum
import numpy as np
from SystemCharacteristics import get_fixed_data
from debugging_model import get_feedback


def optimize_single_day(day):
    #Setup
    model = gp.Model("Task1A")
    fixed_data = get_fixed_data()
    df_pricedata = pd.read_csv("assignment/taskA/PriceData.csv")
    df_or1 = pd.read_csv("assignment/taskA/OccupancyRoom1.csv")
    df_or2 = pd.read_csv("assignment/taskA/OccupancyRoom2.csv")
    hours = fixed_data["num_timeslots"]

    lambda_t = df_pricedata.iloc[day,:].values #eletrical prices at time t
    RO1 = df_or1.iloc[day, :].values #room 1 for occupancy at time t
    RO2 = df_or2.iloc[day, :].values #room 2 for occupancy at time t


    #heat coefficients
    xi_exh = fixed_data["heat_exchange_coeff"]
    xi_loss = fixed_data["thermal_loss_coeff"]
    xi_conv = fixed_data["heating_efficiency_coeff"]
    xi_cool = fixed_data["heat_vent_coeff"]
    xi_occ = fixed_data["heat_occupancy_coeff"]


    #humidity coefficients
    eta_occ = fixed_data["humidity_occupancy_coeff"]
    eta_vent = fixed_data["humidity_vent_coeff"]


    #Parameters
    p_vent = fixed_data["ventilation_power"]
    T_low = fixed_data["temp_min_comfort_threshold"]
    T_high = fixed_data["temp_max_comfort_threshold"]
    T_ok = fixed_data["temp_OK_threshold"]
    T_out = fixed_data["outdoor_temperature"] #outdoor temperature at time t
    H_high = fixed_data["humidity_threshold"]
    P_overline = fixed_data["heating_max_power"] #this is written as P_r but we only have 1 max power heating ?
    T_circ = -3 #read from Systemcharacticeristics
    M_low = T_low - T_circ
    M_high = T_ok - T_circ
    M_hum = 100 - H_high #this might course problems


    #Variables
    p1 = model.addVars(hours, lb=0, ub=P_overline, vtype=GRB.CONTINUOUS, name="p1")
    p2 = model.addVars(hours, lb=0, ub=P_overline, vtype=GRB.CONTINUOUS, name="p2")
    temp1 = model.addVars(hours, lb=T_circ, ub=2*T_high, name="temp1") #couldn't find a good ub value
    temp2 = model.addVars(hours, lb=T_circ, ub=2*T_high, name="temp2")
    z1_cold = model.addVars(hours, vtype=GRB.BINARY, name="z1_cold")
    z1_hot = model.addVars(hours, vtype=GRB.BINARY, name="z1_hot")
    z2_cold = model.addVars(hours, vtype=GRB.BINARY, name="z2_cold")
    z2_hot = model.addVars(hours, vtype=GRB.BINARY, name="z2_hot ")

    ON = model.addVars(hours, vtype=GRB.BINARY, name="ON")
    OFF = model.addVars(hours, vtype=GRB.BINARY, name="OFF")
    V = model.addVars(hours, vtype=GRB.BINARY, name="V")
    hum1 = model.addVars(hours, lb=0, ub=100, vtype=GRB.CONTINUOUS, name="hum1")
    # hum2 = model.addVars(hours, lb=0, ub=100, vtype=GRB.CONTINUOUS, name="hum2")

    #Constraints

    #temp
    model.addConstrs((temp1[t] == temp1[t-1] - xi_exh*(temp1[t-1]-temp2[t-1]) - xi_loss*(temp1[t-1]-T_out[t-1]) + xi_conv*p1[t-1]-xi_cool*V[t-1]+xi_occ*RO1[t-1] for t in range(1,hours)), name="temp1_balance_{t}")
    # model.addConstrs((temp2[t] == temp2[t-1] - xi_exh*(temp2[t-1]-temp1[t-1]) - xi_loss*(temp2[t-1]-T_out[t-1]) + xi_conv*p2[t-1]-xi_cool*V[t-1]+xi_occ*RO2[t-1] for t in range(1,hours)), name="temp2_balance_{t}")

    #humidty
    model.addConstrs((hum1[t] == hum1[t-1] + eta_occ*(RO1[t-1]+RO2[t-1])-eta_vent*V[t-1] for t in range(1,hours)))
    # model.addConstrs((hum2[t] == hum2[t-1] + eta_occ*RO2[t-1]-eta_vent*V[t-1] for t in range(1,hours)))

    #Ventilator
    for t in range(hours):
        if t >= 2:
            model.addConstr(V[t] >= ON[t] + ON[t-1] + ON[t-2])
        elif t == 1:
            model.addConstr(V[t] >= ON[t] + ON[t-1])
        #we set t=0 above

    model.addConstrs((OFF[t] <= V[t-1]for t in range(1, hours)))
    model.addConstrs((ON[t] <= 1-V[t-1]for t in range(1,hours)))
    model.addConstrs((ON[t] + OFF[t] <= 1 for t in range(hours)))
    model.addConstrs((V[t] == V[t-1]+ON[t]-OFF[t] for t in range(1,hours)))


    #Temperature overrule controller

    #Low temperature

    #r1
    model.addConstrs((T_low - temp1[t] <= M_low*z1_cold[t] for t in range(hours)))
    model.addConstrs((T_ok - temp1[t] <= M_high*(1-z1_cold[t-1]+z1_cold[t]) for t in range(1,hours)))
    model.addConstrs((p1[t] >= P_overline*z1_cold[t] for t in range(hours)))

    #r2
    model.addConstrs((T_low - temp2[t] <= M_low*z2_cold[t] for t in range(hours)))
    model.addConstrs((T_ok - temp2[t] <= M_high*(1-z2_cold[t-1]+z2_cold[t]) for t in range(1,hours)))
    model.addConstrs((p2[t] >= P_overline*z2_cold[t] for t in range(hours)))

    #High temperature

    #r1
    model.addConstrs((temp1[t] - T_high <= M_high*z1_hot[t] for t in range(hours)))
    model.addConstrs((p1[t] <= P_overline*(1-z1_hot[t]) for t in range(hours)))

    #r2
    model.addConstrs((temp2[t] - T_high <= M_high*z2_hot[t] for t in range(hours)))
    model.addConstrs((p2[t] <= P_overline*(1-z2_hot[t])for t in range(hours)))


    #Humidity constraints
    model.addConstrs((hum1[t] - H_high <= M_hum*V[t] for t in range(1,hours)))
    # model.addConstrs((hum2[t] - H_high <= M_hum*V[t] for t in range(1,hours)))

    #Objective
    obj = quicksum(lambda_t[t]*(p1[t] + p2[t] + p_vent*V[t])for t in range(hours))

    model.setObjective(obj, GRB.MINIMIZE)


    #Initializie
    init_temp = fixed_data['initial_temperature']
    init_hum = fixed_data['initial_humidity']

    # Temperature Initialization
    model.addConstr(temp1[0] == init_temp, name="Init_Temp_R1")
    model.addConstr(temp2[0] == init_temp, name="Init_Temp_R2")
    model.addConstr((T_ok - temp1[0] <= M_high*(1 + z1_cold[0])), name="R1_LowTemp_Overrule_Init") #For t = 0 of every day
    model.addConstr((T_ok - temp2[0] <= M_high*(1 + z2_cold[0])), name="R2_LowTemp_Overrule_Init") #-||-

    # Humidity Initialization
    model.addConstr(hum1[0] == init_hum, name="Init_Hum_R1")
    # model.addConstr(hum2[0] == init_hum, name="Init_Hum_R2")

    # Ventilization Initialization
    model.addConstr(V[0] == ON[0]) #the init data forces teh ventilator to start so we need to also start ON
    model.addConstr(OFF[0] == 0)


    #optimization / debugging
    model.optimize()
    hum2 = -1000
    get_feedback(
        model, hours, lambda_t, p_vent,
        temp1, temp2, p1, p2, V, hum1, hum2,
        z1_cold, z1_hot, z2_cold, ON
    )

    if model.status == GRB.OPTIMAL:
        return model, {
            'temp1': [temp1[t].X for t in range(hours)],
            'temp2': [temp2[t].X for t in range(hours)],
            'p1':    [p1[t].X for t in range(hours)],
            'p2':    [p2[t].X for t in range(hours)],
            'V':     [V[t].X for t in range(hours)],
            'hum1':  [hum1[t].X for t in range(hours)],
            # 'hum2':  [hum2[t].X for t in range(hours)],
            'price': lambda_t,
            'occ1':  RO1,
            'occ2':  RO2
        }
    else:
        print(f"Day {day} Infeasible!")
        model.computeIIS()
        model.write(f"assignement/taskA/infeasible_day_{day}.ilp")
        return None


