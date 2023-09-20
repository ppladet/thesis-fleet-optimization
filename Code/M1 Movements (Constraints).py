from gurobipy import Model, GRB, quicksum
import pandas as pd


# ---------------------------------------------------#
################# Model Preparation #################
# ---------------------------------------------------#


# Read the consolidated data from CSV file
file_path = '/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Input (CSV)/M1 Input - 2.csv'
df_optimization_data = pd.read_csv(file_path)

print(df_optimization_data)


# Create optimization model
m = Model("fleet_optimization")


# Create the sets A, R, L, T from the CSV data
A = df_optimization_data['Aircraft Type - Identifier'].unique().tolist()
R = df_optimization_data['Route'].unique().tolist()
L = df_optimization_data['Flight Leg'].unique().tolist()
T = df_optimization_data['Period'].unique().tolist()


# Create the network & passenger demand parameters from the CSV data
Distance = df_optimization_data.set_index('Route')['Distance (km)'].to_dict()

P_B = df_optimization_data.set_index(['Route', 'Flight Leg', 'Period'])['P_B'].to_dict()
P_E = df_optimization_data.set_index(['Route', 'Flight Leg', 'Period'])['P_E'].to_dict()
D_B = df_optimization_data.set_index(['Route', 'Flight Leg', 'Period'])['D_B'].to_dict()
D_E = df_optimization_data.set_index(['Route', 'Flight Leg', 'Period'])['D_E'].to_dict()


# Create the aircraft performance parameters from the CSV data
Capacity_Business = df_optimization_data.set_index('Aircraft Type - Identifier')['Capacity Business'].to_dict()
Capacity_Economy = df_optimization_data.set_index('Aircraft Type - Identifier')['Capacity Economy'].to_dict()

Range = df_optimization_data.set_index('Aircraft Type - Identifier')['Range (km)'].to_dict()
Noise = df_optimization_data.set_index('Aircraft Type - Identifier')['Noise (EPNL - Adjusted)'].to_dict()

Flight_Time_Minutes = df_optimization_data.set_index(['Aircraft Type - Identifier', 'Route', 'Flight Leg'])['Flight Time (Minutes)'].to_dict()
Turnaround_Time = df_optimization_data.set_index('Aircraft Type - Identifier')['Turnaround Time (Minutes)'].to_dict()
Max_Flight_Minutes = df_optimization_data.set_index('Aircraft Type - Identifier')['Max Flight Minutes'].to_dict()


# Create the aircraft economics parameters from the CSV data
C_Active = df_optimization_data.set_index(['Aircraft Type - Identifier', 'Route', 'Flight Leg', 'Period'])['Active Costs (USD)'].to_dict()

C_Fixed_Active = df_optimization_data.set_index(['Aircraft Type - Identifier', 'Route', 'Flight Leg', 'Period'])['Fixed Costs - Active (USD)'].to_dict()
C_Fixed = df_optimization_data.set_index(['Aircraft Type - Identifier', 'Period'])['Fixed Costs (USD)'].to_dict()


# ---------------------------------------------------#
################# Decision Variables #################
# ---------------------------------------------------#


# X[a,r,l,t] represents the number of times a specific aircraft 'a' is flown on route 'r', during flight leg 'l', in time period 't'
X = {}
for a in A:
    for r in R:
        if Distance[r] <= Range[a]:
            for l in L:
                for t in T:
                    X[a,r,l,t] = m.addVar(vtype=GRB.INTEGER, name=f"X_{a}_{r}_{l}_{t}")

# Y_B[a,r,l,t] represents the number of business class passengers on aircraft 'a', on route 'r', during flight leg 'l', in time period 't'
Y_B = m.addVars(A, R, L, T, vtype=GRB.INTEGER, name="Y_B")

# Y_E[a,r,l,t] represents the number of economy class passengers on aircraft 'a', on route 'r', during flight leg 'l', in time period 't'
Y_E = m.addVars(A, R, L, T, vtype=GRB.INTEGER, name="Y_E")

# Z[a,t] is a binary variable that is 1 if aircraft 'a' is active during period 't', and 0 otherwise
Z = m.addVars(A, T, vtype=GRB.BINARY, name="Z")

# Idle[a,t] represents the idle time for aircraft 'a' during period 't'. Additional decision variable to represent idle time for each aircraft and period
Idle = m.addVars(A, T, vtype=GRB.CONTINUOUS, name="Idle")

