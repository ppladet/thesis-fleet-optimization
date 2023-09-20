import pandas as pd
from itertools import product


# ---------------------------------------------------#
##### Part 1: Output Processor for M1 Output - 1 #####
# ---------------------------------------------------#


# Load Solution Output Data from Excel file
df_solution_output = pd.read_csv('/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Output (CSV)/Solution.csv')

print(df_solution_output)
print(df_solution_output.columns)


# Function to determine the new "Data" column value based on the "Variable" column
def determine_data_type(variable):
    if variable.startswith("X"):
        return "Number of Flights"
    elif variable.startswith("Y_B"):
        return "PAX Business"
    elif variable.startswith("Y_E"):
        return "PAX Economy"
    elif variable.startswith("Z"):
        return "Aircraft Activity Status"
    elif variable.startswith("W"):
        return "Route Activity Status"
    elif variable.startswith("Idle"):
        return "Idle Time (Minutes)"
    elif variable.startswith("Objective"):
        return "Objective Value"
    else:
        return "Unknown"

# Add new "Data" column to df_solution_output
df_solution_output['Data'] = df_solution_output['Variable'].apply(determine_data_type)


# Function to extract the unique aircraft identifier from the "Variable" column
def extract_unique_aircraft_identifier(row):
    if row['Data'] == 'Number of Flights':
        parts = row['Variable'].split('_')
        return '_'.join(parts[1:-3])  # Joining all parts except the first and last three
    elif row['Data'] in ['PAX Business', 'PAX Economy', 'Idle Time (Minutes)', 'Aircraft Activity Status', 'Route Activity Status']:
        start_idx = row['Variable'].find('[') + 1
        end_idx = row['Variable'].find(',', start_idx)
        return row['Variable'][start_idx:end_idx]
    elif row['Data'] == 'Objective Value':
        return None  # Assuming no identifier for Objective Value
    else:
        return None

# Add new "Unique Aircraft Identifier" column to df_solution_output
df_solution_output['Unique Aircraft Identifier'] = df_solution_output.apply(extract_unique_aircraft_identifier, axis=1)


# Function to extract aircraft details from the "Unique Aircraft Identifier" column
def extract_aircraft_details(row):
    if row['Unique Aircraft Identifier'] is not None:
        parts = row['Unique Aircraft Identifier'].split('|')
        if len(parts) >= 3:
            aircraft_type = parts[0].strip()
            aircraft_age = parts[1].strip()
            aircraft_unit = parts[2].strip()
            return aircraft_type, aircraft_age, aircraft_unit
    return None, None, None

# Apply the function to create new columns for "Aircraft Type", "Aircraft Age", and "Aircraft Unit"
df_solution_output['Aircraft Type'], df_solution_output['Aircraft Age'], df_solution_output['Aircraft Unit'] = zip(*df_solution_output.apply(extract_aircraft_details, axis=1))


# Function to extract the route from the "Variable" column
def extract_route(row):
    if row['Data'] == 'Number of Flights':
        last_idx = row['Variable'].rfind('_')
        second_last_idx = row['Variable'].rfind('_', 0, last_idx)
        third_last_idx = row['Variable'].rfind('_', 0, second_last_idx)
        return row['Variable'][third_last_idx+1:second_last_idx]
    elif row['Data'] in ['PAX Business', 'PAX Economy', 'Route Activity Status']:
        start_idx = row['Variable'].find(',') + 1
        end_idx = row['Variable'].find(',', start_idx)
        return row['Variable'][start_idx:end_idx].strip()
    elif row['Data'] == 'Idle Time (Minutes)':
        return None
    else:
        return None

# Add new "Route" column to df_solution_output
df_solution_output['Route'] = df_solution_output.apply(extract_route, axis=1)


# Function to extract the flight leg from the "Variable" column
def extract_flight_leg(row):
    if "Outbound" in row['Variable']:
        return "Outbound"
    elif "Inbound" in row['Variable']:
        return "Inbound"
    else:
        return None

# Add new "Flight Leg" column to df_solution_output
df_solution_output['Flight Leg'] = df_solution_output.apply(extract_flight_leg, axis=1)


