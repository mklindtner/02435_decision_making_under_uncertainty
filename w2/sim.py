import gurobipy as gp
import csv
from WindProcess import wind_model
from PriceProcess import price_model
from check_feasibility import check_feasibility01

def policy(state):
    #pick random values here
    #set everything to 0 first
    return None

def dummy_policy(state):
    #smart way to chose this?
    #forget about lyzer
    #add just power*generated_prices
    return None


def apply_dynamics(state, decisions):
    return None

    

#Initialize
T = 10

#wind
wind = 0
wind_prev = 0
#price
price = 0
price_prev = 0

data = None

#run for-loop
for t in range(T):
    #----initialize state----

    #wind
    wind_tmp = wind
    wind = wind_model(wind, wind_prev, data)
    wind_prev = wind_tmp

    #price
    price_tmp = price
    price = price_model(price, price_prev, wind, data)
    price_prev = price_tmp

    #Policy
    state = (wind_prev, wind, price_prev, price)
    decisions = policy(state)

    #infeasibility
    infeasible = check_feasibility(decisions)
    if infeasible:
        decisions = dummy_policy(t)

    #stuff i dont wanna think about right now
    cost[t] = current_price*decisions[power_from_grid]
    next_state = apply_dynamics(state,decisions)

    

