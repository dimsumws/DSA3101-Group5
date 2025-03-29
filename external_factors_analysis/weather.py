import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import statsmodels.formula.api as smf
from data import tourism, wait_time, four_day_forecast, weather, events, school_holidays, public_holidays, ride_wait_times, rides, tourism_age

# ensure that date is in datetime format
wait_time_details = wait_time.copy()
wait_time_details['date'] = pd.to_datetime(wait_time_details['date'])

# filter the DataFrame to include only the date and wait_time columns
wait_time_details = wait_time_details.filter(['date', 'wait_time'])

# group by date and calculate the average, maximum, and minimum wait times
wait_time_details = wait_time_details.groupby('date').agg(
    avg_wait=('wait_time', 'mean'),
    max_wait=('wait_time', 'max'),
    min_wait=('wait_time', 'min')
).reset_index()

# ensure that date is in datetime format
weather['Date'] = pd.to_datetime(weather['Date'], format = '%d/%m/%Y')

# filter for entries in the year 2024
weather_2024 = weather[weather['Date'].dt.year == 2024].copy().reset_index()
weather_2024 = weather_2024.drop(columns=['index'])

# filter only for the necessary columns
weather_2024 = weather_2024.filter(['Date', 'Daily Rainfall Total (mm)', 'Maximum Temperature (°C)', 'Minimum Temperature (°C)', 'Rain'])

# get wait time data for the weather types
merge_weather_wait_time = pd.merge(wait_time_details, weather_2024, left_on='date', right_on='Date', how='inner')
merge_weather_wait_time = merge_weather_wait_time.drop(columns=['Date'])

# function to classify weather 
def categorize_weather(row):
    if row['Daily Rainfall Total (mm)'] > 5:
        return 'Rainy'
    elif row['Maximum Temperature (°C)'] > 32:
        return 'Hot'
    else:
        return 'Mild'

# apply to column
merge_weather_wait_time['weather_category'] = merge_weather_wait_time.apply(categorize_weather, axis=1)

# plot boxplot of wait types by weather
plt.figure(figsize=(10, 6))
sns.boxplot(data=merge_weather_wait_time, x='weather_category', y='avg_wait')
plt.title('Average Wait Time by Weather Type')
plt.xlabel('Weather Type')
plt.ylabel('Average Wait Time (min)')
plt.xticks(rotation=45)
plt.tight_layout()

# save figure
plt.savefig('external_factors_analysis/weather_figures/wait_time_by_weather.png', dpi=300, bbox_inches='tight')
plt.show()

# summary statistics for wait times by weather
summary_stats = merge_weather_wait_time.groupby('weather_category')['avg_wait'].describe()
summary_stats = summary_stats.reset_index()
print(summary_stats)

# Filter ride wait data for 2024 and extract just the date
ride_rain = ride_wait_times[ride_wait_times['Date/Time'].dt.year == 2024].copy()
ride_rain['Date'] = ride_rain['Date/Time'].dt.date

# Convert both to pandas datetime for merging
ride_rain['Date'] = pd.to_datetime(ride_rain['Date'])
weather['Date'] = pd.to_datetime(weather['Date'], format='%Y-%m-%d')

# Merge on the cleaned datetime columns
ride_rain = ride_rain.merge(weather, on='Date', how='inner')
ride_rain = ride_rain.filter(['Date/Time', 'Ride', 'Wait Time', 'Rain'])

# get rain data
ride_wait_times_rain = ride_rain[ride_rain['Rain'] == 1].copy()

# change interval to 30mins, and extract time
ride_wait_times_rain['Date/Time'] = pd.to_datetime(ride_wait_times_rain['Date/Time'])
ride_wait_times_rain['Time'] = ride_wait_times_rain['Date/Time'].dt.floor('30T').dt.time

# group data
avg_rain_waits = ride_wait_times_rain.groupby(['Ride', 'Time'])['Wait Time'].mean().reset_index()

