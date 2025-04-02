import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# endpoint for rainfall data from datagov.sg
url = "https://api-open.data.gov.sg/v2/real-time/api/rainfall"

start_date = datetime(2023, 12, 1)
end_date = datetime(2025, 1, 31)

rainfall_data = []

current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    params = {"date": date_str}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        stations = {s["id"]: s for s in data.get("data", {}).get("stations", [])}

        readings_list = data.get("data", {}).get("readings", [])
        if readings_list:
            for reading_item in readings_list:
                timestamp = reading_item.get("timestamp")
                for measurement in reading_item.get("data", []):
                    if measurement.get("stationId") == "S60":
                        station_meta = stations.get("S60", {})
                        label_location = station_meta.get("labelLocation", {})

                        rainfall_data.append({
                            "date"        : date_str,
                            "timestamp"   : timestamp,
                            "station_id"  : "S60",
                            "station_name": station_meta.get("name", "Sentosa"),
                            "rainfall"    : measurement.get("value", 0)
                        })
        else:
            print(f"No readings found for {date_str}.")

        print(f"Fetched data for {date_str}.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {date_str}: {e}")

    current_date += timedelta(days=1)

    time.sleep(0.3)

df = pd.DataFrame(rainfall_data)
if df.empty:
    print("No data found for the specified date range/station. Check the API or station ID.")
else:
    df.sort_values(by="timestamp", inplace=True)
    output_path = "../datasets/final_data/sentosa_rainfall_5min_int.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved {output_path}")
