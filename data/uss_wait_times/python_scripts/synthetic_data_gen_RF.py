import pandas as pd
import numpy as np
import re
from sklearn.ensemble import RandomForestRegressor
from faker import Faker
from faker.providers import BaseProvider
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

class USSWaitTimeProvider(BaseProvider):
    def __init__(self, generator, model_features, model_reg, residual_std, real_deltas):
        super().__init__(generator)
        self.model_features = model_features
        self.model_reg = model_reg
        self.residual_std = residual_std
        self.real_deltas = real_deltas
        self.circuit_breaker_start = pd.to_datetime("2020-04-07")
        self.circuit_breaker_end = pd.to_datetime("2020-06-30")
        self.partial_start = pd.to_datetime("2020-07-01")
        self.partial_end = pd.to_datetime("2021-02-22")

    def is_in_circuit_breaker(self, date_val):
        return self.circuit_breaker_start <= date_val <= self.circuit_breaker_end

    def is_in_partial_capacity(self, date_val):
        return self.partial_start <= date_val <= self.partial_end

    def generate_actual(self, row):
        date_val = row["Date"]
        if self.is_in_circuit_breaker(date_val):
            return 0
        X_features = np.array([row.get(f, 0) for f in self.model_features]).reshape(1, -1)
        base_pred = self.model_reg.predict(X_features)[0]
        noise = np.random.normal(0, self.residual_std)
        raw_val = base_pred + noise
        if self.is_in_partial_capacity(date_val):
            raw_val *= 0.3
        return int(round(max(raw_val, 0)))

    def generate_prediction(self, actual, date_val):
        if self.is_in_circuit_breaker(date_val):
            return (0, 0, "Predicted")
        if len(self.real_deltas) == 0:
            return (actual, 0, "Predicted")
        delta_samp = np.random.choice(self.real_deltas)
        raw_pred = max(actual + delta_samp, 0)
        pred_rounded = int(round(raw_pred))
        delta = pred_rounded - actual
        comment = "Predicted" if delta == 0 else ("Over-Predicted" if delta > 0 else "Under-Predicted")
        return (pred_rounded, delta, comment)

