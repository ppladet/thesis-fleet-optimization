import pandas as pd
from itertools import product


# ---------------------------------------------------#
##### Part 1: Data Preprocessor for M1 Input - 1 #####
# ---------------------------------------------------#


# Load Aircraft Performance Data from Excel file
df_aircraft_performance = pd.read_excel('/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Aircraft Performance.xlsx', sheet_name = 'Aircraft Performance')

print(df_aircraft_performance)
print(df_aircraft_performance.columns)


# Load Aircraft Economics (FC) Data from Excel file
df_aircraft_economics_fc = pd.read_excel('/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Aircraft Economics (FC).xlsx', sheet_name = 'Aircraft Economics (FC)')

print(df_aircraft_economics_fc)
print(df_aircraft_economics_fc.columns)


# Create an empty DataFrame called df_merge_performance_fc
df_merge_performance_fc = pd.DataFrame()

# Create a new column called "Aircraft Type" in df_merge_performance_fc
df_merge_performance_fc["Aircraft Type"] = df_aircraft_economics_fc["Aircraft Type"] + " | " + df_aircraft_economics_fc["Adjusted Age (Years)"].astype(str)


# Define additional metrics
def generate_entries(prefix, count):
    return [f'{prefix}{i}' for i in range(1, count + 1)]

# Set the count for aircraft units
aircraft_units_count = 50

# Generate aircraft units using the function
aircraft_units = generate_entries('U', aircraft_units_count)

# Expand the DataFrame by adding an Aircraft Unit column
df_merge_performance_fc = pd.concat([df_merge_performance_fc.assign(**{'Aircraft Unit': unit}) for unit in aircraft_units], ignore_index=True)


# Create a temporary key in df_merge_performance_fc that ignores the age information
df_merge_performance_fc["temp_key"] = df_merge_performance_fc["Aircraft Type"].apply(lambda x: x.split(' | ')[0])

# Create a temporary key in df_aircraft_performance that matches the one in df_merge_performance_fc
df_aircraft_performance["temp_key"] = df_aircraft_performance["Aircraft Type"]

# Define the columns to be added to df_merge_performance_fc
columns_to_add = ["Capacity Business", "Capacity Economy", "Cruise Speed (km/h)", "Range (km)", "Noise (EPNL - Adjusted)", "Max Flight Minutes", "Turnaround Time (Minutes)"]

# Add the columns to df_merge_performance_fc by merging with df_aircraft_performance
df_merge_performance_fc = pd.merge(df_merge_performance_fc, df_aircraft_performance[["temp_key"] + columns_to_add], on="temp_key", how="left")

# Remove the temporary keys
df_aircraft_performance.drop("temp_key", axis=1, inplace=True)
df_merge_performance_fc.drop("temp_key", axis=1, inplace=True)


# Create a temporary key in df_aircraft_economics_fc that matches the "Aircraft Type" in df_merge_performance_fc
df_aircraft_economics_fc["temp_key"] = df_aircraft_economics_fc["Aircraft Type"] + " | " + df_aircraft_economics_fc["Adjusted Age (Years)"].astype(str)

# Add the "Fixed Costs (USD)" column to df_merge_performance_fc by merging with df_aircraft_economics_fc
df_merge_performance_fc = pd.merge(df_merge_performance_fc, df_aircraft_economics_fc[["temp_key", "Fixed Costs (USD)"]], left_on="Aircraft Type", right_on="temp_key", how="left")

# Remove the temporary keys
df_aircraft_economics_fc.drop("temp_key", axis=1, inplace=True)
df_merge_performance_fc.drop("temp_key", axis=1, inplace=True)

print(df_merge_performance_fc)
print(df_merge_performance_fc.columns)


# Load Demand Data from Excel file (Simulated - 1 or Simulated - 2 for Different Demand Scenarios)
df_demand_data = pd.read_excel('/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Demand Data (Simulated - 2).xlsx', sheet_name = 'Demand Data (Annual)')

print(df_demand_data)