# W[a,r,t] is a binary variable that is 1 if aircraft 'a' flies on route 'r' during period 't', and 0 otherwise
W = m.addVars(A, R, T, vtype=GRB.BINARY, name="W")


# ---------------------------------------------------#
################# Objective Function #################
# ---------------------------------------------------#


# Maximize Profit = (Revenue - Active Costs - Fixed Costs when aircraft is active)
m.setObjective(
    # Revenue from business and economy class passengers
    quicksum(
        Y_B[a, r, l, t] * P_B.get((r, l, t), 0) + Y_E[a, r, l, t] * P_E.get((r, l, t), 0)
        for a in A for r in R for l in L for t in T if (a, r, l, t) in X
    )
    # Subtract Active Costs
    - quicksum(
        X[a, r, l, t] * C_Active.get((a, r, l, t), 0)
        for a in A for r in R for l in L for t in T if (a, r, l, t) in X
    )
    # Subtract Fixed Costs when Flying
    - quicksum(
        Z[a, t] * C_Fixed[a, t]
        for a in A for t in T
    ),
    GRB.MAXIMIZE,
)


# ---------------------------------------------------#
################# Model Constraints #################
# ---------------------------------------------------#


# Calculate idle time for each aircraft in each period
total_time_per_period = 365 * 24 * 60  # Total minutes in a year

for a in A:
    for t in T:
        m.addConstr(
            Idle[a, t] == total_time_per_period - quicksum(
                X[a, r, l, t] * (Flight_Time_Minutes[a, r, l] + Turnaround_Time[a])
                for r in R for l in L if (a, r, l, t) in X
            ),
            name=f"Idle_Time_{a}_{t}"
        )


# Big M value, sufficiently large to enforce the constraint
big_M = 1000000  # might need to adjust this value based on the problem

# Link X and Z: if an aircraft is flown at least once, set Z to 1
for a in A:
    for t in T:
        m.addConstr(
            quicksum(X[a, r, l, t] for r in R for l in L if (a, r, l, t) in X) <= big_M * Z[a, t],
            name=f"Link_X_Z_{a}_{t}"
        )


# Both Ways Constraint: X[a, r, 'Outbound', t] = X[a, r, 'Inbound', t]
for a in A:
    for r in R:
        for t in T:
            if (a, r, "Outbound", t) in X and (a, r, "Inbound", t) in X:
                m.addConstr(
                    X[a, r, "Outbound", t] == X[a, r, "Inbound", t],
                    name=f"Both_Ways_{a}_{r}_{t}"
                )


# Max Flight Minutes Constraint: Sum(Flight_Time + Turnaround) * X <= Max_Flight_Minutes
for a in A:
    for t in T:
        m.addConstr(
            quicksum((Flight_Time_Minutes[a, r, l] + Turnaround_Time[a]) * X[a, r, l, t] for r in R for l in L if (a, r, l, t) in X) <= Max_Flight_Minutes[a],
            name=f"Max_Flight_Minutes_{a}_{t}"
        )


# Business Capacity Constraint: Y_B <= Capacity_Business * X
for a in A:
    for r in R:
        for l in L:
            for t in T:
                if (a, r, l, t) in X:
                    m.addConstr(
                        Y_B[a, r, l, t] <= Capacity_Business[a] * X[a, r, l, t],
                        name=f"Business_Capacity_{a}_{r}_{l}_{t}"
                    )

# Economy Capacity Constraint: Y_E <= Capacity_Economy * X
for a in A:
    for r in R:
        for l in L:
            for t in T:
                if (a, r, l, t) in X:
                    m.addConstr(
                        Y_E[a, r, l, t] <= Capacity_Economy[a] * X[a, r, l, t],
                        name=f"Economy_Capacity_{a}_{r}_{l}_{t}"
                    )


# Business Demand Constraint: Sum(Y_B) <= D_B
for r in R:
    for l in L:
        for t in T:
            m.addConstr(
                quicksum(Y_B[a, r, l, t] for a in A) <= D_B[r, l, t],
                name=f"Business_Demand_{r}_{l}_{t}"
            )

# Economy Demand Constraint: Sum(Y_E) <= D_E
for r in R:
    for l in L:
        for t in T:
            m.addConstr(
                quicksum(Y_E[a, r, l, t] for a in A) <= D_E[r, l, t],
                name=f"Economy_Demand_{r}_{l}_{t}"
            )


