import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import statsmodels.formula.api as smf
from data import tourism, wait_time, four_day_forecast, weather, events, school_holidays, public_holidays, ride_wait_times, rides, tourism_age

# ensure both are datetime type
school_holidays['date'] = pd.to_datetime(school_holidays['date'], format = "%d/%m/%Y")
public_holidays['date'] = pd.to_datetime(public_holidays['date'], format = "%Y-%m-%d")

# keep only school holiday dates NOT in public holiday list
school_only = school_holidays[
    ~school_holidays['date'].isin(public_holidays['date'])
]
school_only = school_only[school_only['year'] == 2024]
school_only = school_only[school_only['holiday_flag'] == 1]

# ensure that public holidays are not duplicated
public_holidays = public_holidays[['date']].drop_duplicates()
# only take public holidays from 2024
public_holidays = public_holidays[public_holidays['date'].dt.year == 2024]

# add flag for public and school holidays
public_holidays['is_public_holiday'] = True
school_only['is_school_only_holiday'] = True

# merge with public and school holidays
daily_wait = wait_time.copy()
daily_wait['date'] = pd.to_datetime(daily_wait['date'], format = 'mixed')
public_holidays['date'] = pd.to_datetime(public_holidays['date'], format = 'mixed')
daily_wait = daily_wait.merge(public_holidays, on='date', how='left')
daily_wait = daily_wait.merge(school_only, on='date', how='left')

# get weekend
daily_wait['day_of_week'] = daily_wait['date'].dt.dayofweek
daily_wait['is_weekend'] = daily_wait['day_of_week'].isin([5, 6])  # 5=Saturday, 6=Sunday

# fill na with false
daily_wait['is_public_holiday'] = daily_wait['is_public_holiday'].fillna(False)
daily_wait['is_school_only_holiday'] = daily_wait['is_school_only_holiday'].fillna(False)

# day time logic
def get_day_type(row):
    if row['is_public_holiday']:
        return 'Public Holiday'
    elif row['is_school_only_holiday']:
        return 'School Holiday'
    elif row['is_weekend']:
        return 'Weekend'
    else:
        return 'Weekday'

daily_wait['day_type'] = daily_wait.apply(get_day_type, axis=1)
daily_wait = daily_wait.filter(['date', 'time', 'wait_time', 'day_type'])
avg_daily_wait = daily_wait.groupby('date').agg({'wait_time': 'mean', 'day_type': 'first'}).reset_index()

# boxplot
plt.figure(figsize=(10, 6))
sns.boxplot(
    data=avg_daily_wait,
    x='day_type',
    y='wait_time',
    order=['Weekday', 'Weekend', 'School Holiday', 'Public Holiday']
)

# plot boxplot of average daily wait times by day type
plt.title('Average Daily Wait Times by Day Type (2024)')
plt.xlabel('Day Type')
plt.ylabel('Average Wait Time (minutes)')
plt.tight_layout()

# save plot
plt.savefig('external_factors_analysis/local_holiday_figures/average_daily_wait_times_by_day_type_2024.png')
plt.show()

# give the summary statistics of the wait time by day type
summary_stats = avg_daily_wait.groupby('day_type')['wait_time'].describe()
summary_stats = summary_stats.reset_index()
print(summary_stats)

# extract date from 'Date/Time' columns
ride_wait_times['date'] = pd.to_datetime(ride_wait_times['Date/Time']).dt.date

ride_wait_times['Ride'] = ride_wait_times['Ride'].str.replace('Puss In Boots’ Giant Journey', 'Puss In Boots\' Giant Journey')

# ensure 'date' column in public_holidays and school_only is of type datetime.date
public_holidays['date'] = pd.to_datetime(public_holidays['date']).dt.date
school_only['date'] = pd.to_datetime(school_only['date']).dt.date

# merge with public and school holidays
ride_daily_wait = ride_wait_times.merge(public_holidays, on='date', how='left')
ride_daily_wait = ride_daily_wait.merge(school_only, on='date', how='left')

# get weekend
ride_daily_wait['day_of_week'] = pd.to_datetime(ride_daily_wait['date']).dt.dayofweek
ride_daily_wait['is_weekend'] = ride_daily_wait['day_of_week'].isin([5, 6])  # 5=Saturday, 6=Sunday

