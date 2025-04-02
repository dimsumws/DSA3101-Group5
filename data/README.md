## Data in this folder

**economy**: Information about the economy in Singapore
- Contains two subfolders **`final`** and **`Python File`**  
    - **`Final`** 
        - **accessible_income.csv**: Assessable income data of Singaporeans from *2004 to 2023*.
        - **annual_unemployment.csv**: Data of Singapore's unemployment rate from *1992 to 2023*.
        - **cpi.csv**: Consumer Price Index data of various categories of goods from *2017 to 2024*.
        - **employment_industry.csv**: Employment changes statistics across various industries from *1991 to 2024*.
        - **median_income.csv**: Median Income among Singaporeans before and after CPF from *2001 to 2023*.
    - **`Python File`** 
        - **accessible_income.py**: python script to retrieve **accessible_income.csv** from public data.gov.sg API.
        - **annual_unemployment.py**: python script to retrieve **annual_unemployment.csv** from public data.gov.sg API.
        - **cpi.py**: python script to retrieve **cpi.csv** from public data.gov.sg API and code for applying data transformation to raw data.
        - **employment_industry.py**: python script to retrieve **unemployment.csv** from public data.gov.sg API and code for applying data transformation to raw data.
        - **median_income.py**: python script to retrieve **median_income.csv** from public data.gov.sg API.
    - **Data Source**: 
        1. [data.gov.sg](https://data.gov.sg/)

---

**events**: information about key events in Singapore, mainly nationwide events, public holidays and school holidays. 
- Contains two subfolders **`EventData`** and **`Holidays`**
    - **`EventData`** 
        - **`supplementary_event_data_2016_2025.csv`**: Contains row of daily dates, with boolean flag to determine if corresponding data has an ongoing event.
        - **`2025_remainder_supplementary_event.csv`**: Similar to previously mentioned file but for remainding days of 2025 (March to December of 2025).
    - **`Holidays`** 
        - **`datasets`**
            - **`2025_daily_school_holidays.csv`**: Daily data for 2025 with boolean flags if corresponding days are school holidays, has column for name of respective school holiday as well.
            - **`daily_school_holidays_combined_updated.csv`**: Similar to *2025_daily_school_holidays.csv*, but for years 2016 to 2025.
            - **`final_merged_PH_2020_2025.csv`**: List of Public Holiday data from years 2020 to 2025 stored in csv file.
            - **`school_holidays_combined.csv`**: List of School Holiday data from years 2019 to 2025 stored in csv file.
        - **`code_solutions`**
            - **`add_2016_to_2018_hol.py`**: Python script to add supplementary school holiday data from 2016 to 2018, and process *school_holidays_combined.csv* into `daily_school_holidays_combined_updated.csv`
            - **`scrape_moe_holiday.py`**: Python Script to scrape MOE Holiday data from 2019 to 2025 from Official MOE website and store in *school_holidays_combined.csv*
    - **Data Source**: 
        1. [Wikipedia]()
        2. [MOE]()
        3. [data.gov.sg](https://data.gov.sg/)

---

**google_reviews**: reviews on Universal Studios Singapore, scraped from Google Reviews.
    - **googlereviewcleaning.ipynb**: Python Notebook for performing data transformation to `googlereviews5000.xlsx` into `google reviews cleaned df_no_text.xlsx` and `google reviews cleaned df_text.xlsx`

---

**google_trends**: google trends data about Universal Studios Singapore and so forth using python libary **pytrends**
    - **`google_trends_search.py`**: Python script to generate USS google trends data from 2023 to 2025 using pytrends. Code to generate google trends graphic as well
    - **`google_trends.png`**: Google Trends data changes from 2023 to 2025 
    - **`uss_google_trends_2023_2025.csv`**: Google Trends data from 2023 to 2025 weightage stored in csv file.
    - **Data Source**:
        1. [PyTrends](https://pypi.org/project/pytrends/)

---        

**instagram**: instagram posts and stories posted by USS, extraction and data cleaning.
- Contains two subfolders **`Data`** and **`Python`**
    - **`Data`**
        **`category_metrics.csv`**
        - **`cleaned_instagram_data.csv`**:
        - **`cleaned_instagram_stories.csv`**:
        - **`uss_ig_classified_sentiment.csv`**
        - **`uss_ig_classified.csv`**
        - **`uss_ig_stories.csv`**:
        - **`uss_ig.csv`**
        
    - **`Python`**
        - **`615_import_firefox_session.py`**:
        - **`clean_ig_post.py`**:
        - **`comment_engineering.py`**
        - **`extract_ig_post.py`**:
        - **`extract_ig_story.py`**:
        - **`marketing_classification.py`**
    
    

---

**meteorological**: information about the weather in Singapore, together with data collection and cleaning code.
- Contains two subfolders **`code_solutions`** and **`datasets`**:
    -**`code_solutions`**
        - **`clean_and_merge_psi.py`**
        - **`generate_synthetic_weather_data_2025`**
        - **`get_4_day_forecast.py`**
        - **`get_5_min_rainfall.py`**
        - **`get_24_hr_daily_forecast.py`**
        - get_avg
    -**`datasets**`
        -**final_data**
        -**raw_data**
**survey_responses**: survey responses obtained from our survey  
**tripadvisor_reviews**: reviews on USS scraped from TripAdvisor  
**uss_attraction_details**: details on entities in USS  
**uss_ride_wait_times**
**uss_wait_times**: wait times for rides in USS scraped from Thrill Data  