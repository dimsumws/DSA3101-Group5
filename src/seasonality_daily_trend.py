import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "cleaned_2024_wait_times.csv")
df = pd.read_csv(data_path)

# Parse datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['parsed_time'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce')
df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['time'])
df['hour'] = df['parsed_time'].dt.hour
df['minute'] = df['parsed_time'].dt.minute

# Monthly trend data
df['month'] = df['date'].dt.month_name()
month_order = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)
monthly_trends = df.groupby('month')['wait_time'].mean().reset_index()

# Normal hours mask: 10:00 to 18:55
normal_mask = (
    ((df['hour'] > 10) & (df['hour'] < 18)) |
    ((df['hour'] == 10) & (df['minute'] >= 0)) |
    ((df['hour'] == 18) & (df['minute'] <= 55))
)
df_normal_cleaned = df[normal_mask].copy()

# Tag HHN dates
open_close_times = df.groupby('date')['datetime'].agg(['min', 'max']).reset_index()
open_close_times.columns = ['date', 'open_time', 'close_time']
open_close_times['close_hour'] = open_close_times['close_time'].dt.strftime('%H:%M')

hhn_start = pd.to_datetime("2024-09-27")
hhn_end = pd.to_datetime("2024-11-02")
open_close_times['is_hhn'] = (open_close_times['close_hour'] == '23:50') & \
                              (open_close_times['date'] >= hhn_start) & \
                              (open_close_times['date'] <= hhn_end)

df_normal_cleaned = df_normal_cleaned.merge(open_close_times[['date', 'is_hhn']], on='date', how='left')
df_hhn = df[(df['date'].isin(open_close_times[open_close_times['is_hhn']]['date'])) & (df['hour'] >= 19)]

# Group by hour
hourly_normal = df_normal_cleaned.groupby('hour')['wait_time'].mean().reset_index()
hourly_hhn = df_hhn.groupby('hour')['wait_time'].mean().reset_index()

# Monthly Plot
plt.figure(figsize=(10, 5))
sns.barplot(data=monthly_trends, x='month', y='wait_time', color='navy')
plt.title("USS Average Wait Time by Month in 2024")
plt.xlabel("Month")
plt.ylabel("Average Wait Time (mins)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Combined Plot: Normal + HHN
fig, axs = plt.subplots(2, 1, figsize=(10, 8))

# Normal day trend
sns.lineplot(data=hourly_normal, x='hour', y='wait_time', marker='o', color='steelblue', ax=axs[0])
axs[0].set_title("Hourly Average Wait Time in 2024 (Normal Days: 10am–7pm)")
axs[0].set_xlabel("Hour of Day")
axs[0].set_ylabel("Avg Wait Time (mins)")
axs[0].set_xticks(range(10, 19))
axs[0].grid(axis='y', linestyle='--', alpha=0.5)

# HHN trend
sns.lineplot(data=hourly_hhn, x='hour', y='wait_time', marker='o', color='darkred', ax=axs[1])
axs[1].set_title("Hourly Average Wait Time in 2024 (HHN: 7pm–12am)")
axs[1].set_xlabel("Hour of Day")
axs[1].set_ylabel("Avg Wait Time (mins)")
axs[1].set_xticks(range(19, 24))
axs[1].grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()