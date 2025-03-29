import pandas as pd

# tourism data
tourism = pd.read_csv('data/singapore_tourism_data/Final/tourism_counts/tourism.csv')
tourism['year_month'] = pd.to_datetime(tourism['year_month'])
tourism['no_of_visitors'] = pd.to_numeric(tourism['no_of_visitors'], errors='coerce').fillna(0).astype(int)

# wait time data
wait_time = pd.read_csv('data/uss_wait_times/cleaned_data_2022_2025/cleaned_2024_wait_times.csv')

# four day weather forecast data
four_day_forecast = pd.read_csv('data/Meteorological/datasets/final_data/4_day_weather_forecasts.csv')

# weather data
weather = pd.read_csv('data/Meteorological/datasets/final_data/final_augmented_weather_sentosa_data.csv')
weather['Rain'] = weather['Daily Rainfall Total (mm)'].apply(lambda x: 1 if x > 0 else 0)

# event data
events = pd.read_csv('data/Events/EventData/supplementary_event_data_2016_2025.csv')

# school holidays data
school_holidays = pd.read_csv('data/Events/Holidays/datasets/daily_school_holidays_combined.csv')

# public holidays data
public_holidays = pd.read_csv('data/Events/Holidays/datasets/final_merged_PH_2020_2025.csv')

# ride wait times data
ride_wait_times = pd.read_csv('data/uss_ride_wait_times/all_ride_wait_times.csv')

# convert to datetime
ride_wait_times['Date/Time'] = pd.to_datetime(ride_wait_times['Date/Time'], errors='coerce')

# convert 'Wait Time' to integer, handling non-numeric values
ride_wait_times['Wait Time'] = pd.to_numeric(ride_wait_times['Wait Time'], errors='coerce').fillna(0).astype(int)

# ensure 'Ride' is of type string
ride_wait_times['Ride'] = ride_wait_times['Ride'].astype(str)

# replace Puss In Boots’ Giant Journey with Puss In Boots' Giant Journey
ride_wait_times['Ride'] = ride_wait_times['Ride'].str.replace('Puss In Boots’ Giant Journey', 'Puss In Boots\' Giant Journey')

# tourism age group data
tourism_age = pd.read_csv('data/singapore_tourism_data/Final/tourism_counts/tourism_age_groups.csv')
tourism_age['year_month'] = pd.to_datetime(tourism_age['year_month'])
tourism_age['no_of_visitors'] = pd.to_numeric(tourism_age['no_of_visitors'], errors='coerce').fillna(0).astype(int)

# ride data
rides = pd.read_csv('data/uss_attraction_details/rides.csv')