# dummy date for plotting
avg_rain_waits['Date/Time'] = pd.to_datetime('2024-04-01 ' + avg_rain_waits['Time'].astype(str))

resampled_data = avg_rain_waits.copy()

# opening hours for USS
resampled_data = avg_rain_waits.copy()
resampled_data['Date/Time'] = pd.to_datetime('2024-04-01 ' + resampled_data['Time'].astype(str))
resampled_data = resampled_data[
    (resampled_data['Date/Time'].dt.time >= pd.to_datetime('09:00').time()) &
    (resampled_data['Date/Time'].dt.time <= pd.to_datetime('21:00').time())
]

# max wait times for each 30 min interval
max_wait_times = resampled_data.loc[resampled_data.groupby('Date/Time')['Wait Time'].idxmax()]

# top 5 rides of the month
avg_wait_by_ride = resampled_data.groupby('Ride')['Wait Time'].mean().sort_values(ascending=False)
top_rides = avg_wait_by_ride.head(5).index.tolist()
top_rides_rain = top_rides.copy()

# setup plot
plt.figure(figsize=(20,12))
palette = sns.color_palette("tab20", len(resampled_data['Ride'].unique()))
ax = plt.gca()

# plot each ride's line with fading for non-top rides
for ride in resampled_data['Ride'].unique():
    ride_data = resampled_data[resampled_data['Ride'] == ride]
    sns.lineplot(
        data=ride_data,
        x='Date/Time',
        y='Wait Time',
        label=ride,
        color=palette[list(resampled_data['Ride'].unique()).index(ride)],
        linewidth=2 if ride in top_rides else 1,
        alpha=1.0 if ride in top_rides else 0.3
    )

# scatter plot for highest wait times at each interval
for ride in resampled_data['Ride'].unique():
    ride_data = max_wait_times[max_wait_times['Ride'] == ride]
    sns.scatterplot(
        data=ride_data,
        x='Date/Time',
        y='Wait Time',
        color=palette[list(resampled_data['Ride'].unique()).index(ride)],
        s=100,
        legend=False
    )

# shade lunchtime and dinner time
for start, end in [('12:00', '13:00'), ('18:00', '19:00')]:
    ax.axvspan(pd.to_datetime(f"2024-04-01 {start}"), pd.to_datetime(f"2024-04-01 {end}"),
               color='lightgray', alpha=0.3)

# format x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
plt.xticks(rotation=0, fontsize=10)
plt.yticks(fontsize=10)

# grid
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# titles and labels
plt.title('USS Ride Average Wait Times Across 2024 Rain Days', fontsize=16, weight='bold')
plt.xlabel('Time of Day', fontsize=12)
plt.ylabel('Average Wait Time (minutes)', fontsize=12)

# 60 min threshold line
plt.axhline(y=60, linestyle='--', color='gray', alpha=0.4)
plt.text(resampled_data['Date/Time'].min(), 62, '60 min threshold', color='gray', fontsize=10)

# custom legend for scatter points
highlight_legend = mpatches.Patch(color='black', label='• Point = Highest Wait Time at Each Interval')
handles, labels = ax.get_legend_handles_labels()
plt.legend(
    handles=handles + [highlight_legend],
    title='Ride',
    bbox_to_anchor=(1.05, 1),
    loc='upper left',
    borderaxespad=0,
    fontsize=9,
    title_fontsize=10
)

plt.tight_layout()

# save figure
plt.savefig('external_factors_analysis/weather_figures/wait_time_during_rain.png', dpi=300, bbox_inches='tight')
plt.show()

# get no rain data
ride_wait_times_no_rain = ride_rain[ride_rain['Rain'] == 0].copy()

# change interval to 30mins, and extract time
ride_wait_times_no_rain['Date/Time'] = pd.to_datetime(ride_wait_times_no_rain['Date/Time'])
ride_wait_times_no_rain['Time'] = ride_wait_times_no_rain['Date/Time'].dt.floor('30T').dt.time

# group data
avg_no_rain_waits = ride_wait_times_no_rain.groupby(['Ride', 'Time'])['Wait Time'].mean().reset_index()

