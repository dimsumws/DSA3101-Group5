import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from faker import Faker
from faker.providers import BaseProvider
import re
from datetime import datetime

class USSAttendanceProvider(BaseProvider):
    def __init__(self, generator, model, model_features, residual_std, year_attendance_dict):
        super().__init__(generator)
        self.model = model
        self.model_features = model_features
        self.residual_std = residual_std
        self.year_attendance_dict = year_attendance_dict

    def generate_attendance(self, row):
        year = row["Year"]
        if year in self.year_attendance_dict and self.year_attendance_dict[year] == 0:
            return 0

        X = np.array([row.get(f, 0) for f in self.model_features]).reshape(1, -1)
        base = self.model.predict(X)[0]

        # Contextual boost logic
        boost = 1.0
        if row.get("IsSchoolHolidayFlag", 0):
            boost += np.random.uniform(0.05, 0.15)
        if row.get("IsPublicHolidayFlag", 0):
            boost += np.random.uniform(0.1, 0.25)
        if row.get("SpecialEventFlag", 0):
            boost += np.random.uniform(0.2, 0.35)
        if row.get("DayOfWeek") in [5, 6]:  # Saturday, Sunday
            boost += np.random.uniform(0.1, 0.2)

        # Rain effect
        rainfall = row.get("RainfallVal", 0)
        if rainfall > 5:
            boost -= np.random.uniform(0.05, 0.2)

        # Add scaled noise
        noise_scale = self.residual_std * np.random.uniform(0.9, 1.5)
        noise = np.random.normal(0, noise_scale)

        attendance = base * boost + noise
        return int(max(0, round(attendance)))
