import pandas as pd
from datetime import datetime, timedelta

file_path = "daily_school_holidays_combined.csv"
df_daily_holidays = pd.read_csv(file_path)
holidays = {
    "2016": {
        "New Year's Day": ["1/1/2016"],
        "Chinese New Year": ["8/2/2016", "9/2/2016"],
        "Good Friday": ["25/3/2016"],
        "Labour Day": ["1/5/2016"],
        "Labour Day in Lieu": ["2/5/2016"],
        "Vesak Day": ["21/5/2016"],
        "Hari Raya Puasa": ["6/7/2016"],
        "National Day": ["9/8/2016"],
        "Hari Raya Haji": ["12/9/2016"],
        "Deepavali": ["29/10/2016"],
        "Christmas Day": ["25/12/2016"],
        "Term 1 Break": ["12/3/2016 to 20/3/2016"],
        "Term 2 Break": ["28/5/2016 to 26/6/2016"],
        "Term 3 Break": ["3/9/2016 to 11/9/2016"],
        "Year-End Break": ["19/11/2016 to 31/12/2016"],
    },
    "2017": {
        "New Year's Day": ["1/1/2017"],
        "Chinese New Year": ["28/1/2017", "29/1/2017"],
        "Good Friday": ["14/4/2017"],
        "Labour Day": ["1/5/2017"],
        "Vesak Day": ["10/5/2017"],
        "Hari Raya Puasa": ["25/6/2017", "26/6/2017"],
        "National Day": ["9/8/2017"],
        "Hari Raya Haji": ["1/9/2017"],
        "Deepavali": ["18/10/2017"],
        "Christmas Day": ["25/12/2017"],
        "Term 1 Break": ["11/3/2017 to 19/3/2017"],
        "Term 2 Break": ["27/5/2017 to 25/6/2017"],
        "Term 3 Break": ["2/9/2017 to 10/9/2017"],
        "Year-End Break": ["18/11/2017 to 31/12/2017"],
    },
    "2018": {
        "New Year's Day": ["1/1/2018"],
        "Chinese New Year": ["16/2/2018", "17/2/2018"],
        "Chinese New Year in Lieu": ["19/2/2018"],
        "Good Friday": ["30/3/2018"],
        "Labour Day": ["1/5/2018"],
        "Vesak Day": ["29/5/2018"],
        "Youth Day": ["2/7/2018"],
        "National Day": ["9/8/2018"],
        "National Day in Lieu": ["10/8/2018"],
        "Hari Raya Haji": ["22/8/2018"],
        "Deepavali": ["6/11/2018"],
        "Christmas Day": ["25/12/2018"],
        "Term 1 Break": ["10/3/2018 to 18/3/2018"],
        "Term 2 Break": ["26/5/2018 to 24/6/2018"],
        "Term 3 Break": ["1/9/2018 to 9/9/2018"],
        "Year-End Break": ["17/11/2018 to 31/12/2018"],
    },
}

df_daily_holidays["year"] = df_daily_holidays["year"].astype(str)
all_new_rows = []
for year in range(2016, 2019):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    holiday_dates = {}
    for holiday_name, date_entries in holidays[str(year)].items():
        for date_entry in date_entries:
            if "to" in date_entry:
                start_date_str, end_date_str = date_entry.split(" to ")
                start_date_range = datetime.strptime(start_date_str.strip(), "%d/%m/%Y")
                end_date_range = datetime.strptime(end_date_str.strip(), "%d/%m/%Y")

                # Iterate through date range and add to holiday dictionary
                current_date = start_date_range
                while current_date <= end_date_range:
                    holiday_dates[current_date.strftime("%d/%m/%Y")] = holiday_name
                    current_date += timedelta(days=1)
            else:
                # Handle standalone single day holidays
                date_obj = datetime.strptime(date_entry.strip(), "%d/%m/%Y")
                holiday_dates[date_obj.strftime("%d/%m/%Y")] = holiday_name

    # Iterate through all days in the year
    current_date = start_date
    while current_date <= end_date:
        formatted_date = current_date.strftime("%d/%m/%Y")  
        is_holiday = "1" if formatted_date in holiday_dates else "0"
        holiday_name = holiday_dates.get(formatted_date, "None")
        all_new_rows.append([str(year), formatted_date, is_holiday, holiday_name])
        current_date += timedelta(days=1)

df_new_holidays = pd.DataFrame(all_new_rows, columns=["year", "date", "holiday_flag", "holiday_category"])
df_updated = pd.concat([df_daily_holidays, df_new_holidays], ignore_index=True)
df_updated["date"] = pd.to_datetime(df_updated["date"], format="%d/%m/%Y")
df_updated = df_updated.sort_values(by=["date"]).reset_index(drop=True)
df_updated["date"] = df_updated["date"].dt.strftime("%d/%m/%Y")
sorted_file_path = "daily_school_holidays_combined_updated.csv"
df_updated.to_csv(sorted_file_path, index=False)
