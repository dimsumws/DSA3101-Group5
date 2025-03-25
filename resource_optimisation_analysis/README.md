# Resource Allocation for Demand Variability

## Overview
This addresses the challenge of dynamically allocating staff and resources in theme parks, where guest demand fluctuates by time of day, season, and special events. Through a combination of wait time forecasting, survey analysis, and optimisation modelling, this aims to improve cost efficiency while enhancing guest experience

## Data and Methods

### 1. Historical Wait Time Analysis
**File:** `seasonality_daily_trend.py`
- Analyses hourly and monthly wait time trends using 2024 USS crowd data
- Separates normal days (10am to 7pm) from **Halloween Horror Nights** (7pm to 12am) for analysis
- Visualises daily and seasonal guest flow using plots, which guide time-specific staffing needs
- Helps to pinpoint when congestion is highest during the day and across the year

### 2. Survey Analysis
**File:** `survey_data_resource_allocation.py`
- Cleans and processes multi-select guest survey responses related to:
    - Preferred visit times
    - Preferred days
    - Satisfaction with queue lengths
    - Perceptions of staff adequacy, friendliness, and overall safety

- Produces counts and visualisations for:
    - Time-of-day preferences
    - Event/day-type attendance
    - Rating distributions on various service aspects

- Informs which aspects of guest experience require improved resource targeting (eg. long queues despite positive staff ratings)

### 3. Staff Optimisation Model
**File:** `staff_optimiser.py`
- Forecasts future hourly wait times based on historical crowd trends using **SARIMAX time series modelling**
- Allows user input for:
    - Target date
    - Total available staff
    - Expected % change in visitor demand
    - Opening/closing hours
    - Average staff shift length (in hours)
    - Priority scale (1-5) for focusing on peak-hours

- Adjusts forecasts based on:
    - Historical date matching (e.g past Fridays in the same month)
    - Seasonal fluctuations
    - USS's prediction bias from prior years

- Uses **CVXPY convex optimisation** to:
    - Allocate staff per hour within realistic constraints
    - Penalise both over and under-staffing
    - Ensure total staff hours do not exceed total staff x shift length
    - Apply smoothness constraint (to avoid abrupt changes in staffing across hours)

- **Output:** Prints a recommended hourly staff schedule that balances operational efficiency with predicted demand