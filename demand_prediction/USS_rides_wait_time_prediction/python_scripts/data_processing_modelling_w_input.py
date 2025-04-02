import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.compose import ColumnTransformer
from math import sqrt
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

weather_data_path    = '../../../data/Meteorological/datasets/final_data/24_hr_weather_forecast_data.csv'
school_hols_path = '../../../data/Events/Holidays/datasets/daily_school_holidays_combined_updated.csv'
event_data_path      = '../../../data/Events/EventData/supplementary_event_data_2016_2025.csv'
rainfall_data_path   = '../../../data/Meteorological/datasets/final_data/sentosa_rainfall_5min_int.csv'

def train_ride_model(ride_name: str):
    # Trains a Gradient Boosting model for a given ride_name

    print(f"Training Model for Ride: {ride_name} ")

    ride_data_path = f'../../../data/uss_ride_wait_times/merged_{ride_name}.csv'

    # Load all necessary data
    df_ride   = pd.read_csv(ride_data_path)
    df_weather= pd.read_csv(weather_data_path)
    df_school = pd.read_csv(school_hols_path)
    df_events = pd.read_csv(event_data_path)
    df_rain   = pd.read_csv(rainfall_data_path)

    # preprocess ride data (labelled data)
    df_ride = df_ride[df_ride["Date/Time"] != "Date/Time"]  # remove repeated headers if any
    df_ride.rename(columns={"Date/Time": "datetime", "Wait Time": "wait_time"}, inplace=True)
    df_ride["wait_time"] = pd.to_numeric(df_ride["wait_time"], errors="coerce")
    df_ride.dropna(subset=["wait_time"], inplace=True)
    df_ride["datetime"] = pd.to_datetime(df_ride["datetime"], errors="coerce")
    df_ride.dropna(subset=["datetime"], inplace=True)

    # drop the ride column as it is not used in model training
    if "Ride" in df_ride.columns:
        df_ride.drop(columns=["Ride"], inplace=True)

    # reprocess weather => rename valid_start -> datetime
    df_weather["valid_start"] = pd.to_datetime(df_weather["valid_start"], errors="coerce")
    df_weather["valid_end"]   = pd.to_datetime(df_weather["valid_end"],   errors="coerce")
    df_weather.dropna(subset=["valid_start"], inplace=True)
    df_weather.rename(columns={"valid_start": "datetime"}, inplace=True)
    if df_weather["datetime"].dtype == "datetime64[ns, UTC+08:00]":
        df_weather["datetime"] = df_weather["datetime"].dt.tz_localize(None)
    df_weather.drop(columns=["valid_end"], errors="ignore", inplace=True)

    # rainfall => rename timestamp -> datetime
    df_rain.rename(columns={"timestamp": "datetime"}, inplace=True)
    df_rain["datetime"] = pd.to_datetime(df_rain["datetime"], errors="coerce")
    df_rain.dropna(subset=["datetime"], inplace=True)
    if df_rain["datetime"].dtype == "datetime64[ns, UTC+08:00]":
        df_rain["datetime"] = df_rain["datetime"].dt.tz_localize(None)
    df_rain = df_rain[["datetime","rainfall"]]

    # merge Ride and Weather (Left join on 'datetime')
    df_merged = pd.merge(df_ride, df_weather, on="datetime", how="left"
    )

    # merge 5-min rainfall data on 'datetime'
    df_merged = pd.merge(df_merged, df_rain,on="datetime",how="left"
    )

    # merge daily data (holidays/events)

    df_merged["date"] = df_merged["datetime"].dt.date

    df_school["date"] = pd.to_datetime(df_school["date"], format="%d/%m/%Y", errors="coerce").dt.date
    if "holiday_flag" in df_school.columns:
        df_merged = df_merged.merge(
            df_school[["date","holiday_flag"]],
            on="date",
            how="left"
        )
        df_merged["holiday_flag"] = df_merged["holiday_flag"].fillna(0)
    else:
        df_merged["holiday_flag"] = 0

    if "Date" in df_events.columns:
        df_events.rename(columns={"Date": "date"}, inplace=True)
    df_events["date"] = pd.to_datetime(df_events["date"], errors="coerce").dt.date
    merge_cols = [c for c in df_events.columns if c != "date"]
    df_merged = df_merged.merge(df_events[["date"] + merge_cols], on="date", how="left")

    # create lag & rolling features due to time series data
    df_merged = df_merged.sort_values("datetime")
    df_merged["wait_time_lag1"] = df_merged["wait_time"].shift(1)
    df_merged["wait_time_lag2"] = df_merged["wait_time"].shift(2)
    df_merged["wait_time_rolling3"] = df_merged["wait_time"].rolling(window=3).mean()
    df_merged["wait_time_rolling6"] = df_merged["wait_time"].rolling(window=6).mean()
    df_merged.fillna(0, inplace=True)

    target = "wait_time"

    for col in df_merged.columns:
        if df_merged[col].dtype in [np.float64, np.int64]:
            df_merged[col] = df_merged[col].fillna(0)
        elif df_merged[col].dtype == object:
            df_merged[col] = df_merged[col].fillna("missing")

    if "wind_direction" in df_merged.columns:
        df_merged["wind_direction"] = df_merged["wind_direction"].astype(str)

    exclude_cols = ["datetime", "date", "valid_end", target]
    X = df_merged.drop(columns=[c for c in exclude_cols if c in df_merged.columns], errors="ignore")
    y = df_merged[target]

    # Distinguish numeric vs categorical
    categorical_cols = ["wind_direction"] if "wind_direction" in X.columns else []
    numeric_cols = [
        c for c in X.columns
        if c not in categorical_cols
        and X[c].dtype in [np.float64, np.int64]
    ]


    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler",  StandardScaler())
    ])
    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols)
        ],
        remainder="drop"
    )
    X_processed = preprocessor.fit_transform(X)

    # perform Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, shuffle=False)

    # Train Gradient Boosting model and hyperparameter finetuning
    model_params = {
        "GradientBoosting": {
            "model": GradientBoostingRegressor(random_state=42),
            "params": {
                "n_estimators": [50, 500],
                "learning_rate": [0.05, 0.1],
                "max_depth": [3, 5],
                "min_samples_split": [2, 5]
            }
        }
    }

    results = {}
    for model_name, mp in model_params.items():
        print(f"\nModel: {model_name} (ride={ride_name})")
        reg = mp["model"]
        param_dist = mp["params"]

        rs = RandomizedSearchCV(
            reg,
            param_distributions=param_dist,
            n_iter=5,
            cv=3,
            scoring="neg_mean_squared_error",
            random_state=42,
            n_jobs=-1
        )
        rs.fit(X_train, y_train)
        best_model = rs.best_estimator_

        y_pred_train = best_model.predict(X_train)
        y_pred_test  = best_model.predict(X_test)

        train_rmse = sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse  = sqrt(mean_squared_error(y_test,  y_pred_test))
        train_r2   = r2_score(y_train, y_pred_train)
        test_r2    = r2_score(y_test,  y_pred_test)

        print(f"Best Params: {rs.best_params_}")
        print(f"Train RMSE: {train_rmse:.3f} & Test RMSE: {test_rmse:.3f}")
        print(f"Train R²: {train_r2:.3f} & Test R²: {test_r2:.3f}")

        results[model_name] = {
            "Best Params": rs.best_params_,
            "Train RMSE": train_rmse,
            "Train R2": train_r2,
            "Test RMSE": test_rmse,
            "Test R2": test_r2
        }

    best_params  = rs.best_params_
    y_pred       = best_model.predict(X_test)
    final_rmse   = sqrt(mean_squared_error(y_test, y_pred))
    final_r2     = r2_score(y_test, y_pred)

    subfolder = f"../models/{ride_name}_gb_model"
    os.makedirs(subfolder, exist_ok=True)

    model_path = f"{subfolder}/best_{ride_name}_gb_model.pkl"

    plt.figure(figsize=(8, 6))

    sns.regplot(
        x=y_test,
        y=y_pred,
          scatter_kws={'alpha': 0.5, 'edgecolor': 'k'},
        line_kws={'color': 'red', 'linestyle': '--'},
        x_jitter=0.8,
        y_jitter=0.8,
        fit_reg=False
    )

    plt.plot(
        [y_test.min(), y_test.max()],
        [y_test.min(), y_test.max()],
        'r--', lw=2
    )

    plt.xlabel("Actual Wait Time (min)")
    plt.ylabel("Predicted Wait Time (min)")
    plt.title(f"{ride_nameq} Ride Model\nRMSE={final_rmse:.2f}, R²={final_r2:.3f}")

    plt.tight_layout()
    plt.savefig(f"{subfolder}/best_{ride_name}_gb_model.png")
    plt.close()

    joblib.dump(best_model, model_path)
    print(f"Model and plot saved in: {subfolder}")

    importances = best_model.feature_importances_
    cat_pipeline = preprocessor.named_transformers_["cat"].named_steps["onehot"]
    numeric_feature_names = numeric_cols
    cat_feature_names = []
    if categorical_cols:
        cat_feature_names = cat_pipeline.get_feature_names_out(categorical_cols)

    all_feature_names = list(numeric_feature_names) + list(cat_feature_names)

    feat_impt_df = pd.DataFrame({
        "feature": all_feature_names,
        "importance": importances
    }).sort_values("importance", ascending=False)

    plt.figure(figsize=(8, 6))
    sns.barplot(data=feat_impt_df, x="importance", y="feature")
    plt.title(f"{ride_name.capitalize()} Feature Importances")
    plt.tight_layout()
    plt.savefig(f"{subfolder}/best_{ride_name}_feature_importance.png")
    plt.close()
    
if __name__ == "__main__":
    # Prompt user for ride name in terminal
    ride_input = input("Enter the ride name (e.g. 'minionmayhem'): ")
    train_ride_model(ride_input)
