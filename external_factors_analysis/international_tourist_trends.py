import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import statsmodels.formula.api as smf
from data import tourism, wait_time, four_day_forecast, weather, events, school_holidays, public_holidays, ride_wait_times, rides, tourism_age

wait_time_month = wait_time.copy()
# ensure that date is in datetime format
wait_time_month['date'] = pd.to_datetime(wait_time['date'])
wait_time_month['month'] = wait_time['date'].dt.month

# group by month and calculate the average wait time
wait_time_month = wait_time_month.groupby('month')['wait_time'].mean().reset_index()

# plotting wait time by month
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=wait_time_month, x='month', y='wait_time', ax=ax)
sns.scatterplot(data=wait_time_month, x='month', y='wait_time', ax=ax, color='red', s=100)
ax.set_title('Average Overall Wait Time in USS by Month')
ax.set_xlabel('Month')
ax.set_ylabel('Average Wait Time (minutes)')
ax.set_xticks(range(1, 13))
# save the figure
plt.savefig('external_factors_analysis/international_tourist_figures/wait_time_month.png', bbox_inches='tight')
plt.show()

# filter for 'Total International Visitor Arrivals By Inbound Tourism Markets'
tourism_total_2024 = tourism[tourism['Region/Country'] == 'Total International Visitor Arrivals By Inbound Tourism Markets'].copy()

# drop the 'DataSeries' column
tourism_total_2024 = tourism_total_2024.drop(columns=['Region/Country'])

# filter for entries in the year 2024
tourism_total_2024 = tourism_total_2024[tourism_total_2024['year_month'].dt.year == 2024]

# extract the month
tourism_total_2024['month'] = tourism_total_2024['year_month'].dt.month
tourism_total_2024 = tourism_total_2024.drop(columns=['year_month'])
tourism_total_2024 = tourism_total_2024.sort_values(by='month')

# plotting total international tourists by month
fig, ax = plt.subplots(figsize=(10, 6))
sns.lineplot(data=tourism_total_2024, x='month', y = "no_of_visitors", ax=ax)
sns.scatterplot(data=tourism_total_2024, x='month', y = "no_of_visitors", ax=ax, color='red', s=100)
ax.set_title('Total International Tourists by Month')
ax.set_xlabel('Month')
ax.set_ylabel('Total Number of Tourists')
ax.set_xticks(range(1, 13))  # ensure all months are shown on the x-axis
# save the figure
plt.savefig('external_factors_analysis/international_tourist_figures/tourism_total_2024.png', bbox_inches='tight')
plt.show()

# filter for entries in the year 2024
tourism_total_2024_reg = tourism[tourism['year_month'].dt.year == 2024].copy()

# define the regions
regions = ['Southeast Asia', 'Greater China', 'North Asia', 'South Asia', 'West Asia', 'Africa', 'Oceania', 'Europe', 'Americas', 'Others']

# extract the month
tourism_total_2024_reg['month'] = tourism_total_2024_reg['year_month'].dt.month

# plotting total international tourists by month for each region
fig, ax = plt.subplots(figsize=(12, 8))

for region in regions:
    region_data = tourism_total_2024_reg[tourism_total_2024_reg['Region/Country'] == region]
    if not region_data.empty:
        monthly_visitors = region_data.groupby('month')['no_of_visitors'].sum().reset_index()
        sns.lineplot(data=monthly_visitors, x='month', y='no_of_visitors', ax=ax, label=region)
        sns.scatterplot(data=monthly_visitors, x='month', y='no_of_visitors', ax=ax, s=100)

ax.set_title('Total International Tourists by Month for Each Region')
ax.set_xlabel('Month')
ax.set_ylabel('Total Number of Tourists')
ax.set_xticks(range(1, 13))  # Ensure all months are shown on the x-axis
ax.legend(title='Region')
# save the figure
plt.savefig('external_factors_analysis/international_tourist_figures/tourism_by_region.png', bbox_inches='tight')
plt.show()

# get feb 2024 data
ride_wait_times_feb = ride_wait_times[
    (ride_wait_times['Date/Time'].dt.month == 2) &
    (ride_wait_times['Date/Time'].dt.year == 2024)
].copy()

# change interval to 30mins, and extract time
ride_wait_times_feb['Date/Time'] = pd.to_datetime(ride_wait_times_feb['Date/Time'])
ride_wait_times_feb['Time'] = ride_wait_times_feb['Date/Time'].dt.floor('30T').dt.time

# group data
avg_feb_waits = ride_wait_times_feb.groupby(['Ride', 'Time'])['Wait Time'].mean().reset_index()

# dummy date for plotting
avg_feb_waits['Date/Time'] = pd.to_datetime('2024-02-01 ' + avg_feb_waits['Time'].astype(str))

resampled_data = avg_feb_waits.copy()

# opening hours for USS
resampled_data = avg_feb_waits.copy()
resampled_data['Date/Time'] = pd.to_datetime('2024-02-01 ' + resampled_data['Time'].astype(str))
resampled_data = resampled_data[
    (resampled_data['Date/Time'].dt.time >= pd.to_datetime('09:00').time()) &
    (resampled_data['Date/Time'].dt.time <= pd.to_datetime('21:00').time())
]

# max wait times for each 30 min interval
max_wait_times = resampled_data.loc[resampled_data.groupby('Date/Time')['Wait Time'].idxmax()]