# Function to extract the period from the "Variable" column
def extract_period(row):
    if row['Data'] == 'Number of Flights':
        last_part = row['Variable'].split('_')[-1]
        return ''.join(filter(str.isdigit, last_part))
    elif row['Data'] in ['PAX Business', 'PAX Economy', 'Route Activity Status']:
        last_idx = row['Variable'].rfind('T')
        if row['Variable'].endswith(']'):
            return ''.join(filter(str.isdigit, row['Variable'][last_idx+1:-1]))
        else:
            return ''.join(filter(str.isdigit, row['Variable'][last_idx+1:]))
    else:
        return None

# Add new "Period" column to df_solution_output
df_solution_output['Period'] = df_solution_output.apply(extract_period, axis=1)


# Drop the "Variable" column
df_solution_output.drop(columns=['Variable'], inplace=True)

# Rearrange columns
df_solution_output = df_solution_output[['Data', 'Unique Aircraft Identifier', 'Aircraft Type', 'Aircraft Age', 'Aircraft Unit', 'Route', 'Flight Leg', 'Period', 'Value']]

print(df_solution_output)
print(df_solution_output.columns)


# Create a path for the output CSV file
output_file_path = '/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Output (Processed)/M1 Output - 1 (Processed).csv'

# Write df_solution_output to a CSV file
df_solution_output.to_csv(output_file_path, index=False)

print(f"\nData has been written to '{output_file_path}'.")


""" 
# Create a path for the output file
output_file_path = '/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Output (Processed)/M1 Output - 1 (Processed).xlsx'

# Create a writer object
writer = pd.ExcelWriter(output_file_path, engine='xlsxwriter')

# Write df_solution_output to an Excel file
df_solution_output.to_excel(writer, sheet_name='M1 Output - 1 (Processed)', index=False)

# Save the Excel file
writer.save()

print(f"\nData has been written to '{output_file_path}'.")

"""


# ---------------------------------------------------#
##### Part 2: Output Processor for M1 Output - 2 #####
# ---------------------------------------------------#


# Load M1 Output - 1 Data from Excel file
df_solution_output_processed = pd.read_csv('/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Output (Processed)/M1 Output - 1 (Processed).csv')

print(df_solution_output_processed)
print(df_solution_output_processed.columns)


# Create a new DataFrame that only contains the rows where "Data" is "Aircraft Activity Status"
df_activity_status = df_solution_output_processed[df_solution_output_processed['Data'] == 'Aircraft Activity Status']

# Create a dictionary that maps "Unique Aircraft Identifier" to "Value" for these rows
activity_status_dict = df_activity_status.set_index('Unique Aircraft Identifier')['Value'].to_dict()

# Add a new column "Activity Status" to the original DataFrame: This new column will have the "Value" from "Aircraft Activity Status" rows for each "Unique Aircraft Identifier"
df_solution_output_processed['Activity Status'] = df_solution_output_processed['Unique Aircraft Identifier'].map(activity_status_dict)

# Remove rows where the 'Data' column is 'Aircraft Activity Status'
df_solution_output_processed = df_solution_output_processed[df_solution_output_processed['Data'] != 'Aircraft Activity Status']


# Create a new DataFrame that only contains the rows where "Data" is "Idle Time (Minutes)"
df_idle_time = df_solution_output_processed[df_solution_output_processed['Data'] == 'Idle Time (Minutes)']

# Create a dictionary that maps "Unique Aircraft Identifier" to "Value" for these rows
idle_time_dict = df_idle_time.set_index('Unique Aircraft Identifier')['Value'].to_dict()

# Add a new column "Idle Time (Minutes)" to the original DataFrame: This new column will have the "Value" from "Idle Time (Minutes)" rows for each "Unique Aircraft Identifier"
df_solution_output_processed['Idle Time (Minutes)'] = df_solution_output_processed['Unique Aircraft Identifier'].map(idle_time_dict)

# Remove rows where the 'Data' column is 'Idle Time (Minutes)'
df_solution_output_processed = df_solution_output_processed[df_solution_output_processed['Data'] != 'Idle Time (Minutes)']


# Create a concatenated column in the original DataFrame as a unique key for merging
df_solution_output_processed['Concat_Key'] = df_solution_output_processed['Unique Aircraft Identifier'].astype(str) + "_" + \
                                              df_solution_output_processed['Route'].astype(str) + "_" + \
                                              df_solution_output_processed['Flight Leg'].astype(str) + "_" + \
                                              df_solution_output_processed['Period'].astype(str)

