import pandas as pd
import numpy as np
import cvxpy as cp
import os
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Step 1: Load Data (2023-2024)

def load_data():
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "..", "data")

    wait_file = os.path.join(data_dir, "cleaned_2024_wait_times.csv") # actual waiting times in 2024 for USS
    pred_file = os.path.join(data_dir, "cleaned_crowd_prediction_accuracy_table.csv") # 2023-2024 forecasted vs actual waiting times for USS

    df_wait = pd.read_csv(wait_file)
    df_pred = pd.read_csv(pred_file)

    # Convert Date columns
    df_wait['date'] = pd.to_datetime(df_wait['date'], errors='coerce')
    df_pred['Date'] = pd.to_datetime(df_pred['Date'], errors='coerce')

    return df_wait, df_pred

# Step 2: Compute USS Prediction Bias

def compute_prediction_bias(df_pred):
    # Calculates historical prediction bias to adjust future forecasts. Positive bias means USS under-predicted; negative bias means USS over-predicted
    avg_bias = df_pred['Delta'].mean()
    return avg_bias

# Step 3: Identify Matching Historical Dates

def get_historical_matches(df_wait, target_date):
    # Finds historical dates in the dataset that match the target date (same month/day from past years). If no exact match, it finds the closest past dates within the same month.
    target_month = target_date.month
    target_day = target_date.day

    # Find exact matches
    historical_matches = df_wait[(df_wait['date'].dt.month == target_month) & (df_wait['date'].dt.day == target_day)]

    if historical_matches.empty:
        df_month = df_wait[df_wait['date'].dt.month == target_month]
        closest_past_date = df_month['date'].max()

        if pd.isna(closest_past_date):
            print(f"No historical data for {target_date.strftime('%Y-%m')}")
            return None
        
        historical_matches = df_month[df_month['date'] == closest_past_date]

    return historical_matches

# Step 4: Forecast Future Waiting Times

def forecast_wait_times(df_wait, df_pred, target_date, open_hour, close_hour):
    
    # Get historical matches
    historical_matches = get_historical_matches(df_wait, target_date)

    if historical_matches is None:
        print("No relevant historical data found.")
        return None

    # Filter historical data to open hours
    historical_matches['hour'] = pd.to_datetime(historical_matches['time'], format="%H:%M:%S").dt.hour
    hourly_trends = historical_matches[(historical_matches['hour'] >= open_hour) & (historical_matches['hour'] <= close_hour)]

    # Compute average wait time for each hour based on historical trends
    hourly_trends = hourly_trends.groupby('hour')['wait_time'].mean().reset_index()

    # Train SARIMA Model based on these historical matches
    model = SARIMAX(hourly_trends['wait_time'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    results = model.fit()

    # Forecast for open hours
    forecast_steps = close_hour - open_hour + 1
    future_wait_times = results.get_forecast(steps=forecast_steps)
    forecast_mean = future_wait_times.predicted_mean.values

    # Adjust forecast based on USS's past prediction bias
    avg_bias = compute_prediction_bias(df_pred)
    adjusted_forecast = forecast_mean + avg_bias

    # Convert into dataframe
    forecast_df = pd.DataFrame({
        'hour': np.arange(open_hour, close_hour + 1),
        "forecasted_wait_time": adjusted_forecast
    })

    return forecast_df

# Step 5: User Input for Future Staff Allocation

def user_input():

    # Date Selection
    target_date_str = input("Enter the date you want to schedule for (YYYY-MM-DD): ")
    target_date = pd.to_datetime(target_date_str, errors='coerce')

    # Total staff available
    total_staff = int(input("\nEnter the total number of staff available for the day: "))

    # Expected visitor increase/decrease
    expected_change = float(input("\nHow much (%) do you expect demand to increase/decrease? (e.g. 10 for +10%, -5 for -5%): "))

    # Operating hours
    open_hour = int(input("\nEnter park opening hour (e.g. 10 for 10 AM): "))
    close_hour = int(input("\nEnter park closing hour (e.g. 22 for 10 PM): "))

    # Priority: Minimise wait times vs distribute staff equally
    print("\nHow much do you prioritise minimising wait times?")
    print("(1 = Staff should be equally distributed, 5 = Staff should be focused on peak hours)")
    wait_priority = int(input("Priority (1-5): "))

    return {
        'target_date': target_date,
        'total_staff': total_staff,
        'expected_change': expected_change,
        'open_hour': open_hour,
        'close_hour': close_hour,
        'wait_priority': wait_priority
    }

# Step 6: Optimisation Model for Staff Allocation

def optimise_staffing(hourly_demand, total_staff, wait_priority):
    T = len(hourly_demand)
    S = cp.Variable(T, nonneg=True) # Staff per time slot

    # Get forecasted wait times and normalise them
    forecast = hourly_demand['forecasted_wait_time'].values
    max_forecast = np.max(forecast)
    demand_weights = forecast / max_forecast  # Scaled between 0 and 1

    # Define a target staffing level per hour as a fraction of total_staff
    target = total_staff * demand_weights

    # Define cost parameters
    c = 1    # Cost per staff per hour (base cost)
    u = wait_priority * 10   # Under-allocation penalty weight
    v = 5    # Over-allocation penalty weight

    # Under-allocation: if S[i] < target[i]
    under_alloc = cp.sum(cp.square(cp.pos(target - S)))
    # Over-allocation: if S[i] > target[i]
    over_alloc = cp.sum(cp.square(cp.pos(S - target)))
    
    # Smoothness penalty: penalise abrupt changes between consecutive hours
    smoothness_penalty = cp.norm(S[1:] - S[:-1], p=2)
    
    objective = cp.Minimize(
        c * cp.sum(S) + u * under_alloc + v * over_alloc + 0.1 * smoothness_penalty
    )

    min_staff = max(10, total_staff // (T)) # Ensure minimum staffing but dynamic

    # Constraints
    constraints = [
        S >= min_staff, # Ensures realistic minimum staff allocation
        S <= total_staff
    ]

    # Solve
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
    df_wait, df_pred = load_data() # Load data

    user_params = user_input() # Get user input

    forecasted_demand = forecast_wait_times(df_wait, df_pred, user_params['target_date'], user_params['open_hour'], user_params['close_hour']) # Forecast wait times for selected future date

    if forecasted_demand is None:
        return
    
    # Adjust forecast based on expected visitor change
    adjustment_factor = 1 + (user_params['expected_change'] / 100)
    forecasted_demand['forecasted_wait_time'] *= adjustment_factor

    # Optimise staffing
    result = optimise_staffing(forecasted_demand, user_params['total_staff'], user_params['wait_priority'])

    # Display Results
    print("\n=== OPTIMISATION RESULTS ===")
    print("Status:", result['status'])

    print("\nHour | Forecasted Wait Time | Staff Allocated")
    for i, hr in enumerate(forecasted_demand['hour']):
        print(f"{hr:4d} | {forecasted_demand.iloc[i]['forecasted_wait_time']:16.2f} | {round(result['staff_allocation'][i]):11d}")

if __name__ == '__main__':
    main()