# fill na with false
ride_daily_wait['is_public_holiday'] = ride_daily_wait['is_public_holiday'].fillna(False)
ride_daily_wait['is_school_only_holiday'] = ride_daily_wait['is_school_only_holiday'].fillna(False)

# apply the get_day_type function
ride_daily_wait['day_type'] = ride_daily_wait.apply(get_day_type, axis=1)
ride_daily_wait = ride_daily_wait.filter(['Date/Time', 'Ride', 'Wait Time', 'day_type'])

# get public holiday data
ride_wait_times_pub_hol = ride_daily_wait[ride_daily_wait['day_type'] == 'Public Holiday'].copy()

# change interval to 30mins, and extract time
ride_wait_times_pub_hol['Date/Time'] = pd.to_datetime(ride_wait_times_pub_hol['Date/Time'])
ride_wait_times_pub_hol['Time'] = ride_wait_times_pub_hol['Date/Time'].dt.floor('30T').dt.time

# group data
avg_pub_hol_waits = ride_wait_times_pub_hol.groupby(['Ride', 'Time'])['Wait Time'].mean().reset_index()

# dummy date for plotting
avg_pub_hol_waits['Date/Time'] = pd.to_datetime('2024-01-01 ' + avg_pub_hol_waits['Time'].astype(str))

resampled_data = avg_pub_hol_waits.copy()

# opening hours for USS
resampled_data = avg_pub_hol_waits.copy()
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
top_rides_pub_hol = top_rides.copy()

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
plt.title('USS Ride Average Wait Times Across 2024 Public Holidays', fontsize=16, weight='bold')
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

# save plot
plt.savefig('external_factors_analysis/local_holiday_figures/average_wait_times_by_ride_pub_hol_2024.png')
plt.show()

# get weekday data
ride_wait_times_normal = ride_daily_wait[ride_daily_wait['day_type'] == 'Weekday'].copy()

# change interval to 30mins, and extract time
ride_wait_times_normal['Date/Time'] = pd.to_datetime(ride_wait_times_normal['Date/Time'])
ride_wait_times_normal['Time'] = ride_wait_times_normal['Date/Time'].dt.floor('30T').dt.time

# group data
avg_weekday_waits = ride_wait_times_normal.groupby(['Ride', 'Time'])['Wait Time'].mean().reset_index()

# dummy date for plotting
avg_weekday_waits['Date/Time'] = pd.to_datetime('2024-03-01 ' + avg_weekday_waits['Time'].astype(str))

# opening hours for USS
resampled_data = avg_weekday_waits.copy()
resampled_data['Date/Time'] = pd.to_datetime('2024-03-01 ' + resampled_data['Time'].astype(str))
resampled_data = resampled_data[
    (resampled_data['Date/Time'].dt.time >= pd.to_datetime('09:00').time()) &
    (resampled_data['Date/Time'].dt.time <= pd.to_datetime('21:00').time())
]

# max wait times for each 30 min interval
max_wait_times = resampled_data.loc[resampled_data.groupby('Date/Time')['Wait Time'].idxmax()]

# top 5 rides of the month
avg_wait_by_ride = resampled_data.groupby('Ride')['Wait Time'].mean().sort_values(ascending=False)
top_rides = avg_wait_by_ride.head(5).index.tolist()
top_rides_weekday = top_rides.copy()

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
    ax.axvspan(pd.to_datetime(f"2024-03-01 {start}"), pd.to_datetime(f"2024-03-01 {end}"),
               color='lightgray', alpha=0.3)

# format x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
plt.xticks(rotation=0, fontsize=10)
plt.yticks(fontsize=10)

# grid
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# titles and labels
plt.title('USS Ride Average Wait Times Across 2024 Weekdays', fontsize=16, weight='bold')
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

# save plot
plt.savefig('external_factors_analysis/local_holiday_figures/average_wait_times_by_ride_weekday_2024.png')
plt.show()

# filter for top rides in public holidays 2024
print('Public Holiday:')
top_rides_info = rides[rides['ride'].isin(top_rides_pub_hol)].copy().reset_index(drop=True)
print(top_rides_info)
# filter for top rides in weekdays 2024
print('Weekday:')
top_rides_info = rides[rides['ride'].isin(top_rides_weekday)].copy().reset_index(drop=True)
print(top_rides_info)