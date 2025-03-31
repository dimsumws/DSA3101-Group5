# code_solutions
this subfolder contains processing, api requesting code, and merger of all csv files code. python requests library was used to make iterative API calls to [data.gov.sg](https://data.gov.sg/) and *Pandas* to store code in a dataframe, and then stored as a CSV for data reference.

# datasets
- this subfolder includes another subfolder called raw_data which was used for processing within *datasets subfolder*
- this subfolder includes another subfolder called final_data which has the final data that will be used in preprocessing *datasets subfolder*
- python scripts are stored in *code_solutions subfolder*

## datasources
[PSI API Data for 2025 dates](https://data.gov.sg/datasets/d_fe37906a0182569d891506e815e819b7/view) and [Historical 24-hr PSI dataset csv](https://data.gov.sg/datasets/d_b4cf557f8750260d229c49fd768e11ed/view) -> Both of these were used in *clean_and_merge_psi.py* and stored in **daily_avg_psi_readings.csv**

[24 Hour Daily Forecast Data](https://data.gov.sg/datasets/d_ce2eb1e307bda31993c533285834ef2b/view) -> used in *get_24_hr_daily_forecast.py* and stored in **24_hr_weather_forecast_data.csv**

[4 Day Forecast Data](https://data.gov.sg/datasets/d_f131f6e343bf8168e4057a04c4326a0a/view) -> used in *get_4_day_forecast.py* and stored in **4_day_weather_forecast.csv**

[Windspeed Data](https://data.gov.sg/datasets/d_7677738484067741bf3b56ab5d69c7e9/view) -> used in *get_avg_windspeed.py* and stored in **sentosa_avg_windspeed.csv**

[Relative Humidity data](https://data.gov.sg/datasets/d_2d3b0c4da128a9a59efca806441e1429/view) -> used *merge_rh.py* and stored in **final_merged_RH_2017_2025.csv**

[General Sentosa Data](https://www.weather.gov.sg/climate-historical-daily/) -> used in *merge_sentosa_data.py* and files are downloaded on a monthly basis, each month from 2016 to 2025 stored in ***sentosa_data.zip*** in **daily_data_sentosa in raw_data

[5 Minute Interval Rain](https://data.gov.sg/datasets/d_6580738cdd7db79374ed3152159fbd69/view) -> data stored in *sentosa_rainfall_5min_int.csv*. Code to generate csv can be found in *'/code_solutions/sentosa/get_5_min_rainfall.py'*

**synthetic_weather_data_faker_style_2025_cleaned.csv** synthetically generted weather data for 2025 dates that have no occured yet. generated from code from "data/Meteorological/code_solutions/generate_synthetic_weather_data_2025.py"