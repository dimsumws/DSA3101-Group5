# Data Description
The data represents the Dates of Public and School Holidays from 2020 to 2025 for Public Holidays, and School Holidays from 2016 to 2025. Keep in mind that School Holidays Data also include Public Holidays on top of Schools' Term Breaks as students also enjoy time off school during Public Holidays as well. 
The date is kept in the folder **datasets** and the **code_solutions** folder contains the scraper python scripts.

## Public Holidays
**final_merged_PH_2020_2025.csv** contains Public Holiday data combined into ONE csv file from 2020 to 2025.

## School Holidays
**school_holidays_combined.csv** contains School Holiday Breaks, together with Public Holidays from 2019 to 2025 for students in Kindergarten to JC/MI levels. Essentially it contains all days in which students do not need to go to school at all (important to keep in mind students can get days off for events such as "Children's Day', Holiday In-Lieu if the Public Holiday fell on a weekend and etc.)

**daily_school_holidays_combined_updated.csv** is a csv file containing for each day from 2016 to 2025 in a DD/MM/YYYY format, it will have a Flag (1 for Being a school/public holiday for students and 0 otherwise). It has a third column which states which holiday that specific date is if it does have a "1" flag. Do note that *daily_school_holidays_combined.csv* is an intermediate subset of **daily_school_holidays_combined_updated.csv**

**add_2016_to_2018_hols.csv** is a python script to manually add from a nested list of school holidays and append it to the **daily_school_holidays_combined.csv** for the years 2016 to 2018 as they were not provided by the MOE website and hence are not able to be scraped with **scrape_moe_holiday.py**.

## Data Sources
The data for Public Holidays was obtained from Ministry of Manpower (MOM), [SOURCE](https://data.gov.sg/collections/691/view).

All the School Holidays data are from individual websites from MOE and data was scraped from the websites using **scrape_moe_holiday.py**, e.g [2021 School Holidays MOE](https://www.moe.gov.sg/news/press-releases/20200817-school-terms-and-holidays-for-2021).

Additionally, holiday data for 2016 can be found from these sources:
[2016 School Holidays](https://time.sg/school-holidays-2016) 
[2017 School Holidays](https://www.todayonline.com/singapore/moe-announces-2017-school-terms-holidays)
[2018 School Holidays](https://www.google.com/search?q=2018+school+holidays+singapore&rlz=1C1VDKB_enSG975SG975&oq=2018+sc&gs_lcrp=EgZjaHJvbWUqDggAEEUYJxg7GIAEGIoFMg4IABBFGCcYOxiABBiKBTIGCAEQRRhAMgYIAhBFGDkyBwgDEAAYgAQyBwgEEAAYgAQyBggFEEUYPDIGCAYQRRg8MgYIBxBFGDzSAQgzOTI2ajBqN6gCALACAA&sourceid=chrome&ie=UTF-8)