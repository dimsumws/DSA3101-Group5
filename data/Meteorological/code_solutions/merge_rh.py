import os
import pandas as pd
import glob
import chardet
import datetime

# API endpoint for relative humidity data
url = "https://api.data.gov.sg/v1/environment/relative-humidity"

# Define date range
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 2, 22)

rh_data = []

current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")  # Format date properly
    params = {"date": date_str}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise error for bad responses
        data = response.json()

        # Extract station metadata (if available)
        stations = {s["id"]: s for s in data.get("metadata", {}).get("stations", [])}

        # Check if "items" exist
        if "items" in data:
            for item in data["items"]:
                timestamp = item.get("timestamp")
                if "readings" in item:
                    for reading in item["readings"]:
                        if reading["station_id"] == "S60":  # Filter only Sentosa station
                            rh_data.append({
                                "date": current_date,
                                "timestamp": timestamp,
                                "station_id": "S60",
                                "station_name": stations.get("S60", {}).get("name", "Sentosa"),
                                "latitude": stations.get("S60", {}).get("location", {}).get("latitude", None),
                                "longitude": stations.get("S60", {}).get("location", {}).get("longitude", None),
                                "relative_humidity": reading["value"]
                            })

        print(f"Fetched data for {current_date.strftime('%Y-%m-%d')}")  # Progress tracking

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {current_date.strftime('%Y-%m-%d')}: {e}")

    # Move to the next day
    current_date += timedelta(days=1)
    time.sleep(0.3)


df = pd.DataFrame(rh_data)
df = df.groupby(['date', 'station_id', 'station_name', 'latitude', 'longitude'])['relative_humidity'].mean().reset_index()
df['relative_humidity'] = round(df["relative_humidity"],2)

csv_file_path = "../datasets/raw_data/sentosa_relative_humidity_part6.csv"
df.to_csv(csv_filename, index=False)

# Since each GET Request is quite long, I did the data pulling in parts,
# Below is the part for merging all these files I had locally together into one master csv file
# Set the folder path to wherever the files are stored in
folder_path = "../datasets/raw_data"

files = glob.glob(os.path.join(folder_path, "*.csv"))

# Initialize an empty 
main = pd.DataFrame()


for file in files:
    df = pd.read_csv(file, dtype=str)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    if "relative_humidity" in df.columns:
        df["relative_humidity"] = pd.to_numeric(df["relative_humidity"], errors="coerce")

    main = pd.concat([main, df], ignore_index=True)

if "date" in main.columns:
    main["date"] = pd.to_datetime(main["date"], errors="coerce")

# Drop duplicate dates and sort by date
main = main.drop_duplicates(subset=["date"]).sort_values(by="date").reset_index(drop=True)

# Fill NaN values with "Unknown" for non-numeric columns
for col in main.select_dtypes(include=["object"]).columns:
    main[col].fillna("Unknown", inplace=True)

print(main.head())

main=main.rename(columns={"relative_humidity":"avg_daily_relative_humidity"})

new_folder_path = "../datasets/final_data"
output_file = os.path.join(new_folder_path, "final_merged_RH_2017_2025.csv")
main.to_csv(output_file, index=False)

print(f"Successfully saved cleaned data to {output_file}")

# next steps are to merge the RH to the main weather dataset (final_merged_weather_sentosa_data.csv) on date column to add avg daily RH 
