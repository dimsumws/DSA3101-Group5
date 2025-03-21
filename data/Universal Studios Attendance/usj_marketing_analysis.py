# create visualisations 1 and 2
# filter date function
# function that labels important years for usj
# visualisation 1: trend
# visualisation 2: bar plot of individual % change + table displaying % change

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def filter_df(*dfs, min_year=2009, max_year=2023):
    years_range = range(min_year, max_year+1) 
    res = ()
    for df in dfs:
        df = df[df['Year'].isin(years_range)]
        df.reset_index(drop=True, inplace=True)
        res += (df,)
    return res


def plot_YoY_change_bar(df, axes, i):
    # Determine the colors based on the percentage change
    colors = np.where(df['YoY_Change'] >= 0, 'skyblue', 'red')  # Blue for positive, red for negative
    
    # Plot the bar chart for YoY percentage change with specified colors
    axes[i].bar(df['Year'], df['YoY_Change'], color=colors)
    # axes[i].set_title('Japan Tourism Year-over-Year Percentage Change (2009-2023)')
    axes[i].set_xlabel('Year')
    axes[i].set_ylabel('Percentage Change (%)')
    axes[i].axhline(0, color='black', linewidth=0.8, linestyle='--')  # Reference line
    axes[i].grid(axis='y')  # Optional: Add grid lines for better readability


def absolute_trend_analysis(usj, tokyo_disney, japan_tourism):
    usj, tokyo_disney_filtered, japan_tourism_filtered = filter_df(usj, tokyo_disney, japan_tourism)
    
    # Plotting
    plt.figure(figsize=(12, 6))

    # Plot Japan Tourism
    plt.plot(japan_tourism_filtered['Year'], japan_tourism_filtered['num_visitors'], label='Japan Tourism', marker='o')

    # Plot USJ
    plt.plot(usj['Year'], usj['Attendance'], label='USJ Attendance', marker='o')

    # Plot Tokyo Disneyland
    plt.plot(tokyo_disney_filtered['Year'], tokyo_disney_filtered['Attendance'], label='Tokyo Disneyland Attendance', marker='o')

    # Adding title and labels
    plt.title('Trend in Japan Tourism (2009-2023)')
    plt.xlabel('Year')
    plt.ylabel('Number of Visitors')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Save the plot
    plt.savefig('absolute_trend.png')  # Save as PNG
    plt.show()
    plt.close()  # Clear the figure after saving


def YoY_change_analysis(usj, tokyo_disney, japan_tourism):
    dfs = filter_df(usj, tokyo_disney, japan_tourism)
    usj, tokyo_disney_filtered, japan_tourism_filtered = dfs
    
    # Calculate YoY percentage change for USJ
    usj['YoY_Change'] = usj['Attendance'].pct_change() * 100

    # Calculate YoY percentage change for Tokyo Disneyland
    tokyo_disney_filtered['YoY_Change'] = tokyo_disney_filtered['Attendance'].pct_change() * 100

    # Create a comparison DataFrame
    comparison_df = pd.DataFrame({
        'Year': usj['Year'],
        'USJ YoY Change (%)': usj['YoY_Change'],
        'Tokyo Disneyland YoY Change (%)': tokyo_disney_filtered['YoY_Change'],
        'Japan Tourism YoY Change (%)': japan_tourism_filtered['YoY_Change']
    })

    # Save the comparison table
    print(comparison_df)
    comparison_df.to_csv("YoY_Change_Comparison.csv", index=False)

    # Set up the bar charts
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 15))

    for i in range(len(dfs)):
        plot_YoY_change_bar(dfs[i], axes, i)

    # Adjust layout and save the YoY change comparison plot
    plt.tight_layout()
    plt.savefig('yoy_change_comparison.png')  # Save as PNG
    plt.show()
    plt.close()  # Clear the figure after saving3

