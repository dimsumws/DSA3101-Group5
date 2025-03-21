path = "../datasets/raw_data/Historical24hrPSI.csv"

import os
import pandas as pd
import glob
import chardet
import datetime

df = pd.read_csv(path)
#print(df.head())

def categorize_psi(psi_reading):
    psi_reading = int(psi_reading)
    if psi_reading <= 50:
        return "Good"
    elif 51 <= psi_reading <= 100:
        return "Moderate"
    elif 101 <= psi_reading <= 200:
        return "Unhealthy"
    elif 201 <= psi_reading <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

df['24hr_psi'] = pd.to_datetime(df['24hr_psi'], format = '%d/%m/%Y %I:%M', errors='coerce')
df = df.rename(columns = {'24hr_psi':'datetime'})
df['date'] = df['datetime'].dt.date
daily_avg_df = round(df.groupby('date').mean(), 2)
daily_avg_df = daily_avg_df.reset_index()
daily_avg_df = daily_avg_df.drop('datetime', axis=1)
daily_avg_df = daily_avg_df.rename(columns={'north':'north_avg_daily_psi', 'south':'south_avg_daily_psi', 'east':'east_avg_daily_psi', 'west':'west_avg_daily_psi', 'central':'central_avg_daily_psi'})
daily_avg_df['highest_region_reading'] = daily_avg_df.iloc[:, 1:6].idxmax(axis=1)
daily_avg_df['psi_level_rating'] = daily_avg_df['average_nationwide_psi'].apply(categorize_psi)
daily_avg_df.to_csv("../datasets/final_data/daily_avg_psi_readings.csv",index=False)

## since the dataset provided from https://data.gov.sg/datasets/d_b4cf557f8750260d229c49fd768e11ed/view only provides from 2014 to 2024 and excludes the first few days of 2025
## we can query psi api from data gov sg to augment the data with the remaining days (which is 1st jan 2025 to 23 feb 2025)

import requests

# API endpoint
url = "https://api-open.data.gov.sg/v2/real-time/api/psi"

start_date = datetime.datetime(2025, 1, 1)
end_date = datetime.datetime(2025, 2, 23)
psi_data = []
current_date = start_date

while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    params = {"date": date_str}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "data" in data and "items" in data["data"] and len(data["data"]["items"]) > 0:
            # Use the last item of the day (most recent reading)
            item = data["data"]["items"][-1]
            readings = item.get("readings", {})
            psi = readings.get("psi_twenty_four_hourly", {})

            row = {
                "date": current_date.date(),
                "north_avg_daily_psi": psi.get("north", 0),
                "south_avg_daily_psi": psi.get("south", 0),
                "east_avg_daily_psi": psi.get("east", 0),
                "west_avg_daily_psi": psi.get("west", 0),
                "central_avg_daily_psi": psi.get("central", 0),
            }

            values = list(row.values())[1:6] # do not include data
            avg = round(sum(values) / len(values), 2)
            row["average_nationwide_psi"] = avg

            region_map = {
                "north_avg_daily_psi": "north",
                "south_avg_daily_psi": "south",
                "east_avg_daily_psi": "east",
                "west_avg_daily_psi": "west",
                "central_avg_daily_psi": "central"
            }
            max_region_col = max(region_map.keys(), key=lambda k: row[k])
            row["highest_region_reading"] = region_map[max_region_col]
            row["psi_level_rating"] = categorize_psi(avg)
            psi_data.append(row)

        else:
            print(f"No data for {date_str}")
    except Exception as e:
        print(f"[ERROR] for {date_str}: {e}")

    current_date += datetime.timedelta(days=1)

final_df = pd.concat([daily_avg_df, pd.DataFrame(psi_data)])
print(final_df.head())
final_df.to_csv("../datasets/final_data/daily_avg_psi_readings.csv",index=False)