# Create a new DataFrame that is the cartesian product of df_merge_performance_fc and df_demand_data
df_merge_performance_fc = pd.concat([df_merge_performance_fc.assign(**dict(zip(df_demand_data.columns, x))) for x in df_demand_data.values])

# Define the new column order
new_column_order = ['Aircraft Type', 'Aircraft Unit', 'Route', 'Distance (km)', 'P_B', 'P_E', 'D_B', 'D_E', 
                    'Capacity Business', 'Capacity Economy', 'Cruise Speed (km/h)', 'Range (km)', 'Noise (EPNL - Adjusted)', 'Max Flight Minutes', 
                    'Turnaround Time (Minutes)', 'Fixed Costs (USD)']

# Rearrange the columns in df_merge_performance_fc
df_merge_performance_fc = df_merge_performance_fc[new_column_order]

print(df_merge_performance_fc)
print(df_merge_performance_fc.columns)


# Define additional metrics (Flight Leg, Flight Number, Period)
n_count = 1
t_count = 1

additional_metrics = {
    'Flight Leg': ['Outbound', 'Inbound'],
    'Flight Number': generate_entries('N', n_count),
    'Period': generate_entries('T', t_count)
}

# Create a DataFrame that is the cartesian product of the additional metrics
df_additional_metrics = pd.DataFrame(list(product(*additional_metrics.values())), columns=additional_metrics.keys())

# Create a new DataFrame that is the cartesian product of df_merge_performance_fc and df_additional_metrics
df_merge_performance_fc = pd.concat([df_merge_performance_fc.assign(**dict(zip(df_additional_metrics.columns, x))) for _, x in df_additional_metrics.iterrows()], ignore_index=True)

# Define the new column order
new_column_order = ['Aircraft Type', 'Aircraft Unit', 'Route', 'Flight Leg', 'Flight Number', 'Period', 'Distance (km)', 'P_B', 'P_E', 'D_B', 'D_E', 
                    'Capacity Business', 'Capacity Economy', 'Cruise Speed (km/h)', 'Range (km)', 'Noise (EPNL - Adjusted)', 'Max Flight Minutes', 
                    'Turnaround Time (Minutes)', 'Fixed Costs (USD)']

# Rearrange the columns in df_merge_performance_fc
df_merge_performance_fc = df_merge_performance_fc[new_column_order]

print(df_merge_performance_fc)
print(df_merge_performance_fc.columns)


# Load Aircraft Economics (AC) Data from Excel file
df_aircraft_economics_ac = pd.read_excel('/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Aircraft Economics (AC).xlsx', sheet_name = 'Aircraft Economics (AC)')

print(df_aircraft_economics_ac)
print(df_aircraft_economics_ac.columns)


# Create a temporary key in df_aircraft_economics_ac that combines Aircraft Type and Distance
df_aircraft_economics_ac["temp_key"] = df_aircraft_economics_ac["Aircraft Type"].astype(str) + " | " + df_aircraft_economics_ac["Distance (km)"].astype(str)

# Create a similar key in df_merge_performance_fc
df_merge_performance_fc["temp_key"] = df_merge_performance_fc["Aircraft Type"].apply(lambda x: x.split(' | ')[0]) + " | " + df_merge_performance_fc["Distance (km)"].astype(str)

# Add the "Active Costs (USD)" column to df_merge_performance_fc by merging with df_aircraft_economics_ac
df_merge_performance_fc = pd.merge(df_merge_performance_fc, df_aircraft_economics_ac[["temp_key", "Active Costs (USD)"]], on="temp_key", how="left")

# Remove the temporary keys
df_aircraft_economics_ac.drop("temp_key", axis=1, inplace=True)
df_merge_performance_fc.drop("temp_key", axis=1, inplace=True)

# Create/Rename df_merge_performance_fc to df_merge_performance_fc_ac for Clarity
df_merge_performance_fc_ac = df_merge_performance_fc


# Calculate the "Flight Time (Minutes)" and insert it after the "Distance (km)" column
df_merge_performance_fc_ac["Flight Time (Minutes)"] = (df_merge_performance_fc_ac["Distance (km)"] / df_merge_performance_fc_ac["Cruise Speed (km/h)"]) * 60

