import pandas as pd
import os

# Step 1: Load CSV and check for missing values

data_path = os.path.join(os.path.dirname(__file__), "..", "data", "comnbined_2024_wait_times.csv")  
df = pd.read_csv(data_path)
print("Missing Values Before Cleaning:\n",df.isnull().sum())

# Step 2: Reformat data

df['Date/Time'] = pd.to_datetime(df['Date/Time'], errors='coerce')
df['date'] = df['Date/Time'].dt.date # Extract date (YYYY-MM-DD)
df['time'] = df['Date/Time'].dt.time # Extract time (HH:MM:SS)
df.drop(columns=['Date/Time'], inplace=True)
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df['wait_time'] = pd.to_numeric(df['wait_time'], errors='coerce')
df['wait_time'] = df['wait_time'].astype(int)

# Step 3: Sort data according to date and time

df = df.sort_values(by=['date', 'time'], ascending=True).reset_index(drop=True)
print(df.info())
print(df.head())

# Step 4: Save new CSV file in data directory

output_folder = os.path.join(os.path.dirname(__file__), "..", "data", "clean data")
output_path = os.path.join(output_folder, "cleaned_2024_wait_times.csv")
df.to_csv(output_path, index=False)