# dummy date for plotting
avg_no_rain_waits['Date/Time'] = pd.to_datetime('2024-01-01 ' + avg_no_rain_waits['Time'].astype(str))

# opening hours for USS
resampled_data = avg_no_rain_waits.copy()
resampled_data['Date/Time'] = pd.to_datetime('2024-01-01 ' + resampled_data['Time'].astype(str))
resampled_data = resampled_data[
    (resampled_data['Date/Time'].dt.time >= pd.to_datetime('09:00').time()) &
    (resampled_data['Date/Time'].dt.time <= pd.to_datetime('21:00').time())
]

# max wait times for each 30 min interval
max_wait_times = resampled_data.loc[resampled_data.groupby('Date/Time')['Wait Time'].idxmax()]

# top 5 rides of the month
avg_wait_by_ride = resampled_data.groupby('Ride')['Wait Time'].mean().sort_values(ascending=False)
top_rides = avg_wait_by_ride.head(5).index.tolist()
top_rides_no_rain = top_rides.copy()

# setup plot
plt.figure(figsize=(20,12))
palette = sns.color_palette("tab20", len(resampled_data['Ride'].unique()))
ax = plt.gca()

# plot each ride's line with fading for non-top rides
for ride in resampled_data['Ride'].unique():
    ride_data = resampled_data[resampled_data['Ride'] == ride]
    sns.lineplot(
        data=ride_data,
        x='Date/Time',
        y='Wait Time',
        label=ride,
        color=palette[list(resampled_data['Ride'].unique()).index(ride)],
        linewidth=2 if ride in top_rides else 1,
        alpha=1.0 if ride in top_rides else 0.3
    )

# scatter plot for highest wait times at each interval
for ride in resampled_data['Ride'].unique():
    ride_data = max_wait_times[max_wait_times['Ride'] == ride]
    sns.scatterplot(
        data=ride_data,
        x='Date/Time',
        y='Wait Time',
        color=palette[list(resampled_data['Ride'].unique()).index(ride)],
        s=100,
        legend=False
    )

# shade lunchtime and dinner time
for start, end in [('12:00', '13:00'), ('18:00', '19:00')]:
    ax.axvspan(pd.to_datetime(f"2024-01-01 {start}"), pd.to_datetime(f"2024-01-01 {end}"),
               color='lightgray', alpha=0.3)

# format x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
plt.xticks(rotation=0, fontsize=10)
plt.yticks(fontsize=10)

# grid
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# titles and labels
plt.title('USS Ride Average Wait Times Across 2024 No Rain Days', fontsize=16, weight='bold')
plt.xlabel('Time of Day', fontsize=12)
plt.ylabel('Average Wait Time (minutes)', fontsize=12)

# 60 min threshold line
plt.axhline(y=60, linestyle='--', color='gray', alpha=0.4)
plt.text(resampled_data['Date/Time'].min(), 62, '60 min threshold', color='gray', fontsize=10)

# custom legend for scatter points
highlight_legend = mpatches.Patch(color='black', label='• Point = Highest Wait Time at Each Interval')
handles, labels = ax.get_legend_handles_labels()
plt.legend(
    handles=handles + [highlight_legend],
    title='Ride',
    bbox_to_anchor=(1.05, 1),
    loc='upper left',
    borderaxespad=0,
    fontsize=9,
    title_fontsize=10
)

plt.tight_layout()

# save figure
plt.savefig('external_factors_analysis/weather_figures/wait_time_during_no_rain.png', dpi=300, bbox_inches='tight')
plt.show()

# filter for top rides in rain 2024
print('Rain:')
top_rides_info = rides[rides['ride'].isin(top_rides_rain)].copy().reset_index(drop=True)
print(top_rides_info)
# filter for top rides in no_rain 2024
print('No Rain:')
top_rides_info = rides[rides['ride'].isin(top_rides_no_rain)].copy().reset_index(drop=True)
print(top_rides_info)