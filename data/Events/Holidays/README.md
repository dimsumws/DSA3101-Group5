## Data Description
The data represents the Dates of Public and School Holidays from 2020 to 2025 for Public Holidays, and School Holidays from 2021 to 2025.

### Public Holidays
**final_merged_PH_2020_2025.csv** contains Public Holiday data combined into ONE csv file from 2020 to 2025.
The data was obtained from Ministry of Manpower (MOM), [SOURCE](https://data.gov.sg/collections/691/view).

### School Holidays
**school_holidays_combined.csv** contains School Holiday Breaks, together with Public Holidays from 2021 to 2025 for students in Kindergarten to JC/MI levels. Essentially it contains all days in which students do not need to go to school at all (important to keep in mind students can get days off for events such as "Children's Day', Holiday In-Lieu if the Public Holiday fell on a weekend and etc.)

**daily_school_holidays_combined.csv** is a csv file containing for each day from 2021 to 2025 in a DD/MM/YYYY format, it will have a Flag (1 for Being a school/public holiday for students and 0 otherwise). It has a third column which states which holiday that specific date is if it does have a "1" flag.

**add_2016_to_2018_hols.csv** is a python script to manually add from a nested list of school holidays and append it to the **daily_school_holidays_combined.csv** for the years 2016 to 2018 as they were not provided by the MOE website and hence are not able to be scraped with **scrape_moe_holiday.py**.

All these data are from individual websites from MOE and data was scraped from the websites using **scrape_moe_holiday.py**, e.g [2021 School Holidays MOE](https://www.moe.gov.sg/news/press-releases/20200817-school-terms-and-holidays-for-2021).