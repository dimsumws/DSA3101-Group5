## Data in this folder

**`economy`**: Information about the economy in Singapore
- Contains two subfolders **`final`** and **`Python File`**  
    - **`Final`** 
        - **`accessible_income.csv`**: Assessable income data of Singaporeans from *2004 to 2023*.
        - **`annual_unemployment.csv`**: Data of Singapore's unemployment rate from *1992 to 2023*.
        - **`cpi.csv`**: Consumer Price Index data of various categories of goods from *2017 to 2024*.
        - **`employment_industry.csv`**: Employment changes statistics across various industries from *1991 to 2024*.
        - **`median_income.csv`**: Median Income among Singaporeans before and after CPF from *2001 to 2023*.
    - **`Python File`** 
        - **`accessible_income.py`**: python script to retrieve **`accessible_income.csv`** from public data.gov.sg API.
        - **`annual_unemployment.py`**: python script to retrieve **`annual_unemployment.csv`** from public data.gov.sg API.
        - **`cpi.py`**: python script to retrieve **`cpi.csv`** from public data.gov.sg API and code for applying data transformation to raw data.
        - **`employment_industry.py`**: python script to retrieve **`unemployment.csv`** from public data.gov.sg API and code for applying data transformation to raw data.
        - **`median_income.py`**: python script to retrieve **`median_income.csv`** from public data.gov.sg API.
    - **Data Source**: 
        1. [data.gov.sg](https://data.gov.sg/)

---

**`events`**: information about key events in Singapore, mainly nationwide events, public holidays and school holidays. 
- Contains two subfolders **`EventData`** and **`Holidays`**
    - **`EventData`** 
        - **`supplementary_event_data_2016_2025.csv`**: Contains row of daily dates, with boolean flag to determine if corresponding data has an ongoing event.
        - **`2025_remainder_supplementary_event.csv`**: Similar to previously mentioned file but for remainding days of 2025 (March to December of 2025).
    - **`Holidays`** 
        - **`datasets`**
            - **`2025_daily_school_holidays.csv`**: Daily data for 2025 with boolean flags if corresponding days are school holidays, has column for name of respective school holiday as well.
            - **`daily_school_holidays_combined_updated.csv`**: Similar to **`2025_daily_school_holidays.csv`**, but for years 2016 to 2025.
            - **`final_merged_PH_2020_2025.csv`**: List of Public Holiday data from years 2020 to 2025 stored in csv file.
            - **`school_holidays_combined.csv`**: List of School Holiday data from years 2019 to 2025 stored in csv file.
        - **`code_solutions`**
            - **`add_2016_to_2018_hol.py`**: Python script to add supplementary school holiday data from 2016 to 2018, and process *school_holidays_combined.csv* into **`daily_school_holidays_combined_updated.csv`**
            - **`scrape_moe_holiday.py`**: Python Script to scrape MOE Holiday data from 2019 to 2025 from Official MOE website and store in **`school_holidays_combined.csv`**
    - **Data Source**: 
        1. [Wikipedia](https://en.wikipedia.org/wiki/Main_Page)
        2. [MOE](https://www.moe.gov.sg/calendar)
        3. [data.gov.sg](https://data.gov.sg/)

---

**`google_reviews`**: reviews on Universal Studios Singapore, scraped from Google Reviews.
- **`googlereviewcleaning.ipynb`**: Python Notebook for performing data transformation to `googlereviews5000.xlsx` into `google reviews cleaned df_no_text.xlsx` and `google reviews cleaned df_text.xlsx`

---

**`google_trends`**: google trends data about Universal Studios Singapore and so forth using python libary **pytrends**
- **`google_trends_search.py`**: Python script to generate USS google trends data from 2023 to 2025 using pytrends. Code to generate google trends graphic as well
- **`google_trends.png`**: Google Trends data changes from 2023 to 2025 
- **`uss_google_trends_2023_2025.csv`**: Google Trends data from 2023 to 2025 weightage stored in csv file.
    - **Data Source**:
        1. [PyTrends Documentation](https://pypi.org/project/pytrends/)

---        

**`instagram`**: instagram posts and stories posted by USS, extraction and data cleaning.
- Contains two subfolders **`Data`** and **`Python`**
    - **`Data`**
        **`category_metrics.csv`**: Aggregated engagement metrics for different marketing categories. 
        - **`cleaned_instagram_data.csv`**:  A cleaned version of `uss_ig.csv` with improved formatting and consistency.
        - **`cleaned_instagram_stories.csv`**: A cleaned version of `uss_ig_stories.csv`.
        - **`uss_ig_classified_sentiment.csv`**:  A further processed version of `uss_ig_classified.csv`, including: `num_comments`, `sentiment`, `engagement_score`.
        - **`uss_ig_classified.csv`**: An enhanced version of `cleaned_instagram_data.csv`, with additional binary columns indicating whether a post belongs to a specific marketing category.
        - **`uss_ig_stories.csv`**: Contains raw Instagram highlights (stories) data.
        - **`uss_ig.csv`**: Contains raw Instagram post data.
        
    - **`Python`**
        - **`615_import_firefox_session.py`**: Script to import user's Instagram session from Firefox.
        - **`clean_ig_post.py`**: Script to clean `uss_ig.csv` and `uss_ig_stories.csv`.
        - **`comment_engineering.py`**: Processes comments and generates new columns: num_comments, sentiment, and engagement_score.
        - **`extract_ig_post.py`**: Script to extract data from @universalstudiossingapore's feed posts.
        - **`extract_ig_story.py`**: Script to extract data from @universalstudiossingapore's story highlights.
        - **`marketing_classification.py`**: Script to classify posts into specific marketing categories.

    - **Data Source**: 
        1. [Instagram](https://www.instagram.com/universalstudiossingapore/)
    
---

**`meteorological`**: information about the weather in Singapore, together with data collection and cleaning code.
- Contains two subfolders **`code_solutions`** and **`datasets`**:
    - **`code_solutions`**
        - **`clean_and_merge_psi.py`**: Retrieve daily PSI data from from data.gov.sg public API, perform data transformation to find average PSI and PSI rating.
        - **`generate_synthetic_weather_data_2025`**: Python code to generate synthetic weather data using **`merged_weather_data_clean.csv`** as a basis.
        - **`get_4_day_forecast.py`**: Retrieve 4 Day Forecast Data from March 2016 to February 2025 data.gov.sg public API.
        - **`get_5_min_rainfall.py`**: Retrieve 5 Min Rainfall Data from December 2023 to January 2025 from data.gov.sg public API.
        - **`get_24_hr_daily_forecast.py`**: Retrieve 24 hr Daily Forecast Data from March 2016 to February 2025 data.gov.sg public API.
        - **`get_avg_windspeed.py`**: Retrieve daily windspeed data from March 2016 to February 2025 using data.gov.sg public API, perform data transformation to find average daily windspeed.
        - **`join_tables_tgt.py`**: Python Script to merge all weather related CSV files together, from 2016 to 2025.
        - **`merge_rh.py`**: Retrieve Relative Humidity data from March 2016 to February 2025 using data.gov.sg public API. Perform data transformation to find daily average RH value.
        - **`merge_sentosa_data.py`**: Merge Monthly Sentosa Weather CSV files into one central file. 
    - **`datasets`**
        - **`final_data`**
            - **`4_day_weather_forecasts.csv`**: 4 Day Weather Forecasts data from 2016 to 2025.
            - **`24_hr_weather_forecast_data.csv`**: 24 Hour Weather Forecast data from 2016 to 2025.
            - **`daily_avg_psi_readings.csv`**: Daily Average PSI Readings data from 2014 to 2025.
            - **`final_augmented_weather_sentosa_data.csv`**: Metoerological Service Singapore Data from 2016 to 2025.
            - **`final_merged_RH_2017_2025.csv`**: Average Relative Humidity data from 2017 to 2025.
            - **`sentosa_avg_windspeed.csv`**: Average Windspeed data from 2017 to 2025.
            - **`sentosa_rainfall_5min_int.csv`**: 5 Minute Interval Sentosa Rainfall data for years 2024 and 2025.
            - **`synthetic_weather_data_2025_cleaned.csv`**: Synthetic daily weather data for rest of 2025 dates.
        - **`raw_data`**
            - **`daily_data_sentosa`**:
                - **`sentosa_data.zip`**: zip file containing monthly data of Sentosa from MSS.
            - **`Historical24hrPSI.csv`**: 24 Hour Historical PSI Values from data.gov.sg.
    - **Data Sources**:
        1. [data.gov.sg](https://data.gov.sg/)
        2. [Meteorological Service Singapore](https://www.weather.gov.sg/climate-historical-daily/)

---

**survey_responses**: survey responses obtained from our survey  
- **`survey_responses.csv`**: Raw data of survey responses
- **`survey_cleaning.py`**: Python script to perform data cleaning and responses 
- **`labels.csv`**: List of Labels for Survey Questions
- **`cleaned_survey_responses.csv`**: Cleaned version of data responses

---

**tripadvisor_reviews**: reviews on USS scraped from Tripadvisor  
- **`DSA3101 trip advisor cleaning.ipynb`**: Python notebook to clean Tripadvisor data
- **`read_data.py`**: Python script to read in **`tripadvisor.csv`**
- **`tripadvisor.csv`**: Finalized and cleaned Tripadvisor data.
- **Data Source**:
    1. [Tripadvisor](https://www.tripadvisor.com.sg/Attraction_Review-g294264-d2439664-Reviews-Universal_Studios_Singapore-Sentosa_Island.html)

---

**uss_attraction_details**: details on entities in USS  
- **`attractions.csv`**: Contains all entities in USS in format: [name, attraction type, zone]
- **`meetandgreet.csv`**: Contains all show timings in format: [title, show times]
- **`rides.csv`**: : Contains all rides in USS in format: [ride, type, environment, description]
- **Data Source**:
    1. [Resorts World Sentosa](https://www.rwsentosa.com/en/Play/universal-studios-singapore)

---


**uss_ride_wait_times**: wait times for all individual rides in USS scraped from Thrill Data
- **`Raw Data`** subfolder
    - Each Individual Ride in USS has a subfolder, with montlhy CSV files containing 5 Minute Interval Wait Time data for corresponding month
- **`merged_XXX.csv`**: Each Ride's total wait time data across all months into an individaul folder
- **`merge_csv.py`**: Python script to merge each ride's **`merged_XXX"`** into **`all_ride_wait_times.csv`**
- **`all_ride_wait_times.csv`**: All rides 5 Minute Interval wait time data from January 2024 to March 2025
- **Data Source**:
    1. [Thrill Data](https://www.thrill-data.com/waits/park/unit/universal-studios-singapore/)

---

**uss_wait_times**: wait times for rides in USS scraped from Thrill Data
- Contains five subfolders **`augmented_wait_time_data`**, **`cleaned_data_2022_2025`**, **`cleaning_python_script_2024_wait_times`**, **`python_scripts`**, and **`raw 2024 wait time datasets`**.
    - **`cleaning_python_script_2024_wait_times`**
    - **`data_scraping.py`**: Retrieve prediction data for ride wait times in USS for 2023-2024 from Thrill Data.
    - **`uss_2024_wait_times_cleaning`**: Script to clean the combined 2024 wait time data for USS.
    - **`uss_wait_times_combined`**: Script to combine monthly raw data for USS wait times into 1 csv file.
- **Data Source**:
    1. [Thrill Data](https://www.thrill-data.com/waits/park/unit/universal-studios-singapore/)
