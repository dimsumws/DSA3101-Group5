import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
from math import sqrt
import cvxpy as cp
from datetime import datetime, timedelta

from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score

def add_custom_css():
    st.markdown(
        """
        <style>
        body {
            background: url('https://raw.githubusercontent.com/travisbrown/misc-images/master/themepark_bg.jpg');
            background-size: cover;
            background-position: center;
            color: #fff;
        }
        .main, .block-container {
            background-color: rgba(0,0,0,0.5) !important;
            color: #f2f2f2 !important;
        }
        h1, h2, h3, h4 {
            color: #FFD700 !important;
            text-shadow: 1px 1px 2px #000;
        }
        button[data-baseweb="button"] {
            background-color: #FF6A6A !important;
            color: #fff !important;
            border-radius: 12px !important;
        }
        .css-1u0x2ww.e1ty961o2 {
            background-color: rgba(255,255,255,0.9) !important;
            color: #000 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def optimise_staffing(hourly_demand, total_staff, wait_priority, shift_hours):
    T = len(hourly_demand)
    S = cp.Variable(T, nonneg=True)

    forecast = hourly_demand["forecasted_wait_time"].values
    mx = np.max(forecast) if np.max(forecast)!=0 else 1
    demand_weights = forecast / mx
    target = total_staff * demand_weights

    c = 1
    u = wait_priority * 10
    v = 5

    under_alloc = cp.sum(cp.square(cp.pos(target - S)))
    over_alloc  = cp.sum(cp.square(cp.pos(S - target)))
    smoothness  = cp.norm(S[1:] - S[:-1], p=2)

    objective = cp.Minimize(
        c * cp.sum(S) + u * under_alloc + v * over_alloc + 0.1 * smoothness
    )
    min_staff = max(10, total_staff // T)
    constraints = [
        S >= min_staff,
        S <= total_staff,
        cp.sum(S) <= total_staff * shift_hours
    ]
    problem = cp.Problem(objective, constraints)
    result = problem.solve()

    if problem.status != "optimal":
        st.warning("Warning: Staff solver not optimal; using uniform fallback.")
        fallback = np.full(T, total_staff // T, dtype=int)
        return {"status": problem.status, "staff_allocation": fallback}
    return {"status": problem.status, "staff_allocation": S.value}

def train_ride_model(ride_name):
    ride_data_path     = f"data/uss_ride_wait_times/merged_{ride_name}.csv"
    weather_data_path  = "data/Meteorological/datasets/final_data/24_hr_weather_forecast_data.csv"
    school_hols_path   = "data/Events/Holidays/datasets/daily_school_holidays_combined_updated.csv"
    event_data_path    = "data/Events/EventData/supplementary_event_data_2016_2025.csv"
    rainfall_data_path = "data/Meteorological/datasets/final_data/sentosa_rainfall_5min_int.csv"

    st.write(f"**Training Ride Model**: {ride_name}")
    df_ride = pd.read_csv(ride_data_path)
    df_ride = df_ride[df_ride["Date/Time"]!="Date/Time"]
    df_ride.rename(columns={"Date/Time": "datetime", "Wait Time": "wait_time"}, inplace=True)
    df_ride["wait_time"] = pd.to_numeric(df_ride["wait_time"], errors="coerce")
    df_ride.dropna(subset=["wait_time"], inplace=True)
    df_ride["datetime"] = pd.to_datetime(df_ride["datetime"], errors="coerce")
    df_ride.dropna(subset=["datetime"], inplace=True)
    if "Ride" in df_ride.columns:
        df_ride.drop(columns=["Ride"], inplace=True)
    if df_ride["datetime"].dtype == "datetime64[ns, UTC+08:00]":
        df_ride["datetime"] = df_ride["datetime"].dt.tz_localize(None)

    # Weather
    df_weather = pd.read_csv(weather_data_path)
    df_weather["valid_start"] = pd.to_datetime(df_weather["valid_start"], errors="coerce")
    df_weather.dropna(subset=["valid_start"], inplace=True)
    df_weather.rename(columns={"valid_start":"datetime"}, inplace=True)
    if "valid_end" in df_weather.columns:
        df_weather.drop(columns=["valid_end"], inplace=True, errors="ignore")
    if df_weather["datetime"].dtype == "datetime64[ns, UTC+08:00]":
        df_weather["datetime"] = df_weather["datetime"].dt.tz_localize(None)

    # Rain
    df_rain = pd.read_csv(rainfall_data_path)
    df_rain.rename(columns={"timestamp": "datetime"}, inplace=True)
    df_rain["datetime"] = pd.to_datetime(df_rain["datetime"], errors="coerce")
    df_rain.dropna(subset=["datetime"], inplace=True)
    df_rain = df_rain[["datetime","rainfall"]]
    if df_rain["datetime"].dtype == "datetime64[ns, UTC+08:00]":
        df_rain["datetime"] = df_rain["datetime"].dt.tz_localize(None)

    # School hol
    df_school = pd.read_csv(school_hols_path)
    df_school["date"] = pd.to_datetime(df_school["date"], format="%d/%m/%Y", errors="coerce").dt.date

    # Events
    df_events = pd.read_csv(event_data_path)
    if "Date" in df_events.columns:
        df_events.rename(columns={"Date": "date"}, inplace=True)
    df_events["date"] = pd.to_datetime(df_events["date"], errors="coerce").dt.date

    # Merge
    df_ride_weather = pd.merge(df_ride, df_weather, on="datetime", how="left")
    df_ride_weather = pd.merge(df_ride_weather, df_rain, on="datetime", how="left")
    df_ride_weather["date"] = df_ride_weather["datetime"].dt.date
    df_ride_weather = df_ride_weather.merge(df_school[["date","holiday_flag"]], on="date", how="left")
    df_ride_weather["holiday_flag"] = df_ride_weather["holiday_flag"].fillna(0)
    merge_cols = [c for c in df_events.columns if c != "date"]
    df_ride_weather = df_ride_weather.merge(df_events[["date"]+merge_cols], on="date", how="left")

    df_ride_weather.sort_values("datetime", inplace=True)
    df_ride_weather["wait_time_lag1"] = df_ride_weather["wait_time"].shift(1)
    df_ride_weather["wait_time_lag2"] = df_ride_weather["wait_time"].shift(2)
    df_ride_weather["wait_time_rolling3"] = df_ride_weather["wait_time"].rolling(3).mean()
    df_ride_weather["wait_time_rolling6"] = df_ride_weather["wait_time"].rolling(6).mean()
    df_ride_weather.fillna(0, inplace=True)

    target = "wait_time"
    for c in df_ride_weather.columns:
        if df_ride_weather[c].dtype in [np.float64, np.int64]:
            df_ride_weather[c] = df_ride_weather[c].fillna(0)
        elif df_ride_weather[c].dtype == object:
            df_ride_weather[c] = df_ride_weather[c].fillna("missing")

    exclude = ["datetime", "date", "valid_end", target]
    X = df_ride_weather.drop(columns=[c for c in exclude if c in df_ride_weather.columns], errors="ignore")
    y = df_ride_weather[target]

    cat_cols = []
    if "wind_direction" in X.columns and X["wind_direction"].dtype == object:
        cat_cols.append("wind_direction")
    numeric_cols = [c for c in X.columns if c not in cat_cols and (X[c].dtype in [np.float64, np.int64])]

    numeric_transformer = Pipeline([
        ("imp", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler())
    ])
    cat_transformer = Pipeline([
        ("imp", SimpleImputer(strategy="constant", fill_value="missing")),
        ("ohe", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, numeric_cols),
        ("cat", cat_transformer, cat_cols)
    ], remainder="drop")

    X_processed = preprocessor.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed, y, test_size=0.2, shuffle=False
    )

    param_grid = {
        "n_estimators": [50, 200],
        "learning_rate":[0.05, 0.1],
        "max_depth": [3, 5],
        "min_samples_split":[2,5]
    }
    gb = GradientBoostingRegressor(random_state=42)
    rs = RandomizedSearchCV(gb, param_grid, n_iter=5, cv=3, scoring="neg_mean_squared_error", random_state=42, n_jobs=-1)
    rs.fit(X_train, y_train)
    best_model = rs.best_estimator_

    y_train_pred = best_model.predict(X_train)
    y_test_pred  = best_model.predict(X_test)
    train_rmse = sqrt(mean_squared_error(y_train, y_train_pred))
    test_rmse  = sqrt(mean_squared_error(y_test, y_test_pred))
    train_r2 = r2_score(y_train, y_train_pred)
    test_r2  = r2_score(y_test,  y_test_pred)

    st.write(f"**Trained Ride**: {ride_name}")

    # Save
    subfolder = f"../models/{ride_name}_gb_model"
    os.makedirs(subfolder, exist_ok=True)
    model_path = f"{subfolder}/best_{ride_name}_gb_model.pkl"
    joblib.dump(best_model, model_path)

    return best_model, preprocessor, df_ride_weather

def predict_5min_for_date(model, preproc, df_data, date):
    date_obj = pd.to_datetime(date, errors="coerce").normalize()
    daydf = df_data[df_data["datetime"].dt.normalize()==date_obj].copy()
    if daydf.empty:
        return None
    if "wait_time" in daydf.columns:
        daydf.drop(columns=["wait_time"], inplace=True, errors="ignore")

    exclude = ["datetime","date","valid_end"]
    X_day = daydf.drop(columns=[c for c in exclude if c in daydf.columns], errors="ignore")
    X_proc = preproc.transform(X_day)
    daydf["PredictedWait"] = model.predict(X_proc)
    return daydf

def suggested_percent_change(df_data, model, preproc, day_to_forecast):
    """
    Compare yesterday vs day before, if holiday => +10.
    """
    date_obj = pd.to_datetime(day_to_forecast, errors="coerce").normalize()
    if pd.isna(date_obj):
        return 0

    yester = date_obj - timedelta(days=1)
    dayb4  = date_obj - timedelta(days=2)

    yest_pred = predict_5min_for_date(model, preproc, df_data, str(yester))
    dayb4_pred= predict_5min_for_date(model, preproc, df_data, str(dayb4))

    if (yest_pred is None or yest_pred.empty) or (dayb4_pred is None or dayb4_pred.empty):
        base = 0
    else:
        ya = yest_pred["PredictedWait"].mean()
        db = dayb4_pred["PredictedWait"].mean()
        if db<=0:
            base=0
        else:
            base=((ya - db)/db)*100.0

    # check if forecast day is holiday => add 10
    daydf = df_data[df_data["datetime"].dt.normalize()==date_obj]
    if not daydf.empty:
        if daydf["holiday_flag"].fillna(0).max()>0:
            base+=10

    return round(base,1)

def main():
    add_custom_css()
    st.title("5-min Ride Wait Model + Staff Allocation (Dropdown + Past Day Logic)")

    # LOAD rides_keys.csv, ensure columns exist, display it for reference
    rides_csv = "data/uss_attraction_details/rides_keys.csv"
    try:
        ridedf = pd.read_csv(rides_csv, on_bad_lines='skip')
    except Exception as e:
        st.error(f"Error reading CSV {rides_csv}: {e}")
        st.stop()

    if "ride" not in ridedf.columns or "file_name" not in ridedf.columns:
        st.error(f"CSV must have columns 'ride' and 'file_name'. Found columns: {ridedf.columns.tolist()}")
        st.stop()

    # Display the table so people can refer to it
    st.write("Here are all the rides in rides_keys.csv:")
    st.dataframe(ridedf)

    # Now the user picks from the "ride" column
    st.subheader("Pick a Ride to Train")
    ride_choice = st.selectbox("Select Ride", ridedf["ride"].unique())
    row = ridedf[ridedf["ride"]==ride_choice].iloc[0]
    ride_file = row["file_name"]  # if KeyError => csv is missing 'file_name'

    if st.button("Train Model for This Ride"):
        model, preproc, df_data = train_ride_model(ride_file)
        st.session_state["model"] = model
        st.session_state["preproc"] = preproc
        st.session_state["df_data"] = df_data
        st.session_state["ride_name"] = ride_choice

    if "model" in st.session_state:
        st.subheader("Predict & Allocate Staff")

        day_choice = st.date_input("Forecast Date", value=datetime(2025,1,15))
        open_hour  = st.number_input("Open Hour", 0, 23, 10)
        close_hour = st.number_input("Close Hour",0,23,20)
        staff      = st.number_input("Total Staff",1,500,30)
        shift_hrs  = st.number_input("Shift Hours/Staff",1,24,8)
        wait_prior = st.slider("Wait Priority(1=even,5=peak)",1,5,3)

        rec_pct = suggested_percent_change(
            st.session_state["df_data"],
            st.session_state["model"],
            st.session_state["preproc"],
            str(day_choice)
        )
        st.write(f"**Suggested Demand Change**: {rec_pct}% (based on day-1 vs day-2 + holiday)")

        user_pct = st.number_input(
        "Demand Change (%)",
        -100.0,       # float
        500.0,        # float
        float(rec_pct) # ensure value is float
        )

        if open_hour>=close_hour:
            st.error("Open hour must be < close hour.")
        else:
            if st.button("Predict & Allocate"):
                daydf = predict_5min_for_date(
                    st.session_state["model"],
                    st.session_state["preproc"],
                    st.session_state["df_data"],
                    str(day_choice)
                )
                if daydf is None or daydf.empty:
                    st.warning("No 5-min data found for that date.")
                else:
                    # apply user pct
                    daydf["PredictedWait"] *= (1+ user_pct/100.0)
                    daydf["hour"]=daydf["datetime"].dt.hour
                    slice_df= daydf[(daydf["hour"]>=open_hour)&(daydf["hour"]<=close_hour)]
                    hr_g= slice_df.groupby("hour")["PredictedWait"].mean().reset_index()
                    hr_g.rename(columns={"PredictedWait":"forecasted_wait_time"}, inplace=True)

                    res= optimise_staffing(hr_g, staff, wait_prior, shift_hrs)
                    st.write(f"**Staff Allocation** - {st.session_state['ride_name']}, {day_choice}")
                    st.write(f"Solver status: {res['status']}")
                    if res["status"]!="optimal":
                        st.error("Infeasible or suboptimal. Increase staff or shift hours or reduce priority?")

                    staffarr= res["staff_allocation"]
                    out_rows= []
                    for i,hrv in enumerate(hr_g["hour"]):
                        out_rows.append({
                            "Hour":hrv,
                            "ForecastedWait": float(hr_g.iloc[i]["forecasted_wait_time"]),
                            "StaffAlloc": round(staffarr[i])
                        })
                    st.dataframe(pd.DataFrame(out_rows))
    else:
        st.info("Train a ride model first to enable predictions.")

if __name__=="__main__":
    main()
