import numpy as np
from taskA_2 import optimize_single_day
from PlotsRestaurant import plot_HVAC_results

#Exercise 2
days = 100
obj_res = np.zeros(days)
for day in range(days):
    model_res,_ = optimize_single_day(day)
    obj_res[day] = model_res.ObjVal

print("---Average daily eletrcity cost---")
print(obj_res.mean())



# #Exercise 3
# np.random.seed(7)
# day_choice = np.random.randint(0, 101, 2)
day_choice = np.array([7,42])

model_res, HVAC_results1 = optimize_single_day(day_choice[0])
model_res, HVAC_results2 = optimize_single_day(day_choice[1])

plot_HVAC_results([HVAC_results1, HVAC_results2])

