import os
import pandas as pd
import numpy as np
import glob
import chardet

folder_path = "../datasets/raw_data/daily_data_sentosa"
destination_path = "../datasets/final_data"
files = glob.glob(os.path.join(folder_path, "*.csv"))

if not files:
    raise ValueError("No CSV files found in the specified folder.")

main = pd.DataFrame()

def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        return chardet.detect(f.read(100000))["encoding"]

file_count = 0
for file in files:
    encoding = detect_encoding(file)
    try:
        df = pd.read_csv(file, encoding=encoding, on_bad_lines="skip", dtype=str)
        file_count += 1
    except UnicodeDecodeError:
        continue
    df.fillna("Unknown", inplace=True)
    if all(col in df.columns for col in ["Year", "Month", "Day"]):
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
        df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
        df["Day"] = pd.to_numeric(df["Day"], errors="coerce")
        df["Date"] = pd.to_datetime(df[["Year", "Month", "Day"]], errors="coerce")
        if df["Date"].isna().sum() == 0:
            df.drop(columns=["Year", "Month", "Day"], inplace=True)
    else:
        continue
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    main = pd.concat([main, df], ignore_index=True)

if file_count == 0:
    raise ValueError("No files were successfully read.")
if "Date" not in main.columns:
    raise ValueError("Error: 'Date' column was not created.")

main["Date"] = pd.to_datetime(main["Date"], errors="coerce")
if "Station" in main.columns:
    main.drop(columns=["Station"], errors="ignore", inplace=True)
main.replace("-", 0, inplace=True)
first_column = main.pop("Date")
main.insert(0, "Date", first_column)
pairs = [("Highest 30 Min Rainfall (mm)", "Highest 30 min Rainfall (mm)"),
         ("Highest 60 Min Rainfall (mm)", "Highest 60 min Rainfall (mm)"),
         ("Highest 120 Min Rainfall (mm)", "Highest 120 min Rainfall (mm)")]
for col_upper, col_lower in pairs:
    if col_upper in main.columns and col_lower in main.columns:
        main[col_upper] = main[col_upper].combine_first(main[col_lower])
        main.drop(columns=[col_lower], inplace=True)

num_cols = main.select_dtypes(include=["number"]).columns.tolist()
main[num_cols] = main[num_cols].fillna(0)
main[num_cols] = main[num_cols].round(1)
main.fillna(0, inplace=True)
numeric_cols = [c for c in main.select_dtypes(include=["number"]).columns if c != "Date"]
sparse_mask = (main[numeric_cols] == 0).sum(axis=1) / len(numeric_cols) > 0.85
synthetic_dist = {}
non_sparse = main[~sparse_mask]
for col in numeric_cols:
    valid_vals = non_sparse.loc[non_sparse[col] != 0, col]
    if not valid_vals.empty:
        synthetic_dist[col] = valid_vals.values
    else:
        synthetic_dist[col] = None
for idx in main[sparse_mask].index:
    for col in numeric_cols:
        if main.at[idx, col] == 0 and synthetic_dist[col] is not None:
            v = np.random.choice(synthetic_dist[col])
            main.at[idx, col] = round(v, 1)
main[num_cols] = main[num_cols].round(1)
wind_cols = ["Mean Wind Speed (km/h)", "Max Wind Speed (km/h)"]
if all(w in main.columns for w in wind_cols):
    both_zero_mask = (main[wind_cols[0]] == 0) & (main[wind_cols[1]] == 0)
    for idx in main[both_zero_mask].index:
        d = main.at[idx, "Date"]
        if pd.notnull(d):
            same_md = (main["Date"].dt.month == d.month) & (main["Date"].dt.day == d.day) & ~both_zero_mask
            subset = main.loc[same_md, wind_cols]
            if not subset.empty:
                row_sample = subset.sample(1)
                main.at[idx, wind_cols[0]] = round(row_sample[wind_cols[0]].values[0], 1)
                main.at[idx, wind_cols[1]] = round(row_sample[wind_cols[1]].values[0], 1)
main[num_cols] = main[num_cols].round(1)
output_file = os.path.join(destination_path, "final_augmented_weather_sentosa_data.csv")
main.to_csv(output_file, index=False)
print(f"Cleaned data saved to: {output_file}")
