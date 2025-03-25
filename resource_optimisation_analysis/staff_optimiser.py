import pandas as pd
import numpy as np
import cvxpy as cp
import os
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Step 1: Load Data (2023-2024)
def load_data():
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "..", "data", "uss_wait_times", "cleaned_data_2022_2025")
    wait_file = os.path.join(data_dir, "cleaned_2024_wait_times.csv")  # Actual waiting times in 2024
    pred_file = os.path.join(data_dir, "cleaned_crowd_prediction_accuracy_table.csv")  # Forecasted vs actual for 2023-2024
    df_wait = pd.read_csv(wait_file)
    df_pred = pd.read_csv(pred_file)
    # Convert Date columns
    df_wait['date'] = pd.to_datetime(df_wait['date'], errors='coerce')
    df_pred['Date'] = pd.to_datetime(df_pred['Date'], errors='coerce')
    return df_wait, df_pred

# Step 2: Compute Prediction Bias
def compute_prediction_bias(df_pred):
    avg_bias = df_pred['Delta'].mean()
    return avg_bias

# Step 3: Identify Matching Historical Dates using a broader historical window
def get_historical_matches(df_wait, target_date):
    target_month = target_date.month
    target_weekday = target_date.weekday()  # Monday=0, Sunday=6
    historical_matches = df_wait[(df_wait['date'].dt.month == target_month) & (df_wait['date'].dt.weekday == target_weekday)]
    if historical_matches.empty:
        historical_matches = df_wait[df_wait['date'].dt.month == target_month]
    return historical_matches

# Step 4: Forecast Future Waiting Times with Rolling Seasonal Adjustment
def forecast_wait_times(df_wait, df_pred, target_date, open_hour, close_hour):
    historical_matches = get_historical_matches(df_wait, target_date)
    if historical_matches.empty:
        print("No relevant historical data found.")
        return None

    historical_matches['hour'] = pd.to_datetime(historical_matches['time'], format="%H:%M:%S").dt.hour
    hourly_trends = historical_matches[(historical_matches['hour'] >= open_hour) & (historical_matches['hour'] <= close_hour)]
    hourly_trends = hourly_trends.groupby('hour')['wait_time'].mean().reset_index()

    model = SARIMAX(hourly_trends['wait_time'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    results = model.fit(disp=False)
    
    forecast_steps = close_hour - open_hour + 1
    future_wait_times = results.get_forecast(steps=forecast_steps)
    forecast_mean = future_wait_times.predicted_mean.values

    avg_bias = compute_prediction_bias(df_pred)
    adjusted_forecast = forecast_mean + avg_bias

    overall_mean = df_wait['wait_time'].mean()
    month_mean = df_wait[df_wait['date'].dt.month == target_date.month]['wait_time'].mean()
    seasonal_factor = month_mean / overall_mean if overall_mean != 0 else 1
    adjusted_forecast *= seasonal_factor

    forecast_df = pd.DataFrame({
        'hour': np.arange(open_hour, close_hour + 1),
        "forecasted_wait_time": adjusted_forecast
    })
    return forecast_df

# Step 5: User Input for Future Staff Allocation (with shift length)
def user_input():
    target_date_str = input("Enter the date to schedule for (YYYY-MM-DD): ")
    target_date = pd.to_datetime(target_date_str, errors='coerce')
    total_staff = int(input("Enter total number of staff available for the day: "))
    expected_change = float(input("Enter expected demand change (%) (e.g., 10 for +10%, -5 for -5): "))
    open_hour = int(input("Enter park opening hour (e.g., 10 for 10 AM): "))
    close_hour = int(input("Enter park closing hour (e.g., 22 for 10 PM): "))
    shift_hours = int(input("Enter the average shift length for a staff member (in hours): "))
    print("\nPriority: 1 = evenly distribute staff, 5 = focus on peak hours")
    wait_priority = int(input("Enter priority (1-5): "))
    return {
        'target_date': target_date,
        'total_staff': total_staff,
        'expected_change': expected_change,
        'open_hour': open_hour,
        'close_hour': close_hour,
        'shift_hours': shift_hours,
        'wait_priority': wait_priority
    }

# Step 6: Optimisation Model for Staff Allocation (with shift-hours constraint)
def optimise_staffing(hourly_demand, total_staff, wait_priority, shift_hours):
    T = len(hourly_demand)
    S = cp.Variable(T, nonneg=True)  # Staff allocated per time slot

    forecast = hourly_demand['forecasted_wait_time'].values
    max_forecast = np.max(forecast)
    demand_weights = forecast / max_forecast  
    target = total_staff * demand_weights

    c = 1    # Base cost per staff per hour
    u = wait_priority * 10   # Under-allocation penalty weight
    v = 5    # Over-allocation penalty weight

    under_alloc = cp.sum(cp.square(cp.pos(target - S)))
    over_alloc = cp.sum(cp.square(cp.pos(S - target)))
    smoothness_penalty = cp.norm(S[1:] - S[:-1], p=2)
    
    objective = cp.Minimize(
        c * cp.sum(S) + u * under_alloc + v * over_alloc + 0.1 * smoothness_penalty
    )
    min_staff = max(10, total_staff // T)
    constraints = [
        S >= min_staff,
        S <= total_staff,
        cp.sum(S) <= total_staff * shift_hours  # Total staff-hours constraint
    ]
    problem = cp.Problem(objective, constraints)
    result = problem.solve()
    if problem.status != "optimal":
        print("Warning: Optimisation did not converge. Using equal distribution as fallback.")
        fallback_alloc = np.full(T, total_staff // T, dtype=int)
        return {"status": problem.status, "staff_allocation": fallback_alloc}
    return {
        'status': problem.status,
        'staff_allocation': S.value
    }

# Step 7: Main Function to run Optimisation
def main():
    df_wait, df_pred = load_data()
    user_params = user_input()
    forecasted_demand = forecast_wait_times(df_wait, df_pred, user_params['target_date'],
                                            user_params['open_hour'], user_params['close_hour'])
    if forecasted_demand is None:
        return
    adjustment_factor = 1 + (user_params['expected_change'] / 100)
    forecasted_demand['forecasted_wait_time'] *= adjustment_factor
    result = optimise_staffing(forecasted_demand, user_params['total_staff'], 
                               user_params['wait_priority'], user_params['shift_hours'])
    print("\n=== OPTIMISATION RESULTS ===")
    print("Status:", result['status'])
    print("\nHour | Forecasted Wait Time | Staff Allocated")
    for i, hr in enumerate(forecasted_demand['hour']):
        print(f"{hr:4d} | {forecasted_demand.iloc[i]['forecasted_wait_time']:16.2f} | {round(result['staff_allocation'][i]):11d}")

if __name__ == '__main__':
    main()
