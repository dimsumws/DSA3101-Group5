import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re

# List of URLs and corresponding years
year_urls = {
    "2019": "https://www.moe.gov.sg/news/press-releases/20180815-school-terms-and-holidays-for-2019",
    "2020": "https://www.moe.gov.sg/news/press-releases/20190813-school-terms-and-holidays-for-2020",
    "2021": "https://www.moe.gov.sg/news/press-releases/20200817-school-terms-and-holidays-for-2021",
    "2022": "https://www.moe.gov.sg/news/press-releases/20210811-school-terms-and-holidays-for-2022",
    "2023": "https://www.moe.gov.sg/news/press-releases/20221019-school-terms-and-holidays-for-2023",
    "2024": "https://www.moe.gov.sg/news/press-releases/20230807-school-terms-and-holidays-for-2024",
    "2025": "https://www.moe.gov.sg/news/press-releases/20240812-school-terms-and-holidays-for-2025"
}

all_holidays = []
all_daily_holidays = []

for year_in_question, url in year_urls.items():
    print(f"Fetching data for {year_in_question}...")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Cannot Access Website for {year_in_question}!")
        continue

    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")

    headers = soup.find_all(['h2', 'h3', 'h4', 'strong', 'p'])
    valid_headers = {f"School Vacation {year_in_question}", f"Scheduled School Holidays {year_in_question}", f"Public Holidays {year_in_question}", f"School Holidays {year_in_question}"}
    filtered_holidays = []

    for header in headers:
        if header.text.strip() in valid_headers:
            next_element = header.find_next_sibling()
            while next_element and next_element.name not in ["table", "ul"]:
                next_element = next_element.find_next_sibling()
            
            if next_element and next_element.name == "table":
                rows = next_element.find_all("tr")
                for row in rows[1:]:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        holiday_name = cols[0].text.strip()
                        date_range = cols[1].text.strip()
                        date_range = re.sub(r'(\*+)', '', date_range).strip()  # Remove any leading asterisks
                        date_range = re.sub(r'(\d{1,2} [A-Za-z]+)\d+', r'\1', date_range)  # Remove footnote numbers
                        filtered_holidays.append([year_in_question, holiday_name, date_range])
    
    df_holidays = pd.DataFrame(filtered_holidays, columns=["Year", "Holiday Name", "Date Range"])
    all_holidays.append(df_holidays)

    holiday_dates = {}

    def clean_date(date_str):
        date_str = re.sub(r'[^A-Za-z0-9 ]', '', date_str)  # Remove special characters
        date_str = re.sub(r'([a-zA-Z]+)\d+', r'\1', date_str)  # Remove trailing numbers
        date_str = date_str.strip()
        return date_str

    for _, row in df_holidays.iterrows():
        name = row["Holiday Name"]
        date_range = row["Date Range"]

        try:
            if "to" in date_range:
                start_date_str, end_date_str = date_range.split(" to ")
            else:
                start_date_str = end_date_str = date_range  

            start_date_str = re.sub(r'^[A-Za-z]+ ', '', start_date_str).strip()
            end_date_str = re.sub(r'^[A-Za-z]+ ', '', end_date_str).strip()
            
            start_date_str = clean_date(start_date_str)
            end_date_str = clean_date(end_date_str)

            if len(start_date_str.split()) == 2:
                start_date_str += f" {year_in_question}"
            if len(end_date_str.split()) == 2:
                end_date_str += f" {year_in_question}"

            start_date = datetime.strptime(start_date_str, "%d %b %Y")
            end_date = datetime.strptime(end_date_str, "%d %b %Y")

            current_date = start_date
            while current_date <= end_date:
                holiday_dates[current_date.strftime("%Y-%m-%d")] = name
                current_date += timedelta(days=1)
        except Exception as e:
            print(f"Error processing holiday: {name} - {date_range} for {year_in_question}. Error: {e}")

    all_dates = []
    for i in range(365):
        date = datetime(int(year_in_question), 1, 1) + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        is_holiday = "1" if date_str in holiday_dates else "0"
        holiday_name = holiday_dates.get(date_str, "None")
        all_dates.append([year_in_question, date_str, is_holiday, holiday_name])

    df_daily = pd.DataFrame(all_dates, columns=["year", "date", "holiday_flag", "holiday_category"])
    all_daily_holidays.append(df_daily)

# Combine all years into one df
df_all_holidays = pd.concat(all_holidays, ignore_index=True)
df_all_daily = pd.concat(all_daily_holidays, ignore_index=True)

df_all_holidays.to_csv("school_holidays_combined.csv", index=False)
df_all_daily.to_csv("daily_school_holidays_combined.csv", index=False)

print("Combined school holidays saved to school_holidays_combined.csv!")
print("Combined daily school holiday flags saved to daily_school_holidays_combined.csv!")