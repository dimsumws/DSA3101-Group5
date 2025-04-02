import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import statsmodels.formula.api as smf
from data import tourism, wait_time, four_day_forecast, weather, events, school_holidays, public_holidays, ride_wait_times, rides, tourism_age

# get events data
events = events.copy()
# convert date column to datetime
events['Date'] = pd.to_datetime(events['Date'], format='mixed')
# convert time column to datetime
events['Year'] = events['Date'].dt.year
# filter for 2024
events = events[events['Year'] == 2024]
# drop the year column
events = events.drop(columns=['Year'])

# convert wait time date column to datetime
wait_time['date'] = pd.to_datetime(wait_time['date'], format='mixed')

# get wait time data and merge
events_wait = wait_time.merge(events, left_on='date', right_on='Date', how='left')
# retrieve only the relevant columns
events_wait_tot = events_wait.filter(['date', 'time', 'wait_time', 'Is_Event'])

# create a categorical label for plotting
events_wait_tot['Event_Label'] = events_wait_tot['Is_Event'].apply(lambda x: 'Event Day' if x == 1 or x == True else 'Non-Event Day')

# group by date to avoid repeated 5-min samples
daily_avg = events_wait_tot.groupby(['date', 'Event_Label'])['wait_time'].mean().reset_index()

# plotting the average wait time on event vs non-event days
plt.figure(figsize=(8, 6))
sns.boxplot(data=daily_avg, x='Event_Label', y='wait_time')
plt.title('Average Daily Wait Time on Event vs Non-Event Days')
plt.ylabel('Average Wait Time (minutes)')
plt.xlabel('Day Type')
plt.tight_layout()

# save figure
plt.savefig('external_factors_analysis/event_figures/event_vs_non_event.png', dpi=300, bbox_inches='tight')
plt.show()

# summary statistics of the wait time on event vs non-event days
event_summary = daily_avg.groupby('Event_Label')['wait_time'].describe()
event_summary = event_summary.reset_index()
print(event_summary)