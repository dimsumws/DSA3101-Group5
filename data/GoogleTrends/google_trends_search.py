from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt

pytrends = TrendReq(hl='en-US', tz=8)
keywords = ["Universal Studios Singapore", "USS queue time", "Sentosa", "Universal Studios Tickets"]
timeframe = "2023-01-01 2025-02-28"

pytrends.build_payload(keywords, timeframe=timeframe, geo="SG")

trends_data = pytrends.interest_over_time()

if 'date' not in trends_data.columns:
    trends_data.reset_index(inplace=True)
trends_data['date'] = pd.to_datetime(trends_data['date'])
trends_data = trends_data.sort_values(by='date')
trends_data.fillna(method='ffill', inplace=True)
trends_data.set_index('date', inplace=True)
trends_data_daily = trends_data.resample('D').ffill().reset_index()

# Save to CSV
trends_data_daily.to_csv("uss_google_trends_2023_2025.csv", index=False)

plt.figure(figsize=(12,6))
for keyword in keywords:
    plt.plot(trends_data.index, trends_data[keyword], label=keyword)

plt.title("Google Trends Interest for Universal Studios Singapore (Jan 2023 - Feb 2025)")
plt.xlabel("Date")
plt.ylabel("Search Interest (0-100)")
plt.legend()
plt.xticks(rotation=45)
plt.grid()
plt.show()
plt.savefig('google_trends.png')