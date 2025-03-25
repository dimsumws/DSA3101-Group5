import os
import pandas as pd
import random

data_dir = os.path.join("..", "datasets", "final_data")

def filter_dates(df, date_col, start, end):
    return df[(df[date_col] >= start) & (df[date_col] <= end)]

def print_date_range(df, col, name):
    if not df.empty:
        print(f"{name}: {df[col].min()} to {df[col].max()}, total dates: {df[col].nunique()}")
    else:
        print(f"{name}: EMPTY")

# Load datasets
forecast_file = os.path.join(data_dir, "4_day_weather_forecasts.csv")
df_forecast = pd.read_csv(forecast_file)
df_forecast["record_date"] = pd.to_datetime(df_forecast["record_date"], errors="coerce")
df_forecast["forecast_date"] = pd.to_datetime(df_forecast["forecast_date"], dayfirst=True, errors="coerce")
df_forecast = df_forecast[df_forecast["forecast_date"] == df_forecast["record_date"] + pd.Timedelta(days=1)]
df_forecast.drop(columns=["forecast_timestamp"], inplace=True)
df_forecast.rename(columns={"record_date": "date"}, inplace=True)
df_forecast.drop(columns=["forecast_date"], inplace=True)
df_forecast["date"] = pd.to_datetime(df_forecast["date"])

avg_psi_file = os.path.join(data_dir, "daily_avg_psi_readings.csv")
df_psi = pd.read_csv(avg_psi_file)
df_psi["date"] = pd.to_datetime(df_psi["date"], errors="coerce")

weather_file = os.path.join(data_dir, "final_augmented_weather_sentosa_data.csv")
df_weather = pd.read_csv(weather_file)
df_weather["Date"] = pd.to_datetime(df_weather["Date"], dayfirst=True, errors="coerce")
df_weather.rename(columns={"Date": "date"}, inplace=True)

humidity_file = os.path.join(data_dir, "final_merged_RH_2017_2025.csv")
df_humidity = pd.read_csv(humidity_file)
df_humidity["date"] = pd.to_datetime(df_humidity["date"], dayfirst=True, errors="coerce")
df_humidity = df_humidity[["date", "avg_daily_relative_humidity"]]

windspeed_file = os.path.join(data_dir, "sentosa_avg_windspeed.csv")
df_wind = pd.read_csv(windspeed_file)
df_wind["date"] = pd.to_datetime(df_wind["date"], errors="coerce")
df_wind = df_wind[["date", "windspeed"]]

# Determine overlapping date range
dfs = [df_forecast, df_psi, df_weather, df_humidity, df_wind]
min_dates = [df['date'].min() for df in dfs]
max_dates = [df['date'].max() for df in dfs]
start_date = max(min_dates)
end_date = min(max_dates)
print(f"\n[✓] Common overlapping date range: {start_date.date()} to {end_date.date()}")

# Filter all data to the shared date range
df_forecast = filter_dates(df_forecast, "date", start_date, end_date)
df_psi = filter_dates(df_psi, "date", start_date, end_date)
df_weather = filter_dates(df_weather, "date", start_date, end_date)
df_humidity = filter_dates(df_humidity, "date", start_date, end_date)
df_wind = filter_dates(df_wind, "date", start_date, end_date)

# Diagnostics
print_date_range(df_forecast, "date", "4_day_weather_forecasts (next-day)")
print_date_range(df_psi, "date", "daily_avg_psi_readings")
print_date_range(df_weather, "date", "final_augmented_weather_sentosa_data")
print_date_range(df_humidity, "date", "final_merged_RH_2017_2025")
print_date_range(df_wind, "date", "sentosa_avg_windspeed")

# Merge with outer join, fill missing with 0
merged_df = df_forecast
for df in [df_psi, df_weather, df_humidity, df_wind]:
    merged_df = pd.merge(merged_df, df, on="date", how="outer")

merged_df = merged_df.sort_values("date").reset_index(drop=True)
merged_df = merged_df.fillna(0)

# --- Synthetic Forecast Handling ---
forecast_cols = [col for col in merged_df.columns if any(key in col.lower() for key in [
    "temp_low", "temp_high", "humidity_low_x", "humidity_high_x",
    "forecast_summary", "forecast_text", "wind_speed_low_x", "wind_speed_high_x", "wind_direction_x"
])]

def is_forecast_empty(row):
    return all((row[col] == 0 or row[col] == "0" or row[col] == "") for col in forecast_cols)

def generate_synthetic_forecast():
    return {
        "temp_low": round(random.uniform(24, 27), 1),
        "temp_high": round(random.uniform(31, 34), 1),
        "humidity_low_x": random.randint(55, 70),
        "humidity_high_x": random.randint(85, 95),
        "forecast_summary": "Partly Cloudy",
        "forecast_text_x": "Windy with passing showers",
        "wind_speed_low_x": random.randint(5, 15),
        "wind_speed_high_x": random.randint(15, 30),
        "wind_direction_x": random.choice(["N", "NNE", "NE", "E", "SE", "S", "SW", "W", "NW"])
    }

synthetic_count = 0
for idx, row in merged_df.iterrows():
    if is_forecast_empty(row):
        synthetic = generate_synthetic_forecast()
        for col, val in synthetic.items():
            if col in merged_df.columns:
                merged_df.at[idx, col] = val
        synthetic_count += 1

# Save output
output_file = os.path.join(data_dir, "merged_weather_data_clean.csv")
merged_df.to_csv(output_file, index=False)

print(f"\n[✓] Final dataset saved to: {output_file}")
print(f"[i] Final row count: {len(merged_df)}")
print(f"[i] Final date range: {merged_df['date'].min().date()} to {merged_df['date'].max().date()}")
