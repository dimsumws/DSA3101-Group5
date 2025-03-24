#!/usr/bin/env python3

import pandas as pd
import numpy as np
import re
from faker import Faker
from faker.providers import BaseProvider
from sklearn.linear_model import LinearRegression

class USSWaitTimeProvider(BaseProvider):
    def __init__(
        self, 
        generator,
        model_features,
        model_reg,
        residual_std,
        real_deltas
    ):
        super().__init__(generator)
        self.model_features = model_features
        self.model_reg = model_reg
        self.residual_std = residual_std
        self.real_deltas = real_deltas
        self.circuit_breaker_start = pd.to_datetime("2020-04-07")
        self.circuit_breaker_end   = pd.to_datetime("2020-06-30")
        self.partial_start = pd.to_datetime("2020-07-01")
        self.partial_end   = pd.to_datetime("2021-02-22")

    def is_in_circuit_breaker(self, date_val):
        return self.circuit_breaker_start <= date_val <= self.circuit_breaker_end

    def is_in_partial_capacity(self, date_val):
        return self.partial_start <= date_val <= self.partial_end

    def generate_actual(self, row):
        date_val = row["Date"]
        if self.is_in_circuit_breaker(date_val):
            return 0
        X_features = []
        for f in self.model_features:
            val = row.get(f, 0)
            if val is None:
                val = 0
            X_features.append(val)
        X_features = np.array(X_features).reshape(1, -1)
        base_pred = self.model_reg.predict(X_features)[0]
        noise = np.random.normal(0, self.residual_std)
        raw_val = base_pred + noise
        if self.is_in_partial_capacity(date_val):
            raw_val *= 0.3
        raw_val = max(raw_val, 0)
        return int(round(raw_val))

    def generate_prediction(self, actual, date_val):
        if self.is_in_circuit_breaker(date_val):
            return (0, 0, "Predicted")
        if len(self.real_deltas) == 0:
            return (actual, 0, "Predicted")
        delta_samp = np.random.choice(self.real_deltas)
        raw_pred   = actual + delta_samp
        raw_pred = max(raw_pred, 0)
        pred_rounded = int(round(raw_pred))
        final_delta  = pred_rounded - actual
        if final_delta == 0:
            cmt = "Predicted"
        elif final_delta > 0:
            cmt = "Over-Predicted"
        else:
            cmt = "Under-Predicted"
        return (pred_rounded, final_delta, cmt)

