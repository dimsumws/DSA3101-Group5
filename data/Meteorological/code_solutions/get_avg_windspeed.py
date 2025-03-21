import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# API for windspeed data
url = "https://api-open.data.gov.sg/v2/real-time/api/wind-speed"

start_date = datetime(2016, 12, 15)
end_date = datetime(2025,2, 23)

windspeed_data = []

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
                
                # Each reading_item has a "data" list containing measurements
                for measurement in reading_item.get("data", []):
                    if measurement.get("stationId") == "S60":
                        windspeed_data.append({
                            "date": date_str,  
                            "timestamp": timestamp,
                            "station_id": "S60",
                            "station_name": stations.get("S60", {}).get("name", "Sentosa"),
                            "latitude": stations.get("S60", {}).get("location", {}).get("latitude", None),
                            "longitude": stations.get("S60", {}).get("location", {}).get("longitude", None),
                            "windspeed": measurement.get("value")
                        })
        else:
            print(f"No readings found for {date_str}.")
        
        print(f"Fetched data for {date_str}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {date_str}: {e}")

    # Move to the next day
    current_date += timedelta(days=1)

    time.sleep(0.3)

# Convert the list to a Pandas DataFrame
df = pd.DataFrame(windspeed_data)

if df.empty:
    print("No data found for the specified date range and station. Check the API response or station id.")
else:
    # Group by the desired columns, then compute the average windspeed
    df = df.groupby(['date', 'station_id', 'station_name', 'latitude', 'longitude'])['windspeed'].mean().reset_index()
    df['windspeed'] = df["windspeed"].round(2)
    csv_filename = "sentosa_avg_windspeed.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Saved {csv_filename}")
