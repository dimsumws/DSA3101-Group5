## generating 3 days worth of data, assuming for each day, the mean is 23 mins
## and using synthethic Weather Data, accurate event and holiday labels

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from scipy.sparse import hstack

event_data = pd.read_csv('../../../data/Events/EventData/2025_remainder_supplementary_event.csv')
school_holidays = pd.read_csv('../../../data/Events/Holidays/datasets/2025_daily_school_holidays.csv')
weather = pd.read_csv('../../../data/Meteorological/datasets/final_data/synthetic_weather_data_faker_style_2025_cleaned.csv')
event_data['Date'] = pd.to_datetime(event_data['Date'], dayfirst=True, errors='coerce')
school_holidays['date'] = pd.to_datetime(school_holidays['date'], dayfirst=True, errors='coerce')
weather['date'] = pd.to_datetime(weather['date'], dayfirst=True, errors='coerce')
df = pd.merge(event_data, school_holidays[['date', 'holiday_flag']], left_on='Date', right_on='date', how='left')
df = pd.merge(df, weather, left_on='Date', right_on='date', how='left')
df = df.loc[:, ~df.columns.str.contains('^date$')]

# === Filter for prediction range ===
df = df[(df['Date'] >= '2025-02-24') & (df['Date'] <= '2025-03-02')]

df['day_of_week'] = df['Date'].dt.dayofweek
weekday_ohe = pd.get_dummies(df['day_of_week'], prefix='weekday')
df = pd.concat([df, weekday_ohe], axis=1)
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
df.drop(columns=['day_of_week'], inplace=True)

df['month'] = df['Date'].dt.month
df['week_of_year'] = df['Date'].dt.isocalendar().week
df['is_holiday_weekend'] = df['is_weekend'] * df['holiday_flag']
df['rain_and_wind'] = df['Daily Rainfall Total (mm)'] * df['windspeed']

df['wait_time_lag_1'] = 23
df['wait_time_roll_mean_3'] = 22.3
df['wait_time_roll_std_5'] = 3.31
df['wait_time_roll_std_7'] = 4.10

training_features = [
    'date_x', 'temp_low', 'temp_high', 'humidity_low', 'humidity_high', 'forecast_summary',
    'wind_speed_low', 'wind_speed_high', 'wind_direction',
    'north_avg_daily_psi', 'south_avg_daily_psi', 'east_avg_daily_psi', 'west_avg_daily_psi', 'central_avg_daily_psi',
    'average_nationwide_psi', 'highest_region_reading', 'psi_level_rating',
    'Daily Rainfall Total (mm)', 'Highest 30 Min Rainfall (mm)', 'Highest 60 Min Rainfall (mm)', 'Highest 120 Min Rainfall (mm)',
    'Mean Temperature (°C)', 'Maximum Temperature (°C)', 'Minimum Temperature (°C)',
    'Mean Wind Speed (km/h)', 'Max Wind Speed (km/h)', 'avg_daily_relative_humidity', 'windspeed',
    'date_y', 'holiday_flag', 'Is_Event', 'Concert_Event', 'Sports_Event', 'MICE_Event', 'Theatre_Event', 'Cultural_Event', 'Social_Event',
    'weekday_0', 'weekday_1', 'weekday_2', 'weekday_3', 'weekday_4', 'weekday_5', 'weekday_6',
    'is_weekend', 'month', 'week_of_year', 'is_holiday_weekend',
    'wait_time_lag_1', 'wait_time_roll_mean_3', 'wait_time_roll_std_5', 'wait_time_roll_std_7'
]

df = df[training_features].copy()
X = df.copy()
with open('../models/Gradient_Boosting_Base.pkl', 'rb') as f:
    model = joblib.load(f)

with open('../models/tfidf_vectorizer.pkl', 'rb') as f:
    tfidf = joblib.load(f)

X['forecast_summary'] = X['forecast_summary'].astype(str).fillna("missing")
numeric_features = X.drop(columns=['forecast_summary']).select_dtypes(include=[np.number]).columns.tolist()
numeric_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])

numeric_output = numeric_pipeline.fit_transform(X[numeric_features])
categorical_output = tfidf.transform(X['forecast_summary'])
X_processed = hstack([numeric_output, categorical_output])

predictions = model.predict(X_processed)
results = pd.DataFrame({
    'Date': pd.date_range(start='2025-02-24', end='2025-03-02'),
    'Predicted_Wait_Time': predictions,
    'Prediction_Quality': 'Predicted'
})

results.to_csv('predicted_wait_times_feb24_mar02.csv', index=False)

