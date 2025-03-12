import requests
import pandas as pd
from datetime import datetime, timedelta
import time

def fetch_forecast(date_str):
    url = "https://api-open.data.gov.sg/v2/real-time/api/four-day-outlook"
    params = {"date": date_str}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # raise an error for bad status codes
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data for {date_str}: {e}")
        return None

def main():
    # Data Gov provides data from March 2016 to Feb 2025
    start_date = datetime(2016, 3, 1)
    end_date = datetime(2025, 2, 23)
    
    latest_records = {}

    current_date = start_date
    while current_date <= end_date:
        query_date_str = current_date.strftime("%Y-%m-%d")
        print(f"Fetching data for {query_date_str}...")
        data = fetch_forecast(query_date_str)
        
        if data:
            records = data.get("data", {}).get("records", [])
            for record in records:
                rec_date = record.get("date", "")
                rec_ts_str = record.get("timestamp", "")
                if not rec_date or not rec_ts_str:
                    continue  # skip records missing required info

                # Parse the record's timestamp
                try:
                    rec_ts = datetime.strptime(rec_ts_str, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    continue

                if (rec_date not in latest_records) or (rec_ts > latest_records[rec_date][1]):
                    latest_records[rec_date] = (record, rec_ts)
        else:
            print(f"Data not available for {query_date_str}.")

        time.sleep(0.3)
        current_date += timedelta(days=1)

    rows = []
    for rec_date, (record, rec_ts) in latest_records.items():
        updatedTimestamp = record.get("updatedTimestamp", "")
        record_timestamp = record.get("timestamp", "")
        # Each record contains a 4-day forecast; extract each day's forecast.
        for forecast in record.get("forecasts", []):
            forecast_ts_str = forecast.get("timestamp", "")
            # Convert forecast timestamp to a formatted date string (DD/MM/YYYY)
            if forecast_ts_str:
                try:
                    forecast_dt = datetime.strptime(forecast_ts_str, "%Y-%m-%dT%H:%M:%S%z")
                    forecast_date_str = forecast_dt.strftime("%d/%m/%Y")
                except ValueError:
                    forecast_date_str = ""
            else:
                forecast_date_str = ""
            
            row = {
                "record_date": rec_date,
                #"updatedTimestamp": updatedTimestamp,
                #"record_timestamp": record_timestamp,
                "forecast_timestamp": forecast_ts_str,
                "forecast_date": forecast_date_str,
                "day": forecast.get("day", ""),
                "temp_low": forecast.get("temperature", {}).get("low"),
                "temp_high": forecast.get("temperature", {}).get("high"),
                "humidity_low": forecast.get("relativeHumidity", {}).get("low"),
                "humidity_high": forecast.get("relativeHumidity", {}).get("high"),
                "forecast_summary": forecast.get("forecast", {}).get("summary", ""),
                "forecast_text": forecast.get("forecast", {}).get("text", ""),
                "wind_speed_low": forecast.get("wind", {}).get("speed", {}).get("low"),
                "wind_speed_high": forecast.get("wind", {}).get("speed", {}).get("high"),
                "wind_direction": forecast.get("wind", {}).get("direction", "")
            }
            rows.append(row)

    df = pd.DataFrame(rows)
    csv_filename = "four_day_weather_forecasts.csv"
    df.to_csv(csv_filename, index=False)
    print(f"Saved {csv_filename}")

if __name__ == "__main__":
    main()
