import pandas as pd
import random
import json
import os

pd.set_option('display.max_columns', None)

# Load materials from the CSV
materials_df = pd.read_csv('datasets/U-value marcos.csv')

# Convert columns to appropriate data types
materials_df['density'] = materials_df['density'].astype(float)
materials_df['min_thickness'] = materials_df['min_thickness'].astype(float)
materials_df['max_thickness'] = materials_df['max_thickness'].astype(float)
materials_df['conductivity'] = materials_df['conductivity'].astype(float)
materials_df['embodied_carbon_coefficient'] = materials_df['embodied_carbon_coefficient'].astype(float)
materials_df['cost'] = materials_df['cost'].astype(float)

# Function to create a wall with unique properties
def create_wall(wall_id, total_wall_area, wall_options, materials_df, outside_temp, inside_temp):
    wall_type = random.choice(wall_options)
    wall = {
        'wall_id': wall_id,
        'materials': [],
        'total_thickness': 0,
        'total_r_value': 0,
        'total_u_value': 0,
        'total_embodied_carbon': 0,
        'heat_transfer': 0,
        'total_cost': 0
    }

    for material_type in wall_type:
        filtered_materials = materials_df[materials_df['material type'] == material_type]
        selected_material = filtered_materials.sample().iloc[0]
        material_thickness = round(random.uniform(selected_material['min_thickness'], selected_material['max_thickness']), 3)
        r_value = round(material_thickness / selected_material['conductivity'], 3)
        u_value = round(1 / r_value, 3)

        material_data = {
            'material': selected_material['material'],
            'thickness': material_thickness,
            'density': selected_material['density'],
            'conductivity': selected_material['conductivity'],
            'u_value': u_value,
            'embodied_carbon_coefficient': selected_material['embodied_carbon_coefficient'],
            'cost': selected_material['cost'],
            'recyclability': selected_material['recyclability'],
            'bio_based': selected_material['bio_based'],
            'color': selected_material['colour']
        }

        wall['materials'].append(material_data)
        wall['total_thickness'] = round(wall['total_thickness'] + material_thickness, 3)
        wall['total_r_value'] = round(wall['total_r_value'] + r_value, 3)
        wall['total_u_value'] = round(wall['total_u_value'] + u_value, 3)
        wall['total_embodied_carbon'] = round(wall['total_embodied_carbon'] + material_thickness * total_wall_area * selected_material['density'] * selected_material['embodied_carbon_coefficient'], 3)
        wall['heat_transfer'] = round((outside_temp - inside_temp) / wall['total_r_value'], 3)
        wall['total_cost'] = round(wall['total_cost'] + selected_material['cost'] * total_wall_area, 3)

    return wall

# Get user inputs
num_walls = int(input("Enter the number of walls to be made: "))
total_wall_area = float(input("Enter the total wall area: "))
outside_temp = float(input("Enter the outside temp: "))
inside_temp = float(input("Enter the inside temp: "))

wall_population = []
wall_options = [
    ['finishing', 'insulation', 'structure', 'finishing'],
    ['finishing', 'insulation', 'finishing'],
    #['glass'],
    ['facade', 'insulation', 'finishing']
]

# Create unique walls
while len(wall_population) < num_walls:
    new_wall = create_wall(len(wall_population) + 1, total_wall_area, wall_options, materials_df, outside_temp, inside_temp)
    if new_wall['total_thickness'] <= 0.300 and new_wall not in wall_population:
        wall_population.append(new_wall)

# Create a DataFrame from the wall population
wall_population_df = pd.DataFrame(wall_population)

# Print the DataFrame
print(wall_population_df.head().to_string())

# Save the DataFrame to a CSV file
'''path = "datasets"
wall_population_df.to_csv(os.path.join(path,r'wall_population.csv'), index=False)'''

# Ensure the DataFrame columns are appropriately converted to native Python data types
def convert_types(df):
    df['wall_id'] = df['wall_id'].astype(int)
    df['total_thickness'] = df['total_thickness'].astype(float)
    df['total_r_value'] = df['total_r_value'].astype(float)
    df['total_u_value'] = df['total_u_value'].astype(float)
    df['total_embodied_carbon'] = df['total_embodied_carbon'].astype(float)
    df['heat_transfer'] = df['heat_transfer'].astype(float)
    df['total_cost'] = df['total_cost'].astype(float)
    return df


wall_population_df = convert_types(wall_population_df)


# Function to convert DataFrame to JSON format
def dataframe_to_json(df):
    json_list = []

    for _, row in df.iterrows():
        materials_list = row['materials']

        # Ensure that all materials are dictionaries with appropriate types
        processed_materials = [
            {
                "material": material["material"],
                "thickness": float(material["thickness"]),
                "density": float(material["density"]),
                "conductivity": float(material["conductivity"]),
                "u_value": float(material["u_value"]),
                "embodied_carbon_coefficient": float(material["embodied_carbon_coefficient"]),
                "cost": float(material["cost"]),
                "recyclability": int(material["recyclability"]),
                "bio_based": bool(material["bio_based"]),
                "color": material["color"]
            }
            for material in materials_list
        ]

        json_row = {
            "wall_id": int(row['wall_id']),
            "materials": processed_materials,
            "total_thickness": float(row['total_thickness']),
            "total_r_value": float(row['total_r_value']),
            "total_u_value": float(row['total_u_value']),
            "total_embodied_carbon": float(row['total_embodied_carbon']),
            "heat_transfer": float(row['heat_transfer']),
            "total_cost": float(row['total_cost'])
        }
        json_list.append(json_row)

    return json_list


# Convert DataFrame to JSON
json_data = dataframe_to_json(wall_population_df)

# Save JSON to a file
with open('wall_population.json', 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

print("DataFrame successfully converted to JSON file.")