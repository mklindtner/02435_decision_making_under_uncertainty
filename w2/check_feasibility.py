import gurobipy as gp



def _get_params():
    P2H = 0
    H2P = 0
    R_H2P = 0
    R_P2H = 0
    D_t = 0*[0] 
    w_t = 0*[0]
    c_t = 0*[0]
    C_elzr = 0*[0]
    H = 0

    return P2H, H2P, R_H2P, R_P2H, D_t, w_t, c_t, C_elzr, H


def check_feasibility01(state):
    model = gp.models("foo")
    wind_prev, wind, price_prev, price, t = state
    #rest of the model
    P2H, H2P, R_H2P, R_P2H, D_t, w_t, c_t, C_elzr, H = _get_params()    

    model.addVar(hours, vtype=, name="P_grid")

