import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json

# API endpoint
url = "https://api-open.data.gov.sg/v2/real-time/api/twenty-four-hr-forecast"

# Define date range
start_date = datetime(2016, 6, 2)
end_date = datetime(2025, 2, 22)

# Initialize list to store data
all_data = []

# Iterate through each date in the range
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")  # Format date as YYYY-MM-DD
    params = {"date": date_str}

    try:
        # Send GET request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes

        # Parse response JSON
        data = response.json()
        
        # Extract necessary fields
        if "data" in data and "records" in data["data"] and len(data["data"]["records"]) > 0:
            for record in data["data"]["records"]:
                # Extract general weather details
                general = record.get("general", {})
                temperature = general.get("temperature", {})
                humidity = general.get("relativeHumidity", {})
                wind = general.get("wind", {})
                forecast = general.get("forecast", {})

                # Extract valid period
                valid_period = general.get("validPeriod", {})
                valid_start = valid_period.get("start", "")
                valid_end = valid_period.get("end", "")

                # Extract wind details
                wind_speed = wind.get("speed", {})
                wind_direction = wind.get("direction", "")

                for period in record.get("periods", []):
                    time_period = period.get("timePeriod", {})
                    start_time = time_period.get("start", "")
                    end_time = time_period.get("end", "")
                    time_text = time_period.get("text", "")

                    regions = period.get("regions", {})
                    all_data.append({
                        "date": record.get("date", date_str),
                        "valid_start": valid_start,
                        "valid_end": valid_end,
                        "temperature_low": temperature.get("low"),
                        "temperature_high": temperature.get("high"),
                        "humidity_low": humidity.get("low"),
                        "humidity_high": humidity.get("high"),
                        "wind_speed_low": wind_speed.get("low"),
                        "wind_speed_high": wind_speed.get("high"),
                        "wind_direction": wind_direction,
                        "forecast_code": forecast.get("code"),
                        "forecast_text": forecast.get("text"),
                        "time_period_start": start_time,
                        "time_period_end": end_time,
                        "time_period_text": time_text,
                        "region_west": regions.get("west", {}).get("text"),
                        "region_east": regions.get("east", {}).get("text"),
                        "region_central": regions.get("central", {}).get("text"),
                        "region_south": regions.get("south", {}).get("text"),
                        "region_north": regions.get("north", {}).get("text"),
                    })

        print(f"Fetched data for {date_str}")  # Progress tracking

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {date_str}: {e}")

    # Move to the next day
    current_date += timedelta(days=1)

    # To avoid rate limiting
    time.sleep(1)

# Save the collected data as JSON
with open("weather_data_enhanced.json", "w") as json_file:
    json.dump(all_data, json_file, indent=4)

df = pd.DataFrame(all_data)

# Save to CSV
df.to_csv("../datasets/final_data/24_hr_weather_forecast_data.csv", index=False)