# Filter rows where 'Data' is 'PAX Business' and create the same concatenated column
df_pax_business = df_solution_output_processed[df_solution_output_processed['Data'] == 'PAX Business']
df_pax_business['Concat_Key'] = df_pax_business['Unique Aircraft Identifier'].astype(str) + "_" + \
                                 df_pax_business['Route'].astype(str) + "_" + \
                                 df_pax_business['Flight Leg'].astype(str) + "_" + \
                                 df_pax_business['Period'].astype(str)

# Create a dictionary that maps 'Concat_Key' to 'Value' for these rows
pax_business_dict = df_pax_business.set_index('Concat_Key')['Value'].to_dict()

# Add a new column 'PAX Business' to the original DataFrame: This new column will have the 'Value' from 'PAX Business' rows for each 'Concat_Key'
df_solution_output_processed['PAX Business'] = df_solution_output_processed['Concat_Key'].map(pax_business_dict)

# Remove rows where the 'Data' column is 'PAX Business'
df_solution_output_processed = df_solution_output_processed[df_solution_output_processed['Data'] != 'PAX Business']

# Remove the 'Concat_Key' column
df_solution_output_processed.drop('Concat_Key', axis=1, inplace=True)


# Create a concatenated column in the original DataFrame as a unique key for merging
df_solution_output_processed['Concat_Key'] = df_solution_output_processed['Unique Aircraft Identifier'].astype(str) + "_" + \
                                              df_solution_output_processed['Route'].astype(str) + "_" + \
                                              df_solution_output_processed['Flight Leg'].astype(str) + "_" + \
                                              df_solution_output_processed['Period'].astype(str)

# Filter rows where 'Data' is 'PAX Economy' and create the same concatenated column
df_pax_economy = df_solution_output_processed[df_solution_output_processed['Data'] == 'PAX Economy']
df_pax_economy['Concat_Key'] = df_pax_economy['Unique Aircraft Identifier'].astype(str) + "_" + \
                                 df_pax_economy['Route'].astype(str) + "_" + \
                                 df_pax_economy['Flight Leg'].astype(str) + "_" + \
                                 df_pax_economy['Period'].astype(str)

# Create a dictionary that maps 'Concat_Key' to 'Value' for these rows
pax_economy_dict = df_pax_economy.set_index('Concat_Key')['Value'].to_dict()

# Add a new column 'PAX Economy' to the original DataFrame: This new column will have the 'Value' from 'PAX Economy' rows for each 'Concat_Key'
df_solution_output_processed['PAX Economy'] = df_solution_output_processed['Concat_Key'].map(pax_economy_dict)

# Remove rows where the 'Data' column is 'PAX Economy'
df_solution_output_processed = df_solution_output_processed[df_solution_output_processed['Data'] != 'PAX Economy']

# Remove the 'Concat_Key' column
df_solution_output_processed.drop('Concat_Key', axis=1, inplace=True)


# Drop rows where 'Activity Status' is 0
df_solution_output_processed = df_solution_output_processed[df_solution_output_processed['Activity Status'] != 0]

# Rearrange columns
df_solution_output_processed = df_solution_output_processed[['Activity Status', 'Idle Time (Minutes)', 'PAX Business', 'PAX Economy', 'Data', 'Unique Aircraft Identifier', 'Aircraft Type', 'Aircraft Age', 'Aircraft Unit', 'Route', 'Flight Leg', 'Period', 'Value']]

print(df_solution_output_processed)
print(df_solution_output_processed.columns)


# Create a path for the output CSV file
output_file_path = '/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Output (Processed)/M1 Output - 2 (Processed).csv'

# Write df_solution_output to a CSV file
df_solution_output_processed.to_csv(output_file_path, index=False)

print(f"\nData has been written to '{output_file_path}'.")


# Create a path for the output file
output_file_path = '/Users/ppladet/Desktop/RSM BAM/Courses/Spring Semester/Thesis/Master Thesis/Data/Model Output (Processed)/M1 Output - 2 (Processed).xlsx'

# Create a writer object
writer = pd.ExcelWriter(output_file_path, engine='xlsxwriter')

# Write df_solution_output to an Excel file
df_solution_output_processed.to_excel(writer, sheet_name='M1 Output - 2 (Processed)', index=False)

# Save the Excel file
writer.save()

print(f"\nData has been written to '{output_file_path}'.")
