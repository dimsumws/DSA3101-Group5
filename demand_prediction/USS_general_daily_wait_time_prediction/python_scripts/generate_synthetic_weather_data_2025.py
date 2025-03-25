import pandas as pd
import numpy as np
from datetime import datetime
from faker import Faker

reference_path = "../../../data/Meteorological/datasets/final_data/merged_weather_data_clean.csv"
reference_df = pd.read_csv(reference_path)
dates = pd.date_range(start="2025-02-23", end="2025-12-31", freq="D")
num_days = len(dates)

# Initialize Faker
fake = Faker()
synth_weather = pd.DataFrame({'date': dates})
synth_weather['forecast_day'] = synth_weather['date'].dt.day_name()

for col in reference_df.columns:
    if col in ['date', 'forecast_day']:
        continue

    col_data = reference_df[col].dropna()

    if reference_df[col].dtype in [np.float64, np.int64]:
        if "humidity_high" in col:
            values = np.random.normal(loc=70, scale=10, size=num_days)
        elif "psi" in col.lower():
            values = np.random.normal(loc=40, scale=10, size=num_days)
            # Inject a few unhealthy days
            high_psi_indices = np.random.choice(num_days, size=5, replace=False)
            values[high_psi_indices] = np.random.randint(101, 200, size=5)
        else:
            mean = col_data.mean()
            std = col_data.std()
            values = np.random.normal(loc=mean, scale=std, size=num_days)
        synth_weather[col] = np.clip(np.round(values, 2), a_min=0, a_max=None)

    else:
        unique_vals = col_data[col_data.astype(str) != "0"].astype(str).unique()
        if len(unique_vals) > 0:
            synth_weather[col] = np.random.choice(unique_vals, size=num_days)
        else:
            synth_weather[col] = [fake.sentence(nb_words=5) for _ in range(num_days)]

# Logical Constraints for Rainfall 
synth_weather['Highest 30 Min Rainfall (mm)'] = np.round(np.random.exponential(scale=2, size=num_days), 2)
synth_weather['Highest 60 Min Rainfall (mm)'] = synth_weather['Highest 30 Min Rainfall (mm)'] + np.round(np.random.exponential(scale=1.5, size=num_days), 2)
synth_weather['Highest 120 Min Rainfall (mm)'] = synth_weather['Highest 60 Min Rainfall (mm)'] + np.round(np.random.exponential(scale=1.5, size=num_days), 2)
synth_weather['Daily Rainfall Total (mm)'] = synth_weather['Highest 120 Min Rainfall (mm)'] + np.round(np.random.exponential(scale=3, size=num_days), 2)

# Logical Constraints for Temperature 
synth_weather['Minimum Temperature (°C)'] = np.round(np.random.normal(loc=25.5, scale=1, size=num_days), 2)
synth_weather['Maximum Temperature (°C)'] = synth_weather['Minimum Temperature (°C)'] + np.round(np.random.uniform(3, 6, size=num_days), 2)
synth_weather['Mean Temperature (°C)'] = (
    synth_weather['Minimum Temperature (°C)'] + synth_weather['Maximum Temperature (°C)']
) / 2

# Logical Constraints for Wind 
synth_weather['Mean Wind Speed (km/h)'] = synth_weather['Min Wind Speed (km/h)'] + np.round(np.random.uniform(1, 3, size=num_days), 2)
synth_weather['Max Wind Speed (km/h)'] = synth_weather['Mean Wind Speed (km/h)'] + np.round(np.random.uniform(2, 4, size=num_days), 2)

def get_psi_rating(value):
    if value <= 50:
        return "Good"
    elif value <= 100:
        return "Moderate"
    elif value <= 200:
        return "Unhealthy"
    else:
        return "Very unhealthy"

synth_weather['psi_level_rating'] = synth_weather['average_nationwide_psi'].apply(get_psi_rating)

output_path = "../../../data//Meteorological/datasets/final_data/synthetic_weather_data_faker_style_2025_cleaned.csv"
synth_weather.to_csv(output_path, index=False)
print(f"✅ Saved cleaned synthetic data to: {output_path}")
