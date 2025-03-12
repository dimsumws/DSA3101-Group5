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

# Step 2: Forecast Future Waiting Times

def forecast_wait_times(df_wait, target_date):
    
    # Extract hourly average wait times for training (2023-2024)
    df_wait['hour'] = pd.to_datetime(df_wait['time'], format="%H:%M:%S").dt.hour
    hourly_trends = df_wait.groupby(['date', 'hour'])['wait_time'].mean().reset_index()

    # Convert dates to numeric index
    hourly_trends['timestamp'] = (hourly_trends['date'] - hourly_trends['date'].min()).dt.days

    # Train SARIMA Model on past waiting time trends
    model = SARIMAX(hourly_trends['wait_time'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 24))
    results = model.fit()

    # Forecast for target date
    forecast_days = (target_date - df_wait['date'].min()).days
    future_wait_times = results.get_forecast(steps=24)
    forecast_mean = future_wait_times.predicted_mean.values

    # Convert into dataframe
    forecast_df = pd.DataFrame({
        'hour': np.arange(24),
        "forecasted_wait_time": forecast_mean
    })

    return forecast_df

# Step 3: User Input for Future Staff Allocation

def user_input():

    # Date Selection
    target_date_str = input("Enter the date you want to schedule for (YYYY-MM-DD): ")
    target_date = pd.to_datetime(target_date_str, errors='coerce')

    # Total staff available
    total_staff = int(input("\nEnter the total number of staff available for the day: "))

    # Expected visitor increase/decrease
    expected_change = float(input("\nHow much (%) do you expect demand to increase/decrease? (e.g. 10 for +10%, -5 for -5%): "))

    # Priority: Minimise wait times vs distribute staff equally
    print("\nHow much do you prioritise minimising wait times?")
    print("(1 = Staff should be equally distributed, 5 = Staff should be focused on peak hours)")
    wait_priority = int(input("Priority (1-5): "))

    return {
        'target_date': target_date,
        'total_staff': total_staff,
        'expected_change': expected_change,
        'wait_priority': wait_priority
    }

# Step 4: Optimisation Model for Staff Allocation

def optimise_staffing(hourly_demand, total_staff, wait_priority):
    T = len(hourly_demand)
    S = cp.Variable(T, nonneg=True) # Staff per time slot

    # Normalise wait times to create a relative weight for each hour
    demand_weights = hourly_demand['forecasted_wait_time'].values
    demand_weights = demand_weights / np.max(demand_weights) # Scale between 0 and 1

    # Objective: allocate staff to minimise wait time impact
    objective = cp.Minimize(-wait_priority * cp.sum(cp.multiply(demand_weights, S)))

    # Constraints
    constraints = [
        cp.sum(S) == total_staff, # Total staff must match available staff
        S >= 0 # No negative staff
    ]

    # Solve
    problem = cp.Problem(objective, constraints)
    result = problem.solve()

    return {
        'status': problem.status,
        'staff_allocation': S.value
    }

# Step 5: Main Function to run Optimisation

def main():
    df_wait, df_pred = load_data() # Load data

    user_params = user_input() # Get user input

    forecasted_demand = forecast_wait_times(df_wait, user_params['target_date']) # Forecast wait times for selected future date

    # Adjust forecast based on expected visitor change
    adjustment_factor = 1 + (user_params['expected_change'] / 100)
    forecasted_demand['forecasted_wait_time'] *= adjustment_factor

    # Optimise staffing
    result = optimise_staffing(
        hourly_demand=forecasted_demand,
        total_staff=user_params['total_staff'],
        wait_priority=user_params['wait_priority']
    )

    # Display Results
    print("\n=== OPTIMISATION RESULTS ===")
    print("Status:", result['status'])

    print("\nHour | Forecasted Wait Time | Staff Allocated")
    for i, hr in enumerate(forecasted_demand['hour']):
        print(f"{hr:4d} | {forecasted_demand.iloc[i]['forecasted_wait_time']:16.2f} | {result['staff_allocation'][i]:11.2f}")

if __name__ == '__main__':
    main()