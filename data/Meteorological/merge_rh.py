import os
import pandas as pd
import glob
import chardet

# Set the folder path where the CSV files are stored
folder_path = r"C:\Users\ninod\sentosa_avg_rh"

files = glob.glob(os.path.join(folder_path, "*.csv"))

# Initialize an empty 
main = pd.DataFrame()


for file in files:
    df = pd.read_csv(file, dtype=str)  # Read all as strings to avoid loss

    # Convert 'date' column to datetime format safely
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    if "relative_humidity" in df.columns:
        df["relative_humidity"] = pd.to_numeric(df["relative_humidity"], errors="coerce")

    # Append to main DataFrame
    main = pd.concat([main, df], ignore_index=True)

# Convert Date column to datetime datatype after merging
if "date" in main.columns:
    main["date"] = pd.to_datetime(main["date"], errors="coerce")

# Drop duplicate dates and sort by date
main = main.drop_duplicates(subset=["date"]).sort_values(by="date").reset_index(drop=True)

# Fill NaN values with "Unknown" for non-numeric columns
for col in main.select_dtypes(include=["object"]).columns:
    main[col].fillna("Unknown", inplace=True)

print(main.head())

main=main.rename(columns={"relative_humidity":"avg_daily_relative_humidity"})

# Save the final cleaned dataset
output_file = os.path.join(folder_path, "final_merged_RH_2017_2025.csv")
main.to_csv(output_file, index=False)

print(f"Successfully saved cleaned data to {output_file}")

# next steps are to merge the  RH to the main weather dataset on date column to add avg daily RH 