# Define the new column order
new_column_order = ['Aircraft Type', 'Aircraft Unit', 'Route', 'Flight Leg', 'Flight Number', 'Period', 'Distance (km)', 'Flight Time (Minutes)', 'P_B', 'P_E', 'D_B', 'D_E', 
                    'Capacity Business', 'Capacity Economy', 'Cruise Speed (km/h)', 'Range (km)', 'Noise (EPNL - Adjusted)', 'Max Flight Minutes', 
                    'Turnaround Time (Minutes)', 'Active Costs (USD)', 'Fixed Costs (USD)']

# Rearrange the columns in df_merge_performance_fc
df_merge_performance_fc_ac = df_merge_performance_fc_ac[new_column_order]

print(df_merge_performance_fc_ac)
print(df_merge_performance_fc_ac.columns)


# Create a path for the output CSV file
output_file_path = '/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Input (CSV)/M1 Input - 1.csv'

# Write df_merge_performance_fc_ac to a CSV file
df_merge_performance_fc_ac.to_csv(output_file_path, index=False)

print(f"\nData has been written to '{output_file_path}'.")


""" 
# Create a path for the output file
output_file_path = '/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Input (CSV)/M1 Input - 1.xlsx'

# Create a writer object
writer = pd.ExcelWriter(output_file_path, engine='xlsxwriter')

# Write df_merge_performance_fc to an Excel file
df_merge_performance_fc_ac.to_excel(writer, sheet_name='M1 Input - 1', index=False)

# Save the Excel file
writer.save()

print(f"\nData has been written to '{output_file_path}'.")
"""


# ---------------------------------------------------#
##### Part 2: Data Preprocessor for M1 Input - 2 #####
# ---------------------------------------------------#


# Load M1 Input - 1 Data from Excel file
df_m1_input_2 = pd.read_csv('/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Input (CSV)/M1 Input - 1.csv')


# Create a new column "Aircraft Type - Identifier" as a merge of "Aircraft Type" and "Aircraft Unit"
df_m1_input_2["Aircraft Type - Identifier"] = df_m1_input_2["Aircraft Type"] + " | " + df_m1_input_2["Aircraft Unit"]

# Drop the original columns "Aircraft Type" and "Aircraft Unit"
df_m1_input_2.drop(["Aircraft Type", "Aircraft Unit"], axis=1, inplace=True)

# Reorder columns to make "Aircraft Type - Identifier" the first column
cols = ["Aircraft Type - Identifier"] + [col for col in df_m1_input_2.columns if col != "Aircraft Type - Identifier"]
df_m1_input_2 = df_m1_input_2[cols]


# Calculate the new column "Fixed Costs - Active (USD)" = (Fixed Costs (USD) / 525600) * (Flight Time (Minutes) + Turnaround Time (Minutes))
total_minutes_in_year = 525600

df_m1_input_2['Fixed Costs - Active (USD)'] = (df_m1_input_2['Fixed Costs (USD)'] / total_minutes_in_year) * \
                                                     (df_m1_input_2['Flight Time (Minutes)'] + df_m1_input_2['Turnaround Time (Minutes)'])

print(df_m1_input_2)
print(df_m1_input_2.columns)


# Create a path for the output CSV file
output_file_path = '/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Input (CSV)/M1 Input - 2.csv'

# Write df_m1_input_2 to a CSV file
df_m1_input_2.to_csv(output_file_path, index=False)

print(f"\nData has been written to '{output_file_path}'.")


""" 
# Create a path for the output file
output_file_path = '/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Input (CSV)/M1 Input - 2.xlsx'

# Create a writer object
writer = pd.ExcelWriter(output_file_path, engine='xlsxwriter')

# Write df_merge_performance_fc to an Excel file
df_m1_input_2.to_excel(writer, sheet_name='M1 Input - 2', index=False)

# Save the Excel file
writer.save()

print(f"\nData has been written to '{output_file_path}'.")
"""