# Maximum Flight Movements Constraint: Sum over all a in A, r in R, l in L of X[a, r, l, t] <= Max_Flight_Movements for all t in T
Max_Flight_Movements = 100000000

for t in T:
    m.addConstr(
        quicksum(X[a, r, l, t] for a in A for r in R for l in L if (a, r, l, t) in X)
        <= Max_Flight_Movements,
        name=f"Max_Flight_Movements_{t}"
    )

# Maximum Noise Level Constraint: Sum over all a in A, r in R, l in L of Noise[a] * X[a, r, l, t] <= Max_Noise_Level for all t in T
Max_Noise_Level = 11818

for t in T:
    m.addConstr(
        quicksum(Noise[a] * X[a, r, l, t] for a in A for r in R for l in L if (a, r, l, t) in X)
        <= Max_Noise_Level,
        name=f"Max_Noise_Level_{t}"
    )


# Link W and X: if a route is flown at least once, set W to 1
for a in A:
    for r in R:
        for t in T:
            m.addConstr(
                quicksum(X[a, r, l, t] for l in L if (a, r, l, t) in X) <= big_M * W[a, r, t],
                name=f"Link_W_X_1_{a}_{r}_{t}"
            )
            m.addConstr(
                W[a, r, t] <= quicksum(X[a, r, l, t] for l in L if (a, r, l, t) in X),
                name=f"Link_W_X_2_{a}_{r}_{t}"
            )

# Minimum Frequency Constraint: If W[a,r,t] = 1, then Sum(X[a,r,l,t] for all l) >= 52
for a in A:
    for r in R:
        for t in T:
            m.addConstr(
                quicksum(X[a, r, l, t] for l in L if (a, r, l, t) in X) >= 52 * W[a, r, t],
                name=f"Min_Frequency_{a}_{r}_{t}"
            )


# ---------------------------------------------------#
#################### Model Solver ####################
# ---------------------------------------------------#


# Set a time limit (in seconds)
m.Params.TimeLimit = 300

# Set a relative optimality gap (expressed as a fraction)
m.Params.MIPGap = 0

# Optimize the model
m.optimize()


# Check the model status
if m.status == GRB.Status.INFEASIBLE or m.status == GRB.Status.INF_OR_UNBD:
    print("Model is infeasible or unbounded, computing IIS...")
    m.computeIIS()
    m.write("model.ilp")
    print("IIS written to file 'model.ilp'.")
else:
    # Print the objective function value to the terminal
    print(f'\nObjective (Maximized Profit): {m.objVal}')


    # Initialize a list to store variable data
    data_list = []
    
    # Loop through the decision variables and add to the list
    for v in m.getVars():
        data_list.append({'Variable': v.varName, 'Value': v.x})
    
    # Add the objective value
    data_list.append({'Variable': 'Objective (Maximized Profit)', 'Value': m.objVal})
    
    # Convert the list of dictionaries to a DataFrame
    df_solution = pd.DataFrame(data_list)


    # Initialize dictionaries to store total flight movements and noise levels for each period
    total_flight_movements = {}
    total_noise_levels = {}

    # Calculate total flight movements and noise levels for each time period
    for t in T:
        total_flight_movements[t] = sum(X[a, r, l, t].x for a in A for r in R for l in L if (a, r, l, t) in X)
        total_noise_levels[t] = sum(Noise[a] * X[a, r, l, t].x for a in A for r in R for l in L if (a, r, l, t) in X)

    # Print the calculated values
    print("Total Flight Movements by Period:", total_flight_movements)
    print("Total Noise Levels by Period:", total_noise_levels)

    # Add these values to the output DataFrame
    df_solution = pd.concat([df_solution, pd.DataFrame([{'Variable': f'Total Flight Movements ({t})', 'Value': total_flight_movements[t]} for t in T])]).reset_index(drop=True)
    df_solution = pd.concat([df_solution, pd.DataFrame([{'Variable': f'Total Noise Level ({t})', 'Value': total_noise_levels[t]} for t in T])]).reset_index(drop=True)


    # Save the DataFrame as a CSV file
    file_path_csv = "/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Output (CSV)/Solution.csv"
    df_solution.to_csv(file_path_csv, index=False)
        
    print(f'\nSolution saved to {file_path_csv}')


""" 
    # Save the DataFrame as an Excel file
    file_path_excel = "/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Output (CSV)/Solution.xlsx"
    df_solution.to_excel(file_path_excel, index=False, sheet_name='Solution')
        
    print(f'Solution saved to {file_path_excel}')

"""