def main():
    year_attendance_dict = {
        2017: 4220000, 2018: 4400000, 2019: 4500000,
        2020: 1098000, 2021: 1200000, 2022: 2100000,
        2023: 3500000, 2024: 4200000, 2025: 4600000
    }

    # Load core dataset
    df = pd.read_csv("../../uss_wait_times/augmented_wait_time_data/2017_to_2025_synthetic_wait_times_final.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["DayOfWeek"] = df["Date"].dt.dayofweek

    if "Actual" not in df.columns:
        df["Actual"] = np.nan

    df_weather = pd.read_csv("../../Meteorological/datasets/final_data/merged_weather_data_clean.csv")
    df_weather.rename(columns={"date": "Date"}, inplace=True)
    df_weather["Date"] = pd.to_datetime(df_weather["Date"], dayfirst=True)

    df_holiday = pd.read_csv("../../Events/Holidays/datasets/daily_school_holidays_combined_updated.csv")
    df_holiday.rename(columns={"date": "Date"}, inplace=True)
    df_holiday["Date"] = pd.to_datetime(df_holiday["Date"], dayfirst=True)

    df_event = pd.read_csv("../../Events/EventData/supplementary_event_data_2016_2025.csv")
    df_event = df_event.drop(columns=["Event_Description"], errors='ignore')
    df_event["Date"] = pd.to_datetime(df_event["Date"], format='mixed', dayfirst=True, errors='coerce')


    df_tourism = pd.read_csv("../Final/tourism_counts/tourism.csv")
    month_map = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
    tourism_dict = {}
    for col in df_tourism.columns:
        if col != "Region":
            match = re.match(r"(\d{4})([A-Za-z]{3})", col)
            if match:
                y, m = match.groups()
                tourism_dict[(int(y), month_map[m])] = df_tourism[col].sum()

    # Merge all external features
    df = pd.merge(df, df_weather, on="Date", how="left")
    df = pd.merge(df, df_holiday, on="Date", how="left")
    df = pd.merge(df, df_event, on="Date", how="left")

    df["MonthStr"] = df["Date"].dt.to_period("M")
    tourism_weighted = {}
    for (year, month), total_visitors in tourism_dict.items():
        days_in_month = pd.Period(f"{year}-{month:02d}").days_in_month
        tourism_weighted[(year, month)] = total_visitors / days_in_month
    df["TourismValue"] = df.apply(lambda r: tourism_weighted.get((r["Year"], r["Month"]), 0), axis=1)

    df["IsPublicHolidayFlag"] = df["IsPublicHoliday"].fillna(False).astype(bool).astype(int) if "IsPublicHoliday" in df else 0
    df["IsSchoolHolidayFlag"] = df["IsSchoolHoliday"].fillna(False).astype(bool).astype(int) if "IsSchoolHoliday" in df else 0
    df["SpecialEventFlag"] = df["SomeEventFlag"].fillna(False).astype(bool).astype(int) if "SomeEventFlag" in df else 0
    df["RainfallVal"] = df["Rainfall_mm"].fillna(0) if "Rainfall_mm" in df else 0

    df_train = df[df["Year"].isin(year_attendance_dict.keys())].copy()
    df_train["WaitWeight"] = df_train["Actual"].fillna(0)
    df_train["TourismWeight"] = df_train["TourismValue"]
    df_train["Weight"] = df_train["WaitWeight"] * 0.6 + df_train["TourismWeight"] * 0.4
    df_train["WeightSumByYear"] = df_train.groupby("Year")["Weight"].transform("sum")
    df_train["WeightProportion"] = df_train["Weight"] / df_train["WeightSumByYear"]
    df_train["USSAttendance"] = df_train["WeightProportion"] * df_train["Year"].map(year_attendance_dict)

    exclude = {"Date", "Prediction", "Actual", "Delta", "Comment", "USSAttendance", "MonthStr"}
    model_features = [c for c in df_train.columns if c not in exclude and df_train[c].dtype in [np.int64, np.float64]]
    print("Features used:", model_features)

    # Model training
    from sklearn.model_selection import GridSearchCV
    X = df_train[model_features].fillna(0)
    y = df_train["USSAttendance"]
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [None, 10],
        'min_samples_split': [2],
        'min_samples_leaf': [1]
    }
    grid_search = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=3, scoring='neg_mean_squared_error', n_jobs=-1, verbose=1)
    grid_search.fit(X, y)
    model = grid_search.best_estimator_
    model.fit(X, y)
    residual_std = np.std(y - model.predict(X))

    # Generate attendance with variation
    print("Generating daily attendance data... and initializing Faker")
    fake = Faker()
    provider = USSAttendanceProvider(fake, model, model_features, residual_std, year_attendance_dict)
    fake.add_provider(provider)

    cb_start = pd.to_datetime("2020-04-07")
    cb_end = pd.to_datetime("2020-06-30")
    df["USSAttendance"] = df.apply(
        lambda r: int(round((r["Actual"] * 0.7 + r["TourismValue"] * 0.3) * np.random.uniform(0.5, 1.2)))
        if cb_start <= r["Date"] <= cb_end else provider.generate_attendance(r),
        axis=1
    )

    # Final normalization to yearly target
    df["TotalByYear"] = df.groupby("Year")["USSAttendance"].transform("sum")
    today = pd.Timestamp(datetime.today().date())
    df["DaysElapsed"] = df["Date"].le(today).astype(int)
    df["YearTotalDays"] = df["Date"].dt.year.map(lambda y: 366 if pd.Timestamp(f"{y}-12-31").is_leap_year else 365)
    df["TargetTotal"] = df.apply(
        lambda r: (year_attendance_dict[r["Year"]] * df[df["Year"] == r["Year"]]["DaysElapsed"].sum() / r["YearTotalDays"])
        if r["Year"] == 2025 else year_attendance_dict[r["Year"]],
        axis=1
    )
    df["ScalingFactor"] = df["TargetTotal"] / df["TotalByYear"]
    df["USSAttendance"] = (df["USSAttendance"] * df["ScalingFactor"]).round().astype(int)

    df[["Date", "USSAttendance"]].to_csv("../Final/synthetic_data_daily_attendance/synthetic_daily_attendance_2017_2025.csv", index=False)

if __name__ == "__main__":
    main()