def main():
    df_wait = pd.read_csv("../cleaned_data_2022_2025/2022_to_2025_wait_times_cleaned.csv")
    df_wait["Date"] = pd.to_datetime(df_wait["Date"])
    needed = {"Date","Prediction","Actual","Delta","Comment"}

    df_wait["DayOfWeek"] = df_wait["Date"].dt.dayofweek
    df_wait["Delta"] = df_wait["Prediction"] - df_wait["Actual"]

    df_tourism = pd.read_csv("../../singapore_tourism_data/Final/tourism_counts/tourism.csv")
    month_map = {
        'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
        'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12
    }
    def parse_year_mon(c):
        pat = re.match(r'^(\d{4})(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$', c)
        if pat:
            y_str, mo_str = pat.groups()
            return int(y_str), month_map[mo_str]
        return None
    tourism_dict = {}
    for col in df_tourism.columns:
        if col != "Region":
            parsed = parse_year_mon(col)
            if parsed:
                tourism_dict[parsed] = df_tourism[col].sum()

    df_wait["Year"] = df_wait["Date"].dt.year
    df_wait["Month"] = df_wait["Date"].dt.month

    df_holiday = pd.read_csv("../../Events/Holidays/datasets/daily_school_holidays_combined_updated.csv")
    if "Date" not in df_holiday.columns:
        if "date" in df_holiday.columns:
            df_holiday.rename(columns={"date": "Date"}, inplace=True)
    df_holiday["Date"] = pd.to_datetime(df_holiday["Date"], dayfirst=True)

    df_weather = pd.read_csv("../../Meteorological/datasets/final_data/merged_weather_data_clean.csv")
    if "Date" not in df_weather.columns:
        if "date" in df_weather.columns:
            df_weather.rename(columns={"date": "Date"}, inplace=True)
    df_weather["Date"] = pd.to_datetime(df_weather["Date"], dayfirst=True)

    df_context = pd.merge(df_holiday, df_weather, on="Date", how="outer")
    all_dates = pd.date_range("2017-01-01","2025-02-22",freq="D")
    df_cal = pd.DataFrame({"Date": all_dates})
    df_cal["Year"] = df_cal["Date"].dt.year
    df_cal["Month"] = df_cal["Date"].dt.month
    df_cal["DayOfWeek"] = df_cal["Date"].dt.dayofweek
    df_merged = pd.merge(df_cal, df_wait, on="Date", how="left", suffixes=("","_real"))
    df_merged = pd.merge(df_merged, df_context, on="Date", how="left")

    df_wait_merged = df_merged[~df_merged["Actual"].isna()].copy()

    def tourism_for_row(row):
        y, m = row["Year"], row["Month"]
        return tourism_dict.get((y,m), 0)
    df_wait_merged["TourismValue"] = df_wait_merged.apply(tourism_for_row, axis=1)

    if "IsPublicHoliday" in df_wait_merged.columns:
        df_wait_merged["IsPublicHolidayFlag"] = df_wait_merged["IsPublicHoliday"].fillna(False).astype(bool).astype(int)
    else:
        df_wait_merged["IsPublicHolidayFlag"] = 0

    if "IsSchoolHoliday" in df_wait_merged.columns:
        df_wait_merged["IsSchoolHolidayFlag"] = df_wait_merged["IsSchoolHoliday"].fillna(False).astype(bool).astype(int)
    else:
        df_wait_merged["IsSchoolHolidayFlag"] = 0

    if "SomeEventFlag" in df_wait_merged.columns:
        df_wait_merged["SpecialEventFlag"] = df_wait_merged["SomeEventFlag"].fillna(False).astype(bool).astype(int)
    else:
        df_wait_merged["SpecialEventFlag"] = 0

    if "Rainfall_mm" in df_wait_merged.columns:
        df_wait_merged["RainfallVal"] = df_wait_merged["Rainfall_mm"].fillna(0)
    else:
        df_wait_merged["RainfallVal"] = 0

    model_features = ["DayOfWeek","TourismValue","IsPublicHolidayFlag","IsSchoolHolidayFlag","SpecialEventFlag","RainfallVal"]
    
    from sklearn.linear_model import LinearRegression
    X = df_wait_merged[model_features].fillna(0)
    y = df_wait_merged["Actual"].values
    model_reg = LinearRegression()
    model_reg.fit(X, y)
    y_pred = model_reg.predict(X)
    residuals = y - y_pred
    residual_std = np.std(residuals)
    real_deltas = df_wait_merged["Delta"].dropna().values

    from faker import Faker
    fake = Faker()

    provider = USSWaitTimeProvider(
        generator = fake,
        model_features = model_features,
        model_reg = model_reg,
        residual_std = residual_std,
        real_deltas = real_deltas
    )
    fake.add_provider(provider)

    missing_mask = df_merged["Actual"].isna()
    syn_rows = df_merged[missing_mask].copy()

    def generate_synthetic_row(r):
        actual_val = provider.generate_actual(r)
        pred_val, delt, cmt = provider.generate_prediction(actual_val, r["Date"])
        return pd.Series([actual_val, pred_val, delt, cmt])

    syn_rows[["Actual","Prediction","Delta","Comment"]] = syn_rows.apply(generate_synthetic_row, axis=1)
    df_existing = df_merged[~missing_mask].copy()
    df_final = pd.concat([df_existing, syn_rows], ignore_index=True)
    df_final.sort_values("Date", inplace=True)
    df_final = df_final[["Date","Prediction","Actual","Delta","Comment"]]
    df_final.to_csv("../augmented_wait_time_data/2017_to_2025_synthetic_wait_times_v2.csv", index=False)

if __name__ == "__main__":
    main()
