from gurobipy import GRB

#chatbot did this i cba to figure out gurobis debugging tools.
def get_feedback(model, hours, lambda_t, p_vent, temp1, temp2, p1, p2, V, hum, z1_cold, z1_hot, z2_cold, ON):
    """
    Prints optimization results for a single day using the provided local variables.
    """
    if model.Status == GRB.OPTIMAL:
        print("\n" + "="*80)
        print(f"OPTIMIZATION SUCCESSFUL")
        print(f"Total Cost (Objective): {model.ObjVal:.4f}")
        print("="*80 + "\n")

        results = []
        
        # Header
        print(f"{'Time':<5} | {'R1 Temp':<8} | {'R2 Temp':<8} | {'R1 Heat':<8} | {'R2 Heat':<8} | {'Vent':<5} | {'R1 Hum':<7} | {'Alerts'}")
        print("-" * 115)

        for t in range(hours):
            # Fix: Access variables using [t] only (1D), using .X to get the value
            r1_t = temp1[t].X
            r2_t = temp2[t].X
            p1_val = p1[t].X
            p2_val = p2[t].X
            vent_on = V[t].X
            hum_val = hum[t].X
            
            # Check for Overrules (active binary variables)
            alerts = []
            if z1_cold[t].X > 0.5: alerts.append("R1_COLD")
            if z1_hot[t].X > 0.5:  alerts.append("R1_HOT")
            if z2_cold[t].X > 0.5: alerts.append("R2_COLD")
            if ON[t].X > 0.5:      alerts.append("VENT_START")
            
            alert_str = ", ".join(alerts)
            
            # Safe price access (handles if lambda_t is a list or scalar)
            current_price = lambda_t[t] if hasattr(lambda_t, '__getitem__') else lambda_t

            # Print row formatted
            print(f"{t:<5} | {r1_t:<8.2f} | {r2_t:<8.2f} | {p1_val:<8.2f} | {p2_val:<8.2f} | {int(vent_on):<5} | {hum_val:<7.1f} | {alert_str}")

            results.append({
                "Hour": t,
                "R1_Heat": p1_val,
                "R2_Heat": p2_val,
                "Vent_Status": int(vent_on)
            })

        # Calculate Totals
        total_heat_energy = sum(r["R1_Heat"] + r["R2_Heat"] for r in results)
        total_vent_energy = sum(r["Vent_Status"] * p_vent for r in results)
        
        print("\n" + "-"*30)
        print(f"Total Heat Energy: {total_heat_energy:.2f} kWh")
        print(f"Total Vent Energy: {total_vent_energy:.2f} kWh")
        print(f"Total Energy Consumed: {total_heat_energy + total_vent_energy:.2f} kWh")
        print("-"*30)

    elif model.Status == GRB.INFEASIBLE:
        print("\nModel is Infeasible!")
        print("Computing IIS (Irreducible Inconsistent Subsystem)...")
        model.computeIIS()
        model.write("assignment/taskA/model_conflict.ilp") 
        print("Conflict written to 'model_conflict.ilp'")

    else:
        print(f"\nOptimization ended with status {model.Status}")