# Staff Optimiser

## Overview

This module aims to dynamically allocate staff within Universal Studios Singapore (USS) based on forecasted hourly guest demand. The model takes into account historical wait times, seasonal patterns, and user-specified constraints such as opening hours and staff availability. It provides a data-driven, intuitive tool for theme park managers to improve operational efficiency and guest satisfaction.

## Data Sources

- `cleaned_2024_wait_times.csv`: Actual wait times in 5-minute intervals for USS in 2024.
- `cleaned_crowd_prediction_accuracy_table.csv`: Historical forecast vs actual wait times from 2023-2024, including USS prediction bias

## Methodology

### Data Preprocessing

1. **Data Aggregation:**
    - Extracts hourly average wait times from 5-minute intervals.
    - Filters data by matching historical dates (same month and weekday as target date).
    - Incorporates seasonal adjustment based on monthly average trends.

2. **Feature Engineering:**
    - Computes USS's historical forecast bias and adjusts future forecasts.
    - Allows dynamic scaling based on user input (expected change in demand).

### Modelling Approach

- **Forecasting:**
    Uses SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous regressors) to forecast hourly waiting times for a future date, based on matched historical patterns.

- **Optimisation Model:**
    - **Objective:** Minimise staffing cost while penalising both over and under-allocation of staff.
    - **Inputs:**
        - Forecasted demand (hourly waiting time)
        - Total staff
        - Average shift length
        - Wait time priority level
        - Opening/closing hours
    - **Constraints:**
        - Minimum and maximum hourly staff thresholds
        - Total staff-hours <= total staff x shift length
        - Smooth transitions across hours to avoid scheduling instability

### Key Findings:

- Staff demand peaks align with historically high wait times between 1 PM and 7 PM.
- USS typically underestimates demand in previous years - this bias is accounted for in forecast adjustments.
- Staff recommendations adjust based on predicted demand surges, input constraints, and managerial priorities.

## Applications

- **Daily Staff Scheduling:**
    Generates a tailored staff schedule based on real-time managerial input and expected guest volume.

- **Scenario Planning:**
    Useful for simulating different crowd levels during school holidays, weekends, or special events (e.g. Halloween Horror Nights).

- **Budget-Conscious Resource Allocation:**
    Helps managers allocate available workforce efficiently, within operational constraints.

## Future improvements

- **Model Evaluation:**
    Currently, the optimiser has not been quantitatively evaluated due to the absence of ground-truth staffing data. Future work can incorporate actual staff logs and operational KPIs (e.g. queue satisfaction, ride throughput) to validate and improve the model.

- **Incorporation of More Features:**
    Including weather data, holiday schedules, and marketing campaigns could further improve forecast accuracy.

- **Multi-Objective Optimisation:**
    Introduce other goals such as staff fatigue reduction or ride-specific allocation for more granularity.
