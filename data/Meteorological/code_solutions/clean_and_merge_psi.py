path = "../datasets/raw_data/Historical24hrPSI.csv"

import pandas as pd 
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