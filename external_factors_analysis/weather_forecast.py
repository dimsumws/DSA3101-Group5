import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import statsmodels.formula.api as smf
from data import tourism, wait_time, four_day_forecast, weather, events, school_holidays, public_holidays, ride_wait_times, rides, tourism_age

# ensure forecast_date and record_date are in datetime format
four_day_forecast['forecast_date'] = pd.to_datetime(four_day_forecast['forecast_date'])
four_day_forecast['record_date'] = pd.to_datetime(four_day_forecast['record_date'])

# filter for forecast_date in the year 2024
forecast_2024 = four_day_forecast[four_day_forecast['forecast_date'].dt.year == 2024]

# calculate the number of days prior the forecast was made
forecast_2024['days_prior'] = (forecast_2024['forecast_date'] - forecast_2024['record_date']).dt.days

# group by the number of days prior
grouped_forecast = forecast_2024.groupby('days_prior')

# split the dataset by the number of days prior
split_datasets = {days_prior: group for days_prior, group in grouped_forecast}

# save each split dataset as a variable
for days_prior, df in split_datasets.items():
    vars()[f'forecast_{days_prior}d'] = df
    print(f'forecast_{days_prior}d')

# label each forecast DataFrame by forecast horizon
forecast_1d['forecast_horizon'] = '1_day_prior'
forecast_2d['forecast_horizon'] = '2_days_prior'
forecast_3d['forecast_horizon'] = '3_days_prior'
forecast_4d['forecast_horizon'] = '4_days_prior'

# combine all forecasts into a single DataFrame
forecast_all = pd.concat([forecast_1d, forecast_2d, forecast_3d, forecast_4d], ignore_index=True)

# select only necessary columns for merging
forecast_all = forecast_all[[
    'forecast_date', 'forecast_horizon', 'forecast_text'
]]

# change wait time date to datetime
wait_time['date'] = pd.to_datetime(wait_time['date'], format = 'mixed')

# merge forecast data into wait times based on matching date
wait_times_weather = wait_time.merge(
    forecast_all,
    left_on='date',
    right_on='forecast_date',
    how='left'
)

# group by date, forecast horizon, and forecast text to compute average daily wait time
daily_weather_wait = wait_times_weather.groupby(
    ['date', 'forecast_horizon', 'forecast_text']
)['wait_time'].mean().reset_index()

# define a function to detect if the forecast implies rain
rain_keywords = ['showers', 'rain', 'thunder', 'thundery']

def is_rain_forecast(text):
    if pd.isna(text):
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in rain_keywords)

# create a new boolean column for rain forecast
daily_weather_wait['rain_forecast'] = daily_weather_wait['forecast_text'].apply(is_rain_forecast)

# plot boxplot of average daily wait times: Rain vs No Rain
plt.figure(figsize=(10, 6))
sns.boxplot(
    data=daily_weather_wait,
    x='rain_forecast',
    y='wait_time',
    hue='forecast_horizon'
)

# plot of wait time with and without rain
plt.title('Wait Times on Days With vs Without Rain Forecast')
plt.xlabel('Rain Forecasted')
plt.ylabel('Average Daily Wait Time (minutes)')
plt.xticks([0, 1], ['No Rain', 'Rain'])
plt.tight_layout()

# save figure
plt.savefig('external_factors_analysis/weather_forecast_figures/boxplot_rain_no_rain.png', dpi=300, bbox_inches='tight')
plt.show()

# summary statistics of wait times
rain_summary = daily_weather_wait.groupby('rain_forecast')['wait_time'].describe()
print(rain_summary)

# Prepare data
daily_weather_wait['rain_forecast'] = daily_weather_wait['forecast_text'].str.lower().str.contains('rain|shower|thunder')

# Fit linear model
model = smf.ols('wait_time ~ C(rain_forecast) + C(forecast_horizon)', data=daily_weather_wait).fit()
print(model.summary())