# top 5 rides of the month
avg_wait_by_ride = resampled_data.groupby('Ride')['Wait Time'].mean().sort_values(ascending=False)
top_rides = avg_wait_by_ride.head(5).index.tolist()
top_rides_feb = top_rides.copy()

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
    ax.axvspan(pd.to_datetime(f"2024-02-01 {start}"), pd.to_datetime(f"2024-02-01 {end}"),
               color='lightgray', alpha=0.3)

# format x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
plt.xticks(rotation=0, fontsize=10)
plt.yticks(fontsize=10)

# grid
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# titles and labels
plt.title('USS Ride Average Wait Times Across February 2024', fontsize=16, weight='bold')
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
# save the figure
plt.savefig('external_factors_analysis/international_tourist_figures/uss_wait_times_feb_2024.png', bbox_inches='tight')
plt.show()

# get jul 2024 data
ride_wait_times_jul = ride_wait_times[
    (ride_wait_times['Date/Time'].dt.month == 7) &
    (ride_wait_times['Date/Time'].dt.year == 2024)
].copy()

# change interval to 30mins, and extract time
ride_wait_times_jul['Date/Time'] = pd.to_datetime(ride_wait_times_jul['Date/Time'])
ride_wait_times_jul['Time'] = ride_wait_times_jul['Date/Time'].dt.floor('30T').dt.time

# group data
avg_jul_waits = ride_wait_times_jul.groupby(['Ride', 'Time'])['Wait Time'].mean().reset_index()

# dummy date for plotting
avg_jul_waits['Date/Time'] = pd.to_datetime('2024-07-01 ' + avg_jul_waits['Time'].astype(str))

resampled_data = avg_jul_waits.copy()

# opening hours for USS
resampled_data = avg_jul_waits.copy()
resampled_data['Date/Time'] = pd.to_datetime('2024-07-01 ' + resampled_data['Time'].astype(str))
resampled_data = resampled_data[
    (resampled_data['Date/Time'].dt.time >= pd.to_datetime('09:00').time()) &
    (resampled_data['Date/Time'].dt.time <= pd.to_datetime('21:00').time())
]

# max wait times for each 30 min interval
max_wait_times = resampled_data.loc[resampled_data.groupby('Date/Time')['Wait Time'].idxmax()]

# top 5 rides of the month
avg_wait_by_ride = resampled_data.groupby('Ride')['Wait Time'].mean().sort_values(ascending=False)
top_rides = avg_wait_by_ride.head(5).index.tolist()
top_rides_jul = top_rides.copy()

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
    ax.axvspan(pd.to_datetime(f"2024-07-01 {start}"), pd.to_datetime(f"2024-07-01 {end}"),
               color='lightgray', alpha=0.3)

# format x-axis
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
plt.xticks(rotation=0, fontsize=10)
plt.yticks(fontsize=10)

# grid
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# titles and labels
plt.title('USS Ride Average Wait Times Across July 2024', fontsize=16, weight='bold')
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

# save the figure
plt.savefig('external_factors_analysis/international_tourist_figures/uss_wait_times_jul_2024.png', bbox_inches='tight')
plt.show()

# filter for top rides in feb 2024
print('February 2024:')
top_rides_info = rides[rides['ride'].isin(top_rides_feb)].copy().reset_index(drop=True)
print(top_rides_info)
# filter for top rides in jul 2024
print('July 2024:')
top_rides_info = rides[rides['ride'].isin(top_rides_jul)].copy().reset_index(drop=True)
print(top_rides_info)

# filter the data for February and July 2024
age_groups_feb_jul_2024 = tourism_age[
    (tourism_age['year_month'].dt.year == 2024) &
    (tourism_age['year_month'].dt.month.isin([2, 7]))
].copy()

# extract the month for plotting
age_groups_feb_jul_2024['month'] = age_groups_feb_jul_2024['year_month'].dt.month

# convert month number to month name
age_groups_feb_jul_2024['month'] = age_groups_feb_jul_2024['year_month'].dt.month.map({2: 'February', 7: 'July'})

# group by age group and month, and sum the number of visitors
grouped_data = age_groups_feb_jul_2024.groupby(['age_group', 'month'])['no_of_visitors'].sum().reset_index()

# calculate the total number of visitors for each month
total_visitors_per_month = grouped_data.groupby('month')['no_of_visitors'].sum().reset_index()
total_visitors_per_month.columns = ['month', 'total_visitors']

# merge the total visitors data with the grouped data
grouped_data = pd.merge(grouped_data, total_visitors_per_month, on='month')

# calculate the proportion of visitors for each age group within each month
grouped_data['proportion'] = grouped_data['no_of_visitors'] / grouped_data['total_visitors']

# define the order of age groups for plotting
age_order = [
    'Under 15 Years',
    '15-19 Years',
    '20-24 Years',
    '25-34 Years',
    '35-44 Years',
    '45-54 Years',
    '55-64 Years',
    '65 & Over'
]

# plotting the proportion of visitors by age group for February and July 2024
plt.figure(figsize=(14, 8))
sns.barplot(data=grouped_data, x='age_group', y='proportion', hue='month', order=age_order)
plt.title('Proportion of Visitors by Age Group in February and July 2024')
plt.xlabel('Age Group')
plt.ylabel('Proportion of Visitors')
plt.xticks(rotation=45)

# save the figure
plt.savefig('external_factors_analysis/international_tourist_figures/age_group_proportion.png', bbox_inches='tight')
plt.show()