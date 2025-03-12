import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Relative path from src folder to dataset in data folder
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "cleaned_2024_wait_times.csv")

# Load dataset
df = pd.read_csv(data_path)

# Convert 'date' to a proper datetime format
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Extract hour from 'time' for daily trend analysis
df['hour'] = pd.to_datetime(df['time'], format="%H:%M:%S", errors='coerce').dt.hour

# Extract month name from 'date' for seasonality analysis
df['month'] = df['date'].dt.month_name()

# Define the correct order of months
month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)

# Compute average wait time per month (seasonality)
monthly_trends = df.groupby('month')['wait_time'].mean().reset_index()

# Compute average wait time per hour (daily trends)
hourly_trends = df.groupby('hour')['wait_time'].mean().reset_index()

# Plot monthly trends
sns.barplot(data=monthly_trends, x='month', y='wait_time')
plt.title("Average Crowd Waiting Time by Month")
plt.show()

# Plot hourly trends
sns.lineplot(data=hourly_trends, x='hour', y='wait_time', marker='o')
plt.title("Average Crowd Waiting Time by the Hour")
plt.show()