import pandas as pd
import glob
import os

# Step 1: Set relative path

folder_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw 2024 wait time datasets")
file_paths =  glob.glob(os.path.join(folder_path, "*.csv"))

# Step 2: Load, process and filter each dataset

dataframes = []

for file in file_paths:
    df = pd.read_csv(file)
    df['Date/Time'] = pd.to_datetime(df['Date/Time'], errors='coerce') # Convert 'Date/Time' to datetime format
    df_2024 = df[df['Date/Time'].dt.year == 2024] # Filter for 2024 data only
    dataframes.append(df_2024)

# Step 3: Combine all filtered dataframes

full_dataset = pd.concat(dataframes, ignore_index=True)

# Step 4: Save combined dataset in data directory

output_folder = os.path.join(os.path.dirname(__file__), "..", "data")
output_path = os.path.join(output_folder, "combined_2024_wait_times.csv")
full_dataset.to_csv(output_path, index=False)

# Display summary

print(f"Combined dataset saved at: {output_path}")
print(f"Shape: {full_dataset.shape}")
print(full_dataset.head())