def main():
    df_wait = pd.read_csv("../cleaned_data_2022_2025/2022_to_2025_wait_times_cleaned.csv")
    df_wait["Date"] = pd.to_datetime(df_wait["Date"])
    df_wait["DayOfWeek"] = df_wait["Date"].dt.dayofweek
    df_wait["Year"] = df_wait["Date"].dt.year
    df_wait["Month"] = df_wait["Date"].dt.month
    df_wait["Delta"] = df_wait["Prediction"] - df_wait["Actual"]

    df_tourism = pd.read_csv("../../singapore_tourism_data/Final/tourism_counts/tourism.csv")
    month_map = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}

    def parse_year_mon(c):
        match = re.match(r"(\d{4})([A-Za-z]{3})", c)
        if match:
            y, m = match.groups()
            return int(y), month_map[m]
        return None

    tourism_dict = {}
    for col in df_tourism.columns:
        if col != "Region":
            parsed = parse_year_mon(col)
            if parsed:
                tourism_dict[parsed] = df_tourism[col].sum()

    df_holiday = pd.read_csv("../../Events/Holidays/datasets/daily_school_holidays_combined_updated.csv")
    df_holiday.rename(columns={"date": "Date"}, inplace=True)
    df_holiday["Date"] = pd.to_datetime(df_holiday["Date"], dayfirst=True)

    df_weather = pd.read_csv("../../Meteorological/datasets/final_data/merged_weather_data_clean.csv")
    df_weather.rename(columns={"date": "Date"}, inplace=True)
    df_weather["Date"] = pd.to_datetime(df_weather["Date"], dayfirst=True)

    df_event = pd.read_csv("../../Events/EventData/supplementary_event_data_2016_2025.csv")
    df_event = df_event.drop(columns=["Event_Description"], errors="ignore")
    df_event["Date"] = pd.to_datetime(df_event["Date"], format='mixed', dayfirst=True, errors="coerce")
    df_event = df_event.dropna(subset=["Date"])

    df_context = pd.merge(df_holiday, df_weather, on="Date", how="outer")
    df_cal = pd.DataFrame({"Date": pd.date_range("2017-01-01", "2025-02-23", freq="D")})
    df_cal["Year"] = df_cal["Date"].dt.year
    df_cal["Month"] = df_cal["Date"].dt.month
    df_cal["DayOfWeek"] = df_cal["Date"].dt.dayofweek

    df_merged = pd.merge(df_cal, df_wait, on="Date", how="left")
    df_merged = pd.merge(df_merged, df_context, on="Date", how="left")

    df_merged["Year"] = df_merged["Date"].dt.year
    df_merged["Month"] = df_merged["Date"].dt.month
    df_merged["DayOfWeek"] = df_merged["Date"].dt.dayofweek

    def tourism_for_row(row):
        return tourism_dict.get((row["Year"], row["Month"]), 0)

    df_merged["TourismValue"] = df_merged.apply(tourism_for_row, axis=1)
    df_merged["IsPublicHolidayFlag"] = df_merged["IsPublicHoliday"].fillna(False).astype(bool).astype(int) if "IsPublicHoliday" in df_merged else 0
    df_merged["IsSchoolHolidayFlag"] = df_merged["IsSchoolHoliday"].fillna(False).astype(bool).astype(int) if "IsSchoolHoliday" in df_merged else 0
    df_merged["SpecialEventFlag"] = df_merged["SomeEventFlag"].fillna(False).astype(bool).astype(int) if "SomeEventFlag" in df_merged else 0
    df_merged["RainfallVal"] = df_merged["Rainfall_mm"].fillna(0) if "Rainfall_mm" in df_merged else 0

    exclude_cols = {"Date", "Actual", "Prediction", "Delta", "Comment", "Year", "Month"}
    model_features = [col for col in df_merged.columns 
                  if col not in exclude_cols and df_merged[col].dtype in [np.int64, np.float64]]

    print("Features used for training:", model_features)
    df_train = df_merged[~df_merged["Actual"].isna()].copy()
    X_train = df_train[model_features].fillna(0)
    y_train = df_train["Actual"]

    model_reg = RandomForestRegressor(n_estimators=100, random_state=42)
    model_reg.fit(X_train, y_train)
    residuals = y_train - model_reg.predict(X_train)
    residual_std = np.std(residuals)
    real_deltas = df_train["Delta"].dropna().values

    fake = Faker()
    provider = USSWaitTimeProvider(fake, model_features, model_reg, residual_std, real_deltas)
    fake.add_provider(provider)

    df_syn = df_merged[df_merged["Actual"].isna()].copy()
    def generate_synthetic_row(r):
        actual = provider.generate_actual(r)
        prediction, delta, comment = provider.generate_prediction(actual, r["Date"])
        return pd.Series([actual, prediction, delta, comment], index=["Actual", "Prediction", "Delta", "Comment"])

    syn_results = df_syn.apply(generate_synthetic_row, axis=1)

    # Drop any of the result columns if they already exist in df_syn
    df_syn = df_syn.drop(columns=[col for col in ["Actual", "Prediction", "Delta", "Comment"] if col in df_syn.columns])
    df_syn = pd.concat([df_syn.reset_index(drop=True), syn_results.reset_index(drop=True)], axis=1)

    df_real = df_merged[~df_merged["Actual"].isna()].copy()
    df_final = pd.concat([df_real, df_syn], ignore_index=True)
    df_final.sort_values("Date", inplace=True)
    df_final = df_final[["Date", "Prediction", "Actual", "Delta", "Comment"]]

    df_final.to_csv("../augmented_wait_time_data/2017_to_2025_synthetic_wait_times_final.csv", index=False)

if __name__ == "__main__":
    main()